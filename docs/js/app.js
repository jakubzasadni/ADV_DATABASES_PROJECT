let allEvents = [];
let stats = {};
let map, markersLayer;

async function loadData() {
  const [evResp, stResp, metaResp] = await Promise.all([
    fetch("data/earthquakes.json"),
    fetch("data/stats.json"),
    fetch("data/meta.json"),
  ]);
  allEvents = await evResp.json();
  stats = await stResp.json();
  const meta = await metaResp.json();

  document.getElementById("meta-info").textContent =
    "Last updated: " + new Date(meta.exported_at).toLocaleString();

  updateSummary(stats.summary);
  renderCharts(stats);
  applyFilters();
}

function updateSummary(s) {
  document.getElementById("s-total").textContent   = s.total?.toLocaleString() ?? "–";
  document.getElementById("s-avg").textContent     = s.avg_mag != null ? s.avg_mag.toFixed(2) : "–";
  document.getElementById("s-max").textContent     = s.max_mag?.toFixed(1) ?? "–";
  document.getElementById("s-tsunami").textContent = s.tsunami_count?.toLocaleString() ?? "–";
}

// ── Map ──────────────────────────────────────────────────────────────────────
function initMap() {
  map = L.map("map", { center: [20, 0], zoom: 2 });
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
    maxZoom: 18,
  }).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
}

function magColor(mag) {
  if (mag == null) return "#94a3b8";
  if (mag >= 7)    return "#ef4444";
  if (mag >= 5)    return "#f97316";
  if (mag >= 3)    return "#eab308";
  return "#22c55e";
}

function alertColor(alert) {
  if (alert === "red")    return "#ef4444";
  if (alert === "orange") return "#f97316";
  if (alert === "yellow") return "#eab308";
  if (alert === "green")  return "#22c55e";
  return "#94a3b8";
}

function renderMap(events) {
  markersLayer.clearLayers();
  const hasAlertFilter = document.getElementById("f-alert").value !== "";
  const subset = events.slice(0, 2000);
  subset.forEach(e => {
    if (e.latitude == null || e.longitude == null) return;
    const r = Math.max(3, Math.min(18, (e.magnitude ?? 1) * 2.5));
    const color = hasAlertFilter ? alertColor(e.alert) : magColor(e.magnitude);
    L.circleMarker([e.latitude, e.longitude], {
      radius: r,
      color: color,
      fillColor: color,
      fillOpacity: 0.6,
      weight: 1,
    })
      .bindPopup(`
        <b>${e.place ?? "Unknown"}</b><br/>
        Magnitude: ${e.magnitude ?? "–"} ${e.mag_type ?? ""}<br/>
        Depth: ${e.depth?.toFixed(1) ?? "–"} km<br/>
        Time: ${new Date(e.time).toUTCString()}<br/>
        ${e.tsunami ? "<span style='color:#f97316'>⚠ Tsunami warning</span>" : ""}
      `)
      .addTo(markersLayer);
  });
}

// ── Charts ───────────────────────────────────────────────────────────────────
function renderCharts(s) {
  // Timeline
  Plotly.newPlot("chart-timeline", [{
    x: s.daily_counts.map(d => d.day),
    y: s.daily_counts.map(d => d.count),
    type: "bar",
    marker: { color: "#3b82f6" },
    name: "Events/day",
  }], {
    title: { text: "Daily Earthquake Count (last 90 days)", font: { color: "#e2e8f0" } },
    paper_bgcolor: "#1a1d27", plot_bgcolor: "#1a1d27",
    font: { color: "#94a3b8" },
    xaxis: { gridcolor: "#2d3148" },
    yaxis: { gridcolor: "#2d3148" },
    margin: { t: 45, r: 20, b: 40, l: 50 },
  }, { responsive: true });

  // Magnitude distribution
  Plotly.newPlot("chart-magnitude", [{
    x: s.magnitude_distribution.map(d => `M${d.bucket}–${d.bucket + 1}`),
    y: s.magnitude_distribution.map(d => d.count),
    type: "bar",
    marker: { color: "#f97316" },
    name: "Count",
  }], {
    title: { text: "Magnitude Distribution (last 365 days)", font: { color: "#e2e8f0" } },
    paper_bgcolor: "#1a1d27", plot_bgcolor: "#1a1d27",
    font: { color: "#94a3b8" },
    xaxis: { gridcolor: "#2d3148" },
    yaxis: { gridcolor: "#2d3148" },
    margin: { t: 45, r: 20, b: 40, l: 50 },
  }, { responsive: true });
}

// ── Filters ──────────────────────────────────────────────────────────────────
function getFilters() {
  return {
    dateFrom: document.getElementById("f-date-from").value,
    dateTo:   document.getElementById("f-date-to").value,
    magMin:   parseFloat(document.getElementById("f-mag-min").value) || 0,
    magMax:   parseFloat(document.getElementById("f-mag-max").value) || 10,
    depth:    parseFloat(document.getElementById("f-depth").value)   || Infinity,
    alert:    document.getElementById("f-alert").value,
    tsunami:  document.getElementById("f-tsunami").value,
    place:    document.getElementById("f-place").value.toLowerCase(),
  };
}

function matchesFilter(e, f) {
  const t = new Date(e.time);
  if (f.dateFrom && t < new Date(f.dateFrom)) return false;
  if (f.dateTo   && t > new Date(f.dateTo + "T23:59:59Z")) return false;
  if (e.magnitude != null) {
    if (e.magnitude < f.magMin || e.magnitude > f.magMax) return false;
  }
  if (e.depth != null && e.depth > f.depth) return false;
  if (f.alert && e.alert !== f.alert) return false;
  if (f.tsunami === "true"  && !e.tsunami)  return false;
  if (f.tsunami === "false" && e.tsunami)   return false;
  if (f.place && !(e.place ?? "").toLowerCase().includes(f.place)) return false;
  return true;
}

function applyFilters() {
  const f = getFilters();
  const filtered = allEvents.filter(e => matchesFilter(e, f));
  renderMap(filtered);
  renderTable(filtered.slice(0, 200));
}

function resetFilters() {
  ["f-date-from","f-date-to","f-mag-min","f-mag-max","f-depth","f-place"].forEach(id => {
    document.getElementById(id).value = "";
  });
  document.getElementById("f-alert").value = "";
  document.getElementById("f-tsunami").value = "";
  applyFilters();
}

// ── Table ────────────────────────────────────────────────────────────────────
function renderTable(events) {
  document.getElementById("table-count").textContent = `(${events.length} shown)`;
  const tbody = document.getElementById("table-body");
  tbody.innerHTML = events.map(e => `
    <tr>
      <td>${new Date(e.time).toISOString().replace("T"," ").slice(0,19)}</td>
      <td>${e.place ?? "–"}</td>
      <td><b>${e.magnitude?.toFixed(1) ?? "–"}</b> ${e.mag_type ?? ""}</td>
      <td>${e.depth?.toFixed(1) ?? "–"}</td>
      <td class="alert-${e.alert ?? ""}">${e.alert ?? "–"}</td>
      <td>${e.tsunami ? "⚠ Yes" : "No"}</td>
    </tr>
  `).join("");
}

// ── Init ─────────────────────────────────────────────────────────────────────
document.getElementById("btn-apply").addEventListener("click", applyFilters);
document.getElementById("btn-reset").addEventListener("click", resetFilters);

initMap();
loadData().catch(err => console.error("Failed to load data:", err));
