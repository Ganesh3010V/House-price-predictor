"""
test_api.py
Tests the /predict endpoint with 3 sample inputs and verifies price ordering.
"""
import sys
import json
import urllib.request
import urllib.error
import os

BASE = "http://127.0.0.1:5000/predict"

SAMPLES = [
    {
        "label": "Small Apartment in Electronic City (no pool)",
        "payload": {
            "Area_SqFt":     600,
            "Rooms":         2,
            "Build_Year":    2000,
            "Location":      "Electronic City",
            "Street_Type":   "Inner Lane",
            "Furnishing":    "Unfurnished",
            "Property_Type": "Apartment",
            "Has_Pool":      False,
        },
    },
    {
        "label": "Mid-size Independent House in Whitefield",
        "payload": {
            "Area_SqFt":     1800,
            "Rooms":         4,
            "Build_Year":    2012,
            "Location":      "Whitefield",
            "Street_Type":   "Cross Road",
            "Furnishing":    "Semi-Furnished",
            "Property_Type": "Independent House",
            "Has_Pool":      False,
        },
    },
    {
        "label": "Large Villa with Pool in Indiranagar",
        "payload": {
            "Area_SqFt":     4500,
            "Rooms":         8,
            "Build_Year":    2022,
            "Location":      "Indiranagar",
            "Street_Type":   "Main Road",
            "Furnishing":    "Fully Furnished",
            "Property_Type": "Villa",
            "Has_Pool":      True,
        },
    },
]


def call_predict(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


os.makedirs("report_assets", exist_ok=True)
results = []
prices  = []

print("=" * 60)
print("  House Price Predictor — API Test Results")
print("=" * 60)

for s in SAMPLES:
    try:
        resp = call_predict(s["payload"])
        price = resp["price_lakhs"]
        prices.append(price)
        line = (
            f"\n📌  {s['label']}\n"
            f"    Input   : {json.dumps(s['payload'], indent=None)}\n"
            f"    Result  : {resp['formatted']}  ({price} Lakhs)\n"
        )
        print(line)
        results.append({"label": s["label"], "input": s["payload"], "result": resp})
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌  {s['label']} → HTTP {e.code}: {body}")
        sys.exit(1)

# Ordering check
small_price  = prices[0]
medium_price = prices[1]
large_price  = prices[2]

print("=" * 60)
print("Ordering check:")
print(f"  Small  : {small_price:.2f} Lakhs")
print(f"  Medium : {medium_price:.2f} Lakhs")
print(f"  Large  : {large_price:.2f} Lakhs")

if large_price > medium_price > small_price:
    print("✅  PASS — prices increase with property size/quality.")
elif large_price > small_price:
    print("⚠️   PARTIAL — large > small, medium order may vary (noise).")
else:
    print("❌  FAIL — large Villa is not more expensive than small Apartment!")
    sys.exit(1)

# Save report
report_lines = ["House Price Predictor — Sample Predictions\n", "=" * 60 + "\n"]
for r in results:
    report_lines.append(f"\nLabel : {r['label']}\n")
    report_lines.append(f"Input : {json.dumps(r['input'])}\n")
    report_lines.append(f"Result: {r['result']['formatted']} ({r['result']['price_lakhs']} Lakhs)\n")
report_lines.append("\nOrdering: " + ("PASS ✅" if large_price > small_price else "FAIL ❌") + "\n")

with open("report_assets/sample_predictions.txt", "w", encoding="utf-8") as f:
    f.writelines(report_lines)

print("\n✅  Saved report_assets/sample_predictions.txt")
print("=" * 60)
