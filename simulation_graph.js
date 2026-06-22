/**
 * simulation_graph.js — KING DIADEM
 * Real-time Decision Stability Graph
 * pulls from /api/galaxy/nodes every 10s
 * tracks: stability, entropy, resource (waterline triad)
 */

(function () {
  const MAX_POINTS = 20;

  // ── รอ canvas พร้อม ────────────────────────────────────────────
  const canvas = document.getElementById("simChart");
  if (!canvas) {
    console.warn("simulation_graph: #simChart not found");
    return;
  }

  // ── Dataset template ───────────────────────────────────────────
  const chartData = {
    labels: [],
    datasets: [
      {
        label: "Stability",
        data: [],
        borderColor: "#4bd4ff",
        backgroundColor: "rgba(75,212,255,0.08)",
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
      },
      {
        label: "Entropy",
        data: [],
        borderColor: "#ff6b6b",
        backgroundColor: "rgba(255,107,107,0.08)",
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
      },
      {
        label: "Resource",
        data: [],
        borderColor: "#c8a84b",
        backgroundColor: "rgba(200,168,75,0.08)",
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5,
      },
    ],
  };

  // ── Chart init ─────────────────────────────────────────────────
  const chart = new Chart(canvas, {
    type: "line",
    data: chartData,
    options: {
      responsive: true,
      animation: { duration: 400 },
      plugins: {
        legend: {
          labels: { color: "#a0b8d0", font: { size: 12 } },
        },
        tooltip: {
          backgroundColor: "#0a0f1e",
          borderColor: "#4a9eff",
          borderWidth: 1,
          titleColor: "#c8a84b",
          bodyColor: "#a0b8d0",
        },
      },
      scales: {
        x: {
          ticks: { color: "#4a6070", maxTicksLimit: 8 },
          grid:  { color: "rgba(74,144,255,0.08)" },
        },
        y: {
          min: 0,
          max: 100,
          ticks: { color: "#4a6070", stepSize: 20 },
          grid:  { color: "rgba(74,144,255,0.08)" },
        },
      },
    },
  });

  // ── Fetch + push ───────────────────────────────────────────────
  async function fetchAndUpdate() {
    try {
      const res = await fetch("/api/galaxy/nodes");
      if (!res.ok) return;
      const json = await res.json();

      const wl = json.waterline || {};
      const stability = typeof wl.stability === "number" ? wl.stability : null;
      const entropy   = typeof wl.entropy   === "number" ? wl.entropy   : null;
      const resource  = typeof wl.resource  === "number" ? wl.resource  : null;

      if (stability === null) return; // ข้อมูลยังไม่พร้อม

      // timestamp label
      const now = new Date();
      const label = `${String(now.getHours()).padStart(2,"0")}:${String(now.getMinutes()).padStart(2,"0")}:${String(now.getSeconds()).padStart(2,"0")}`;

      chartData.labels.push(label);
      chartData.datasets[0].data.push(Math.round(stability));
      chartData.datasets[1].data.push(Math.round(entropy));
      chartData.datasets[2].data.push(Math.round(resource));

      // sliding window
      if (chartData.labels.length > MAX_POINTS) {
        chartData.labels.shift();
        chartData.datasets.forEach(ds => ds.data.shift());
      }

      chart.update();

    } catch (e) {
      // silent fail — ไม่ crash หน้าเว็บ
      console.warn("simulation_graph fetch error:", e);
    }
  }

  // ── Seed ด้วย 1 point ทันที แล้ว poll ──────────────────────────
  fetchAndUpdate();
  setInterval(fetchAndUpdate, 10_000);

})();
