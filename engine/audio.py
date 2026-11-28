"""Bande-son originale des Reels Arian Studio (100 % synthétisée, libre de droits).

make_track(duration, cuts, out_wav, seed) écrit un WAV stéréo 44,1 kHz :
- un beat « Reel » énergique à 126 BPM : kick 4 temps, clap + caisse sur 2 et 4,
  charleston en doubles croches avec accents, basse 808, nappe et mélodie « pluck » qui reste en tête ;
- un impact (boom + crash) à 0 s pour que la 1re phrase tombe sur un temps fort ;
- un « whoosh » montant avant chaque changement de carte et un impact à chaque carte ;
- un « drop » : un demi-temps de silence juste avant la carte finale, puis impact ;
- saturation douce, crête à -1 dBFS.
La progression d'accords varie avec `seed` pour que chaque Reel sonne un peu différemment.
"""
import numpy as np
import wave

SR = 44100
BPM = 126
BEAT = 60 / BPM

PROGRESSIONS = [  # fondamentales en Hz (basse) + accords (fréquences)
    [("A", [220.0, 261.63, 329.63]), ("F", [174.61, 220.0, 261.63]), ("C", [196.0, 261.63, 329.63]), ("G", [196.0, 246.94, 293.66])],
    [("D", [146.83, 174.61, 220.0]), ("Bb", [174.61, 233.08, 293.66]), ("F", [174.61, 220.0, 261.63]), ("C", [196.0, 261.63, 329.63])],
    [("E", [164.81, 196.0, 246.94]), ("C", [196.0, 261.63, 329.63]), ("G", [196.0, 246.94, 293.66]), ("D", [185.0, 220.0, 293.66])],
]
ROOTS = {"A": 55.0, "F": 43.65, "C": 65.41, "G": 49.0, "D": 73.42, "Bb": 58.27, "E": 41.2}


def _lp(x, cutoff):
    from scipy.signal import butter, lfilter
    b, a = butter(2, min(cutoff / (SR / 2), 0.99), "low")
    return lfilter(b, a, x)


def _hp(x, cutoff):
    from scipy.signal import butter, lfilter
    b, a = butter(2, cutoff / (SR / 2), "high")
    return lfilter(b, a, x)


def _env(n, attack, decay):
    t = np.arange(n) / SR
    e = np.minimum(t / max(attack, 1e-4), 1.0) * np.exp(-t / decay)
    return e


def _add(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * _env(n, 0.002, 0.12) * 0.9


def clap(rng):
    n = int(0.22 * SR)
    x = _lp(_hp(rng.standard_normal(n), 900), 5000) * _env(n, 0.001, 0.05)
    return x * 0.3


def hat(rng, open_=False):
    n = int((0.12 if open_ else 0.04) * SR)
    x = _lp(_hp(rng.standard_normal(n), 7000), 12000) * _env(n, 0.001, 0.05 if open_ else 0.012)
    return x * 0.12


def bass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * 2 * freq * t)
    return x * _env(n, 0.005, dur * 0.6) * 0.32


def pad(freqs, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.004):
            ff = f * (1 + det)
            x += 2 * ((t * ff) % 1.0) - 1  # dent de scie
    x = _lp(x, 2200) / (len(freqs) * 3)
    e = np.minimum(t / 0.25, 1.0) * np.minimum((dur - t) / 0.3, 1.0)
    return x * np.clip(e, 0, 1) * 0.24


def whoosh(rng, dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # balayage passe-bande montant : on mélange deux passe-bas en fondu
    lo, hi = _lp(x, 600), _lp(x, 6000)
    k = (t / dur) ** 2
    y = _hp(lo * (1 - k) + hi * k, 200)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2 * (t / dur)
    return y * e * 0.35


def tick():
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * _env(n, 0.0005, 0.012) * 0.12




def sub808(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 1.5 * np.exp(-t * 40))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(2.2 * np.sin(ph))
    return x * _env(n, 0.003, dur * 0.7) * 0.42


def snare(rng):
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 190 * t) * _env(n, 0.001, 0.04)
    noise = _hp(rng.standard_normal(n), 1500) * _env(n, 0.001, 0.07)
    return (tone * 0.5 + noise * 0.35) * 0.6


