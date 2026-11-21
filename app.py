"""
app.py — Flask backend for House Price Predictor
"""
import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ── Load model once at startup ────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "house_model.pkl")
pipeline = joblib.load(MODEL_PATH)

# ── Allowed category values ───────────────────────────────────────────────────
ALLOWED = {
    "Location":      ["Indiranagar", "Koramangala", "Whitefield", "HSR Layout",
                      "Jayanagar", "Electronic City", "Yelahanka", "Marathahalli"],
    "Street_Type":   ["Main Road", "Cross Road", "Inner Lane", "Highway Facing"],
    "Furnishing":    ["Unfurnished", "Semi-Furnished", "Fully Furnished"],
    "Property_Type": ["Apartment", "Independent House", "Villa", "Penthouse"],
}

FEATURE_ORDER = ["Area_SqFt", "Rooms", "Build_Year", "Has_Pool",
                 "Location", "Street_Type", "Furnishing", "Property_Type"]


def validate_and_parse(data):
    """Returns (parsed_dict, error_string). error_string is None on success."""
    errors = []

    # Numeric fields
    numeric_fields = {
        "Area_SqFt":  (400, 5000),
        "Rooms":      (1, 10),
        "Build_Year": (1990, 2025),
    }
    parsed = {}
    for field, (lo, hi) in numeric_fields.items():
        val = data.get(field)
        if val is None:
            errors.append(f"'{field}' is required.")
            continue
        try:
            val = float(val)
        except (TypeError, ValueError):
            errors.append(f"'{field}' must be a number.")
            continue
        if not (lo <= val <= hi):
            errors.append(f"'{field}' must be between {lo} and {hi} (got {val}).")
        parsed[field] = val

    # Category fields
    for field, allowed in ALLOWED.items():
        val = data.get(field)
        if val is None:
            errors.append(f"'{field}' is required.")
        elif val not in allowed:
            errors.append(f"'{field}' must be one of {allowed} (got '{val}').")
        else:
            parsed[field] = val

    # Boolean Has_Pool
    pool_val = data.get("Has_Pool")
    if pool_val is None:
        errors.append("'Has_Pool' is required (true or false).")
    else:
        if isinstance(pool_val, bool):
            parsed["Has_Pool"] = int(pool_val)
        elif str(pool_val).strip().lower() in ("true", "1", "yes"):
            parsed["Has_Pool"] = 1
        elif str(pool_val).strip().lower() in ("false", "0", "no"):
            parsed["Has_Pool"] = 0
        else:
            errors.append("'Has_Pool' must be true or false.")

    if errors:
        return None, " | ".join(errors)
    return parsed, None


def format_price(lakhs):
    if lakhs < 100:
        return f"{lakhs:.2f} Lakhs"
    crores = lakhs / 100
    return f"{crores:.2f} Crores"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True, silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    parsed, err = validate_and_parse(data)
    if err:
        return jsonify({"error": err}), 400

    row = pd.DataFrame([{col: parsed[col] for col in FEATURE_ORDER}])
    price = float(pipeline.predict(row)[0])
    price = round(price, 2)

    return jsonify({
        "price_lakhs": price,
        "formatted":   format_price(price),
    })


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
