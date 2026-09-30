"""Render the built site with Playwright: screenshots at desktop and phone, read-as presets, print-to-PDF.
Usage: python3 scripts/verify.py  (after npm run build). Output in verify-out/.
"""
import asyncio, subprocess, sys, time, os, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUT = ROOT / "verify-out"
OUT.mkdir(exist_ok=True)
PORT = 8771

async def main():
    server = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"], cwd=DIST, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    errors = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
            page = await ctx.new_page()
            page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
            page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
            await page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
            await page.screenshot(path=str(OUT / "desktop-top.png"))
            await page.screenshot(path=str(OUT / "desktop-full.png"), full_page=True)
            # scroll to the middle to exercise the spine parallax, then shoot the viewport
            await page.evaluate("document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0, document.documentElement.scrollHeight * 0.45)")
            await page.wait_for_timeout(600)
            await page.screenshot(path=str(OUT / "desktop-mid.png"))
            # read-as presets
            for q in ("home", "source", "quick"):
                await page.goto(f"http://127.0.0.1:{PORT}/#q={q}", wait_until="networkidle")
                await page.wait_for_timeout(200)
                cls = await page.evaluate("document.body.className")
                summ = await page.evaluate("document.getElementById('copy-summary').textContent")
                print(f"read-as {q}: body='{cls}' | {summ}")
                await page.screenshot(path=str(OUT / f"desktop-q-{q}.png"), full_page=True)
            # live toggle (the API is unreachable from this sandbox, so the fallback path is exercised)
            await page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
            await page.click('#fig1 .tog[data-mode="live"]')
            await page.wait_for_timeout(300)
            print("fig1 live title:", await page.evaluate("document.getElementById('fig1-title').textContent"))
            await page.click('#fig1 .tog[data-region="gb"]')
            await page.wait_for_timeout(200)
            print("fig1 gb title:", await page.evaluate("document.getElementById('fig1-title').textContent"))
            # print to PDF (emulates the print stylesheet)
            await page.goto(f"http://127.0.0.1:{PORT}/#q=all", wait_until="networkidle")
            await page.emulate_media(media="print")
            await page.pdf(path=str(OUT / "notebook-all.pdf"), format="A4", print_background=True)
            await page.goto(f"http://127.0.0.1:{PORT}/#q=home", wait_until="networkidle")
            await page.wait_for_timeout(200)
            await page.emulate_media(media="print")
            await page.pdf(path=str(OUT / "notebook-home.pdf"), format="A4", print_background=True)
            await ctx.close()
            ctx = await browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
            page = await ctx.new_page()
            page.on("pageerror", lambda e: errors.append(f"pageerror(phone): {e}"))
            await page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
            await page.screenshot(path=str(OUT / "phone-top.png"))
            await page.screenshot(path=str(OUT / "phone-full.png"), full_page=True)
            ov = await page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            print("phone horizontal overflow px:", ov)
            await ctx.close()
            await browser.close()
    finally:
        server.terminate()
    print("errors:", errors if errors else "none")

asyncio.run(main())