def pluck(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = sum(2 * ((t * freq * (1 + d)) % 1.0) - 1 for d in (-0.006, 0.0, 0.006)) / 3
    # filtre qui se ferme vite = attaque brillante puis son rond
    bright, dark = _lp(x, 5200), _lp(x, 900)
    k = np.exp(-t * 18)
    y = bright * k + dark * (1 - k)
    return y * _env(n, 0.002, 0.16) * 0.26


def crash(rng, dur=1.2):
    n = int(dur * SR)
    return _hp(rng.standard_normal(n), 5000) * _env(n, 0.001, 0.25) * 0.07


def impact(rng):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 38 + 120 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.001, 0.32)
    return boom * 0.9 + crash(rng, 0.9)[:n]


# motifs de la mélodie (indice dans l'accord, -1 = silence), en doubles croches sur une mesure
HOOKS = [
    [0, -1, 2, -1, 1, -1, 2, 0, -1, 2, -1, 1, 2, -1, 1, -1],
    [2, -1, 1, 0, -1, 0, 2, -1, 1, -1, 2, -1, 0, 1, -1, 2],
    [0, 1, -1, 2, -1, 2, 1, -1, 0, -1, 2, 1, -1, 2, -1, -1],
]

def make_track(duration, cuts, out_wav, seed=0):
    rng = np.random.default_rng(seed)
    n = int((duration + 1.5) * SR)
    drums = np.zeros(n); music = np.zeros(n); fx = np.zeros(n)
    prog = PROGRESSIONS[seed % len(PROGRESSIONS)]
    hook = HOOKS[seed % len(HOOKS)]
    bar = 4 * BEAT; s16 = BEAT / 4
    k, cl, sn = kick(), clap(rng), snare(rng)
    b = 0
    while b * bar < duration + bar:
        t0 = b * bar
        name, chord = prog[b % len(prog)]
        _add(music, pad(chord, bar) * 0.7, t0)
        _add(music, sub808(ROOTS[name], bar * 0.95), t0)
        for st in range(16):
            ts = t0 + st * s16
            if st % 4 == 0:
                _add(drums, k, ts)
            if st in (4, 12):
                _add(drums, cl, ts); _add(drums, sn, ts)
            acc = 1.0 if st % 2 == 0 else 0.55
            _add(drums, hat(rng, open_=(st % 4 == 2)) * acc, ts)
            if hook[st] >= 0:
                _add(music, pluck(chord[hook[st]] * 2, s16 * 2.2), ts)
        b += 1
    _add(fx, impact(rng) * 0.7, 0.0)
    last = cuts[-1] if cuts else None
    for ct in cuts:
        if ct > 0.3:
            _add(fx, whoosh(rng, 0.55) * 0.45, max(0, ct - 0.52))
            _add(fx, impact(rng) * (0.6 if ct == last else 0.28), ct)
    tt = np.arange(n) / SR
    phase = (tt % BEAT) / BEAT
    duck = 0.65 + 0.35 * np.clip(phase / 0.3, 0, 1)
    beat_bus = drums * 0.75 + music * duck
    # drop : demi-temps de silence (sauf le whoosh) juste avant la carte finale
    if last and last > 1.0:
        i0, i1 = int((last - BEAT / 2) * SR), int(last * SR)
        beat_bus[i0:i1] *= np.linspace(1, 0, i1 - i0) ** 4
    mix = beat_bus + fx
    m = int(duration * SR)
    mix, fx = mix[:m], fx[:m]
    fo = int(0.45 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix / (np.max(np.abs(mix)) or 1) * 1.8)  # saturation douce = plus de punch
    left = mix + 0.05 * np.roll(fx, 260)
    right = mix + 0.05 * np.roll(fx, -260)
    st = np.stack([left, right], axis=1)
    st = st / (np.max(np.abs(st)) or 1.0) * 10 ** (-1 / 20)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out_wav
