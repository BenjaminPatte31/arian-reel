"""Moteur de rendu des Reels Arian Studio.

Usage : python3 engine/render.py engine/specs/<fichier>.json [...]
Chaque spec produit reels/<id>.mp4 (1080x1920, 30 fps, H.264 + piste audio muette).
Prérequis : `cd engine && npm install` (polices), playwright (préinstallé), ffmpeg.
"""
import asyncio, base64, json, os, pathlib, shutil, subprocess, sys, urllib.parse
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
FPS = 30
FONTS = [
    ("Bricolage Grotesque", 800, "bricolage-grotesque"), ("Bricolage Grotesque", 700, "bricolage-grotesque"),
    ("Manrope", 800, "manrope"), ("Manrope", 700, "manrope"), ("Manrope", 600, "manrope"),
    ("Montserrat", 800, "montserrat"), ("Montserrat", 700, "montserrat"),
]

def build_fonts():
    out = ROOT / "fonts.css"
    if out.exists():
        return
    css = []
    for fam, w, pkg in FONTS:
        f = ROOT / f"node_modules/@fontsource/{pkg}/files/{pkg}-latin-{w}-normal.woff2"
        b = base64.b64encode(f.read_bytes()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};font-display:block;src:url(data:font/woff2;base64,{b}) format('woff2')}}")
    out.write_text("\n".join(css))

async def render(ctx, spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text())
    for c in spec["cards"]:
        if c.get("type") == "demo":
            c["video"] = "file://" + str((REPO / c["video"]).resolve())
    rid = spec["id"]
    fdir = pathlib.Path(os.environ.get("TMPDIR", "/tmp")) / f"frames-{rid}"
    shutil.rmtree(fdir, ignore_errors=True); fdir.mkdir(parents=True)
    pg = await ctx.new_page()
    q = urllib.parse.quote(urllib.parse.quote(json.dumps(spec, ensure_ascii=False)))
    await pg.goto(f"file://{ROOT}/reel.html?spec={q}", wait_until="load")
    await pg.wait_for_function("document.body.dataset.ready==='1'")
    await pg.evaluate("window.ready")
    await pg.wait_for_timeout(400)
    dur = await pg.evaluate("window.DURATION")
    for i in range(int(dur * FPS)):
        await pg.evaluate(f"window.renderFrame({i / FPS})")
        await pg.screenshot(path=str(fdir / f"f{i:05d}.jpg"), type="jpeg", quality=92)
    await pg.close()
    out = REPO / "reels" / f"{rid}.mp4"
    out.parent.mkdir(exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(fdir / "f%05d.jpg"),
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-crf", "19",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(out)],
                   check=True, capture_output=True)
    shutil.copy(fdir / f"f{int(FPS*1.2):05d}.jpg", REPO / "reels" / f"{rid}-check.jpg")
    shutil.rmtree(fdir, ignore_errors=True)
    print(f"{rid}: {dur:.1f}s -> {out}")

async def main(paths):
    build_fonts()
    async with async_playwright() as p:
        br = await p.chromium.launch(args=["--allow-file-access-from-files", "--force-color-profile=srgb"])
        ctx = await br.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1, locale="fr-FR")
        for sp in paths:
            await render(ctx, sp)
        await br.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
