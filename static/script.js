/* script.js — House Price Predictor */

(function () {
  "use strict";

  const form       = document.getElementById("predictForm");
  const submitBtn  = document.getElementById("submitBtn");
  const resultCard = document.getElementById("resultCard");
  const resultInner= document.getElementById("resultInner");
  const poolYes    = document.getElementById("pool-yes");
  const poolNo     = document.getElementById("pool-no");
  const poolInput  = document.getElementById("Has_Pool");

  // ── Pool toggle ─────────────────────────────────────────────────────────────
  [poolYes, poolNo].forEach(btn => {
    btn.addEventListener("click", () => {
      poolYes.classList.toggle("active", btn === poolYes);
      poolNo.classList.toggle("active",  btn === poolNo);
      poolInput.value = btn.dataset.value;
    });
  });

  // ── Validation helpers ───────────────────────────────────────────────────────
  function markValid(el)   { el.classList.remove("invalid"); }
  function markInvalid(el) { el.classList.add("invalid"); }

  function validateField(el) {
    const val = el.value.trim();
    if (!val) { markInvalid(el); return false; }
    if (el.type === "number") {
      const num = Number(val);
      const lo  = Number(el.min);
      const hi  = Number(el.max);
      if (isNaN(num) || num < lo || num > hi) { markInvalid(el); return false; }
    }
    markValid(el);
    return true;
  }

  // Clear invalid on change
  form.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("input",  () => markValid(el));
    el.addEventListener("change", () => markValid(el));
  });

  // ── Show result ──────────────────────────────────────────────────────────────
  function showResult(html, type) {
    resultInner.className = type === "success" ? "result-inner success" : "result-inner error-box";
    resultInner.innerHTML = html;
    resultCard.classList.add("show");
  }

  function showLoading() {
    submitBtn.disabled = true;
    submitBtn.classList.add("loading");
  }
  function hideLoading() {
    submitBtn.disabled = false;
    submitBtn.classList.remove("loading");
  }

  // ── Form submit ──────────────────────────────────────────────────────────────
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Validate all fields
    const inputs   = [...form.querySelectorAll("input[required], select[required]")];
    const allValid = inputs.map(validateField).every(Boolean);
    if (!allValid) {
      showResult(
        `<div class="error-msg">⚠️ Please fill in all required fields correctly.</div>`,
        "error"
      );
      resultCard.classList.add("show");
      return;
    }

    // Build payload
    const payload = {
      Area_SqFt:     Number(document.getElementById("Area_SqFt").value),
      Rooms:         Number(document.getElementById("Rooms").value),
      Build_Year:    Number(document.getElementById("Build_Year").value),
      Location:      document.getElementById("Location").value,
      Street_Type:   document.getElementById("Street_Type").value,
      Furnishing:    document.getElementById("Furnishing").value,
      Property_Type: document.getElementById("Property_Type").value,
      Has_Pool:      poolInput.value === "true",
    };

    showLoading();
    // Hide old result
    resultCard.classList.remove("show");

    try {
      const resp = await fetch("/predict", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });

      const data = await resp.json();
      hideLoading();

      if (!resp.ok) {
        showResult(
          `<div class="error-msg">❌ ${data.error || "Prediction failed. Please try again."}</div>`,
          "error"
        );
        return;
      }

      const formatted  = data.formatted;
      const priceLakhs = data.price_lakhs;

      showResult(`
        <div class="result-label">Estimated Price</div>
        <div class="price-display">${formatted}</div>
        <div class="price-sub">≈ ₹${priceLakhs.toFixed(2)} Lakhs&emsp;·&emsp;Random Forest Model</div>
      `, "success");

    } catch (err) {
      hideLoading();
      showResult(
        `<div class="error-msg">🌐 Network error — make sure the server is running.<br>${err.message}</div>`,
        "error"
      );
    }
  });

  // Demo auto-fill helper for screenshots/previews
  if (window.location.search.includes("demo=1")) {
    document.getElementById("Area_SqFt").value = 2400;
    document.getElementById("Rooms").value = 4;
    document.getElementById("Build_Year").value = 2018;
    document.getElementById("Location").value = "Koramangala";
    document.getElementById("Street_Type").value = "Main Road";
    document.getElementById("Furnishing").value = "Semi-Furnished";
    document.getElementById("Property_Type").value = "Independent House";
    setTimeout(() => {
      form.dispatchEvent(new Event("submit"));
    }, 200);
  }
})();
