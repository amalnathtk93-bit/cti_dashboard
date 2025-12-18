document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("threat-map");
  if (!container) return;

  let useDemo = false;

  // Toggle buttons (if present)
  const liveBtn = document.getElementById("liveBtn");
  const demoBtn = document.getElementById("demoBtn");

  if (liveBtn && demoBtn) {
    liveBtn.onclick = () => {
      useDemo = false;
      liveBtn.classList.add("active");
      demoBtn.classList.remove("active");
      fetchThreats();
    };
    demoBtn.onclick = () => {
      useDemo = true;
      demoBtn.classList.add("active");
      liveBtn.classList.remove("active");
      fetchThreats();
    };
  }

  container.innerHTML = `<svg id="world-map"></svg>`;

  const width = container.clientWidth;
  const height = 380;

  const svg = d3
    .select("#world-map")
    .attr("width", width)
    .attr("height", height);

  const projection = d3
    .geoMercator()
    .scale(width / 6.2)
    .translate([width / 2, height / 1.45]);

  const path = d3.geoPath().projection(projection);

  // Background
  svg.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "#020617");

  // Draw world
  d3.json("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json")
    .then(world => {
      const countries = topojson.feature(world, world.objects.countries);

      svg.append("g")
        .selectAll("path")
        .data(countries.features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr("fill", "#0b1d3a")
        .attr("stroke", "#1e40af")
        .attr("stroke-width", 0.4)
        .attr("opacity", 0.9);

      svg.append("g").attr("id", "threat-layer");

      fetchThreats();
      setInterval(fetchThreats, 60000);
    });

  function fetchThreats() {
    if (useDemo) {
      updateThreats(demoThreats());
      return;
    }

    fetch("/api/threat-map")
      .then(res => res.json())
      .then(data => {
        if (!data || data.length === 0) {
          data = demoThreats();
        }
        updateThreats(data);
      })
      .catch(() => updateThreats(demoThreats()));
  }

  function riskColor(risk) {
    if (risk === "malicious") return "#ef4444";
    if (risk === "suspicious") return "#f59e0b";
    return "#22c55e";
  }

  function updateThreats(threats) {
    const layer = svg.select("#threat-layer");

    const groups = layer
      .selectAll("g.threat")
      .data(threats, d => d.ip);

    groups.exit().remove();

    const enter = groups.enter()
      .append("g")
      .attr("class", "threat")
      .attr("transform", d => {
        const [x, y] = projection([d.lon, d.lat]);
        return `translate(${x}, ${y})`;
      })
      .on("click", (_, d) => openModal(d));

    // Core dot
    enter.append("circle")
      .attr("r", 4)
      .attr("fill", d => riskColor(d.risk))
      .attr("opacity", 0.95);

    // Pulse ring
    enter.append("circle")
      .attr("r", 4)
      .attr("fill", "none")
      .attr("stroke", d => riskColor(d.risk))
      .attr("stroke-width", 2)
      .attr("opacity", 0.8)
      .call(pulse);

    // Update position
    groups
      .transition()
      .duration(400)
      .attr("transform", d => {
        const [x, y] = projection([d.lon, d.lat]);
        return `translate(${x}, ${y})`;
      });
  }

  function pulse(circle) {
    circle
      .transition()
      .duration(1500)
      .attr("r", 14)
      .attr("opacity", 0)
      .transition()
      .duration(0)
      .attr("r", 4)
      .attr("opacity", 0.8)
      .on("end", () => pulse(circle));
  }

  function openModal(d) {
    const modal = new bootstrap.Modal(document.getElementById("iocModal"));
    document.getElementById("modal-ip").textContent = d.ip;
    document.getElementById("modal-country").textContent = d.country;
    document.getElementById("modal-risk").textContent = d.risk;
    modal.show();
  }

  function demoThreats() {
    return [
      { ip: "45.33.12.1", country: "US", risk: "malicious", lat: 37.77, lon: -122.41 },
      { ip: "103.21.244.1", country: "IN", risk: "suspicious", lat: 28.61, lon: 77.20 },
      { ip: "91.198.174.192", country: "DE", risk: "malicious", lat: 52.52, lon: 13.40 },
      { ip: "203.0.113.45", country: "JP", risk: "harmless", lat: 35.68, lon: 139.76 }
    ];
  }

  window.addEventListener("resize", () => location.reload());
});
