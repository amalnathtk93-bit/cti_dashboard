document.addEventListener("DOMContentLoaded", () => {

  function animateValue(element, start, end, duration) {
    if (!element) return;

    const range = end - start;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const value = Math.floor(start + range * easeOutCubic(progress));
      element.textContent = value;

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = end;
      }
    }

    requestAnimationFrame(update);
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  // ===== GET KPI ELEMENTS =====
  const totalEl = document.getElementById("kpi-total");
  const malEl   = document.getElementById("kpi-mal");
  const goodEl  = document.getElementById("kpi-good");
  const suspEl  = document.getElementById("kpi-susp");

  // ===== DEMO VALUES (SAFE DEFAULTS) =====
  // Later these can come from backend/API
  const values = {
    total: 248,
    malicious: 63,
    harmless: 141,
    suspicious: 44
  };

  // ===== ANIMATE =====
  animateValue(totalEl, 0, values.total, 900);
  animateValue(malEl, 0, values.malicious, 800);
  animateValue(goodEl, 0, values.harmless, 1000);
  animateValue(suspEl, 0, values.suspicious, 850);

});
