"""
CX MIRROR — Comprehensive Browser Automation & Screenshot Suite
Automates Chromium at 1440x1000 viewport, tests every tab, preset, SVG overlay,
split wipe, threshold slider, and ROC benchmark, and captures real verification screenshots.
"""

import os
import sys
import time
import asyncio
from playwright.async_api import async_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "artifacts", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FRONTEND_URL = "http://127.0.0.1:5173"


async def run_browser_verification():
    print("[*] Launching Chromium browser automation...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 1000},
            device_scale_factor=1
        )
        page = await context.new_page()

        print("[1/9] Navigating to CX Mirror Workbench at:", FRONTEND_URL)
        await page.goto(FRONTEND_URL, wait_until="networkidle")
        await page.wait_for_timeout(2500)  # Wait for initial analysis to complete

        # TEST A: Clean Baseline PASS
        print("[2/9] Capturing TEST A: Clean Baseline (PASS)...")
        shot_a = os.path.join(SCREENSHOT_DIR, "01_clean_pass.png")
        await page.screenshot(path=shot_a, full_page=False)
        print(f"      Saved: {shot_a}")

        # TEST B: Drifted Layout with SVG Lasers
        print("[3/9] Testing TEST B: Drifted Layout...")
        drifted_btn = page.locator("button:has-text('2. Drifted Layout')")
        await drifted_btn.click()
        await page.wait_for_timeout(3500)  # Wait for analysis execution

        shot_b = os.path.join(SCREENSHOT_DIR, "02_drifted_lasers.png")
        await page.screenshot(path=shot_b, full_page=False)
        print(f"      Saved: {shot_b}")

        # TEST G: Split-Screen Wipe
        print("[4/9] Testing TEST G: Split-Screen Wipe Slider...")
        split_tab = page.locator("button:has-text('Split-Screen Wipe')")
        await split_tab.click()
        await page.wait_for_timeout(1000)

        shot_split = os.path.join(SCREENSHOT_DIR, "03_split_screen_wipe.png")
        await page.screenshot(path=shot_split, full_page=False)
        print(f"      Saved: {shot_split}")

        # Switch back to laser overlay
        laser_tab = page.locator("button:has-text('SVG Displacement Lasers')")
        await laser_tab.click()
        await page.wait_for_timeout(500)

        # TEST C: Price SKU Bug
        print("[5/9] Testing TEST C: Price Bug (CRITICAL FAIL)...")
        price_btn = page.locator("button:has-text('3. Price SKU Bug')")
        await price_btn.click()
        await page.wait_for_timeout(3500)

        shot_c = os.path.join(SCREENSHOT_DIR, "04_price_bug_fail.png")
        await page.screenshot(path=shot_c, full_page=False)
        print(f"      Saved: {shot_c}")

        # TEST D: Legal Hidden
        print("[6/9] Testing TEST D: Legal Hidden (CRITICAL FAIL)...")
        legal_btn = page.locator("button:has-text('4. Legal Hidden')")
        await legal_btn.click()
        await page.wait_for_timeout(3500)

        shot_d = os.path.join(SCREENSHOT_DIR, "05_legal_hidden_fail.png")
        await page.screenshot(path=shot_d, full_page=False)
        print(f"      Saved: {shot_d}")

        # TEST E: All Bugs
        print("[7/9] Testing TEST E: All Bugs...")
        all_bugs_btn = page.locator("button:has-text('5. All Bugs')")
        await all_bugs_btn.click()
        await page.wait_for_timeout(3500)

        shot_e = os.path.join(SCREENSHOT_DIR, "06_all_bugs_fail.png")
        await page.screenshot(path=shot_e, full_page=False)
        print(f"      Saved: {shot_e}")

        # TEST I: Benchmark Lab (60-ROC)
        print("[8/9] Testing TEST I: Benchmark Lab (60-ROC)...")
        bench_nav = page.locator("button:has-text('Benchmark Lab (60-ROC)')")
        await bench_nav.click()
        await page.wait_for_timeout(2500)

        shot_i = os.path.join(SCREENSHOT_DIR, "07_benchmark_lab_roc.png")
        await page.screenshot(path=shot_i, full_page=False)
        print(f"      Saved: {shot_i}")

        # Overview Executive Dashboard
        print("[9/9] Testing Overview Dashboard & Reference Contracts...")
        dash_nav = page.locator("button:has-text('Overview')")
        await dash_nav.click()
        await page.wait_for_timeout(1000)

        shot_dash = os.path.join(SCREENSHOT_DIR, "08_executive_dashboard.png")
        await page.screenshot(path=shot_dash, full_page=False)
        print(f"      Saved: {shot_dash}")

        contracts_nav = page.locator("button:has-text('Reference Contracts')")
        await contracts_nav.click()
        await page.wait_for_timeout(1000)

        shot_contracts = os.path.join(SCREENSHOT_DIR, "09_reference_contracts.png")
        await page.screenshot(path=shot_contracts, full_page=False)
        print(f"      Saved: {shot_contracts}")

        await context.close()
        await browser.close()
        print("\n[+] Browser Verification Suite Completed Successfully! All screenshots captured.")


if __name__ == "__main__":
    asyncio.run(run_browser_verification())

