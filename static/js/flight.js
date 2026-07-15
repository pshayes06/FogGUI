const flightId = window.location.pathname.split("/").pop();
let allReadings = [];
let readonly = false;

function createChart(ctxId, label) {
    return new Chart(document.getElementById(ctxId), {
        type: "line",
        data: { datasets: [{ label: label, pointRadius: 2 }] },
        options: {
            animation: false,
            maintainAspectRatio: false,
            scales: {
                x: { type: "linear" },
                y: {}
            }
        }
    });
}

const chart1 = createChart("detail-temp", "Temperature x Altitude");
const chart2 = createChart("detail-hum", "Relative Humidity x Altitude");
const chart3 = createChart("detail-press", "Pressure x Altitude");

function renderCharts(readings) {
    chart1.data.datasets[0].data = readings.map(r => ({ x: r.temperature_c, y: r.altitude_m }));
    chart2.data.datasets[0].data = readings.map(r => ({ x: r.humidity_pct, y: r.altitude_m }));
    chart3.data.datasets[0].data = readings.map(r => ({ x: r.pressure_mb, y: r.altitude_m }));
    chart1.update();
    chart2.update();
    chart3.update();
}

async function loadCharts() {
    const minAlt = document.getElementById("minAlt").value;
    const maxAlt = document.getElementById("maxAlt").value;

    let url = `/api/flights/${flightId}/readings`;
    const params = new URLSearchParams();
    if (minAlt) params.append("min_alt", minAlt);
    if (maxAlt) params.append("max_alt", maxAlt);
    if (params.toString()) url += "?" + params.toString();

    const res = await fetch(url);
    allReadings = await res.json();

    const scrubber = document.getElementById("scrubber");
    const maxUptime = allReadings.reduce((max, r) => r.uptime_s > max ? r.uptime_s : max, 0);
    scrubber.max = maxUptime;
    scrubber.value = 0;
    document.getElementById("scrubberLabel").textContent = `Time: 0s`;

    renderCharts([]);
}

document.getElementById("scrubber").addEventListener("input", function() {
    const t = parseFloat(this.value);
    document.getElementById("scrubberLabel").textContent = `Time: ${t.toFixed(1)}s`;
    const filtered = allReadings.filter(r => r.uptime_s <= t);
    renderCharts(filtered);
});

async function loadFlight() {
    const res = await fetch(`/api/flights/${flightId}`);
    const flight = await res.json();
    document.getElementById("flightLabel").textContent = flight.label || "Flight";
}

async function saveLabel() {
    if (readonly) return alert("This is a read-only demo. Renaming is disabled here.");
    const label = document.getElementById("editLabel").value.trim();
    if (!label) return;
    await fetch(`/api/flights/${flightId}/label`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label })
    });
    document.getElementById("flightLabel").textContent = label;
    document.getElementById("editLabel").value = "";
}

fetch("/api/config").then(r => r.json()).then(cfg => { readonly = cfg.readonly; });
loadFlight();
loadCharts();
