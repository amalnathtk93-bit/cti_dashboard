document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("mapToggleBtn");
  const container = document.getElementById("globe-container");

  if (!btn || !container) return;

  let currentView = "globe"; // default

  function loadGlobe() {
    container.innerHTML = "";
    const script = document.createElement("script");
    script.src = "/static/js/globe.js";
    script.defer = true;
    document.body.appendChild(script);
    btn.textContent = "Switch to Map";
    currentView = "globe";
  }

  function loadMap() {
    container.innerHTML = "";
    const script = document.createElement("script");
    script.src = "/static/js/map.js";
    script.defer = true;
    document.body.appendChild(script);
    btn.textContent = "Switch to Globe";
    currentView = "map";
  }

  btn.addEventListener("click", () => {
    if (currentView === "globe") {
      loadMap();
    } else {
      loadGlobe();
    }
  });
});
