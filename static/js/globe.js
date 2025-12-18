document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("globe-container");
  if (!container) return;

  // Create canvas
  container.innerHTML = `<canvas id="globe-canvas"></canvas>`;
  const canvas = document.getElementById("globe-canvas");
  const ctx = canvas.getContext("2d");

  function resize() {
    canvas.width = container.clientWidth;
    canvas.height = 420;
  }

  resize();
  window.addEventListener("resize", resize);

  let rotation = 0;

  function drawGlobe() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const r = Math.min(cx, cy) - 20;

    /* === Outer glow === */
    const glow = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r * 1.1);
    glow.addColorStop(0, "rgba(59,130,246,0.35)");
    glow.addColorStop(1, "rgba(0,0,0,0)");

    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(cx, cy, r * 1.1, 0, Math.PI * 2);
    ctx.fill();

    /* === Globe body === */
    const body = ctx.createRadialGradient(cx - r * 0.3, cy - r * 0.3, r * 0.2, cx, cy, r);
    body.addColorStop(0, "#0b3b7a");
    body.addColorStop(1, "#020617");

    ctx.fillStyle = body;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();

    /* === Outline === */
    ctx.strokeStyle = "rgba(59,130,246,0.6)";
    ctx.lineWidth = 2;
    ctx.stroke();

    /* === Latitude lines === */
    ctx.strokeStyle = "rgba(59,130,246,0.25)";
    ctx.lineWidth = 1;

    for (let i = -60; i <= 60; i += 30) {
      ctx.beginPath();
      ctx.ellipse(
        cx,
        cy,
        r,
        r * Math.cos((i * Math.PI) / 180),
        0,
        0,
        Math.PI * 2
      );
      ctx.stroke();
    }

    /* === Longitude lines (rotating) === */
    for (let i = 0; i < 6; i++) {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate(rotation + (i * Math.PI) / 3);
      ctx.beginPath();
      ctx.ellipse(0, 0, r, r * 0.3, 0, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }

    rotation += 0.002;
    requestAnimationFrame(drawGlobe);
  }

  drawGlobe();
});
