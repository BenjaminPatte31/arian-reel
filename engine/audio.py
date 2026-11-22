"""Bande-son originale des Reels Arian Studio (100 % synthétisée, libre de droits).

make_track(duration, cuts, out_wav, seed) écrit un WAV stéréo 44,1 kHz :
- un beat house/lo-fi (kick, clap, charleston, basse, nappe d'accords) à 112 BPM ;
- un « whoosh » avant chaque changement de carte (cuts = instants en secondes) ;
- un petit « tick » à chaque apparition de carte ;
- fondu d'entrée/sortie, crête à -1 dBFS.
La progression d'accords varie avec `seed` pour que chaque Reel sonne un peu différemment.
"""
import numpy as np
import wave

SR = 44100
BPM = 112
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


def make_track(duration, cuts, out_wav, seed=0):
    rng = np.random.default_rng(seed)
    n = int((duration + 0.5) * SR)
    drums = np.zeros(n)
    music = np.zeros(n)
    fx = np.zeros(n)
    prog = PROGRESSIONS[seed % len(PROGRESSIONS)]
    bar = 4 * BEAT
    k, c = kick(), clap(rng)
    b = 0
    while b * bar < duration + bar:
        t0 = b * bar
        name, chord = prog[b % len(prog)]
        _add(music, pad(chord, bar), t0)
        for beat in range(4):
            tb = t0 + beat * BEAT
            _add(drums, k, tb)
            if beat in (1, 3):
                _add(drums, c, tb)
            _add(drums, hat(rng), tb + BEAT / 2)
            _add(drums, hat(rng), tb + BEAT / 4 * 3)
            _add(music, bass(ROOTS[name], BEAT / 2), tb + BEAT / 2)
        b += 1
    for i, ct in enumerate(cuts):
        if ct > 0.3:
            _add(fx, whoosh(rng), max(0, ct - 0.42))
        _add(fx, tick(), ct + 0.08)
    # léger « sidechain » : la musique respire sur le kick
    duck = np.ones(n)
    tt = np.arange(n) / SR
    phase = (tt % BEAT) / BEAT
    duck = 0.55 + 0.45 * np.clip(phase / 0.35, 0, 1)
    mix = drums * 0.65 + music * duck + fx
    m = int(duration * SR)
    mix, fx = mix[:m], fx[:m]
    # fondus
    fi, fo = int(0.04 * SR), int(0.5 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)
    mix[-fo:] *= np.linspace(1, 0, fo)
    # stéréo : charleston et fx un peu élargis
    left = mix + 0.06 * np.roll(fx, 220)
    right = mix + 0.06 * np.roll(fx, -220)
    st = np.stack([left, right], axis=1)
    peak = np.max(np.abs(st)) or 1.0
    st = st / peak * 10 ** (-1 / 20)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return out_wav
