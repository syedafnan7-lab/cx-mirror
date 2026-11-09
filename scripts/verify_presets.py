"""
CX MIRROR — Automated Verification Suite
Runs the full verification pipeline on all five presets and records exact measurements.
"""

import os
import sys
import json
import asyncio
import httpx

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VERIF_DIR = os.path.join(PROJECT_ROOT, "artifacts", "verification")
os.makedirs(VERIF_DIR, exist_ok=True)

PRESETS = ["clean", "drifted", "price_bug", "legal_hidden", "all_bugs"]


async def verify_all():
    results = {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        for preset in PRESETS:
            print(f"[*] Verifying preset: {preset}...")
            payload = {
                "target_url": f"http://127.0.0.1:8000/sandbox?preset={preset}",
                "preset": preset,
                "threshold": "95.0"
            }
            res = await client.post("http://127.0.0.1:8000/api/analyze", data=payload)
            if res.status_code != 200:
                print(f"[!] Error on {preset}: {res.status_code} - {res.text}")
                continue

            data = res.json()
            results[preset] = {
                "verdict": data["verdict"],
                "confidence": data["confidence"],
                "threshold": data["threshold"],
                "scores": data["scores"],
                "summary": data["summary"],
                "discrepancies_count": len(data["discrepancies"]),
                "critical_failures": data["summary"]["critical_failures"],
                "execution_time_ms": data["execution_time_ms"],
                "discrepancies": data["discrepancies"]
            }
            print(f"    --> Verdict: {data['verdict']}, Confidence: {data['confidence']}%, Discrepancies: {len(data['discrepancies'])}, Critical: {data['summary']['critical_failures']}")

    out_file = os.path.join(VERIF_DIR, "preset_verification_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] All preset results recorded in: {out_file}")


if __name__ == "__main__":
    asyncio.run(verify_all())

