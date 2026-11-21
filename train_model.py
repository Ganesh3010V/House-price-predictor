"""
train_model.py
Trains a RandomForestRegressor pipeline and saves the model + report assets.
"""
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ── Directories ───────────────────────────────────────────────────────────────
os.makedirs("model", exist_ok=True)
os.makedirs("report_assets", exist_ok=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv("data/house_data.csv")
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# Has_Pool → 0/1
df["Has_Pool"] = df["Has_Pool"].map({True: 1, False: 0,
                                     "True": 1, "False": 0}).astype(int)

# ── Features / target ─────────────────────────────────────────────────────────
CAT_COLS = ["Location", "Street_Type", "Furnishing", "Property_Type"]
NUM_COLS = ["Area_SqFt", "Rooms", "Build_Year", "Has_Pool"]
FEATURE_ORDER = NUM_COLS + CAT_COLS   # must match app.py

X = df[FEATURE_ORDER]
y = df["Price"]

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42)
print(f"Train: {len(X_train)}  |  Test: {len(X_test)}")

# ── Pipeline ──────────────────────────────────────────────────────────────────
preprocessor = ColumnTransformer(transformers=[
    ("ohe", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
    ("num", "passthrough", NUM_COLS),
])

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("model", RandomForestRegressor(
        n_estimators=200, random_state=42, n_jobs=-1)),
])

pipeline.fit(X_train, y_train)
print("✅  Model trained.")

# ── Evaluate ──────────────────────────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print(f"\n── Test-set metrics ──────────────────")
print(f"  MAE  : {mae:.2f} Lakhs")
print(f"  RMSE : {rmse:.2f} Lakhs")
print(f"  R²   : {r2:.4f}")

# ── Save model ────────────────────────────────────────────────────────────────
joblib.dump(pipeline, "model/house_model.pkl")
print("\n✅  Saved model/house_model.pkl")

# ── metrics.txt ──────────────────────────────────────────────────────────────
metrics_text = f"""House Price Predictor — Model Metrics
======================================
Dataset size  : {df.shape[0]} rows
Train size    : {len(X_train)}
Test size     : {len(X_test)}

MAE  : {mae:.4f} Lakhs
RMSE : {rmse:.4f} Lakhs
R²   : {r2:.4f}

Feature columns (order used in training):
  Numeric : {NUM_COLS}
  Categorical : {CAT_COLS}
"""
with open("report_assets/metrics.txt", "w") as f:
    f.write(metrics_text)
print("✅  Saved report_assets/metrics.txt")

# ── Feature importance plot ───────────────────────────────────────────────────
ohe = pipeline.named_steps["preprocessor"].named_transformers_["ohe"]
ohe_names = ohe.get_feature_names_out(CAT_COLS).tolist()
all_feature_names = ohe_names + NUM_COLS

importances = pipeline.named_steps["model"].feature_importances_
indices = np.argsort(importances)[::-1][:15]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh([all_feature_names[i] for i in indices[::-1]],
        importances[indices[::-1]], color="#4f8ef7")
ax.set_xlabel("Importance")
ax.set_title("Top 15 Feature Importances — House Price Predictor")
ax.invert_yaxis()
plt.tight_layout()
fig.savefig("report_assets/feature_importance.png", dpi=120)
plt.close(fig)
print("✅  Saved report_assets/feature_importance.png")

# ── Actual vs Predicted plot ──────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(y_test, y_pred, alpha=0.3, s=15, color="#4f8ef7", label="Predictions")
lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
ax.plot(lims, lims, "r--", linewidth=1.5, label="Perfect prediction")
ax.set_xlabel("Actual Price (Lakhs)")
ax.set_ylabel("Predicted Price (Lakhs)")
ax.set_title("Actual vs Predicted House Prices")
ax.legend()
plt.tight_layout()
fig.savefig("report_assets/actual_vs_predicted.png", dpi=120)
plt.close(fig)
print("✅  Saved report_assets/actual_vs_predicted.png")

print("\n🎉  Training complete!")
