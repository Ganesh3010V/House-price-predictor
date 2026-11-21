"""
generate_data.py
Generates a realistic synthetic dataset of ~5000 rows for House Price Predictor.
Price depends logically on every feature plus random noise.
"""
import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 5000

# ── Feature definitions ────────────────────────────────────────────────────────
locations = ["Indiranagar", "Koramangala", "Whitefield", "HSR Layout",
             "Jayanagar", "Electronic City", "Yelahanka", "Marathahalli"]

street_types = ["Main Road", "Cross Road", "Inner Lane", "Highway Facing"]
furnishings  = ["Unfurnished", "Semi-Furnished", "Fully Furnished"]
prop_types   = ["Apartment", "Independent House", "Villa", "Penthouse"]

# ── Location tier multipliers (premium → budget) ───────────────────────────────
location_mult = {
    "Indiranagar":    1.55,
    "Koramangala":    1.50,
    "HSR Layout":     1.30,
    "Jayanagar":      1.25,
    "Whitefield":     1.20,
    "Marathahalli":   1.10,
    "Electronic City":1.05,
    "Yelahanka":      1.00,
}

street_mult = {
    "Main Road":      1.15,
    "Highway Facing": 1.10,
    "Cross Road":     1.05,
    "Inner Lane":     1.00,
}

furnish_mult = {
    "Fully Furnished": 1.20,
    "Semi-Furnished":  1.08,
    "Unfurnished":     1.00,
}

prop_mult = {
    "Penthouse":        1.60,
    "Villa":            1.45,
    "Independent House":1.20,
    "Apartment":        1.00,
}

# ── Sample raw features ────────────────────────────────────────────────────────
area       = np.random.randint(400, 5001, N)
rooms      = np.random.randint(1, 11, N)
build_year = np.random.randint(1990, 2026, N)
location   = np.random.choice(locations, N)
street     = np.random.choice(street_types, N)
furnish    = np.random.choice(furnishings, N)
prop       = np.random.choice(prop_types, N)
has_pool   = np.random.choice([True, False], N, p=[0.20, 0.80])

# ── Price formula (INR Lakhs) ─────────────────────────────────────────────────
base_price_per_sqft = 4.5   # lakhs per 100 sq ft roughly
price = (area / 100) * base_price_per_sqft

# Apply multipliers
price = price * np.array([location_mult[l] for l in location])
price = price * np.array([street_mult[s]   for s in street])
price = price * np.array([furnish_mult[f]  for f in furnish])
price = price * np.array([prop_mult[p]     for p in prop])

# Rooms bonus (more rooms → higher price)
price = price * (1 + 0.03 * rooms)

# Build year bonus (newer → higher price, older → depreciation)
year_norm = (build_year - 1990) / (2025 - 1990)   # 0 → 1
price = price * (0.85 + 0.30 * year_norm)

# Pool premium
price = price * np.where(has_pool, 1.18, 1.00)

# Random noise ±10%
noise = np.random.uniform(0.90, 1.10, N)
price = price * noise

# Round to 2 decimal places
price = np.round(price, 2)

# ── Assemble DataFrame ─────────────────────────────────────────────────────────
df = pd.DataFrame({
    "Area_SqFt":     area,
    "Rooms":         rooms,
    "Build_Year":    build_year,
    "Location":      location,
    "Street_Type":   street,
    "Furnishing":    furnish,
    "Property_Type": prop,
    "Has_Pool":      has_pool,
    "Price":         price,
})

os.makedirs("data", exist_ok=True)
df.to_csv("data/house_data.csv", index=False)
print(f"✅  Saved {len(df)} rows to data/house_data.csv")
print(df.describe())
print("\nSample rows:")
print(df.head(5))
