function createChart(ctxId, label) {
    return new Chart(document.getElementById(ctxId), {
        type: 'line',
        data: { datasets: [{ label: label, pointRadius: 2 }] },
        options: {
            maintainAspectRatio: false,
            scales: {
                x: { type: 'linear' },
                y: {}
            }
        }
    });
}

const chart1 = createChart("tempxalt", "Temperature x Altitude");
const chart2 = createChart("relhumxalt", "Relative Humidity x Altitude");
const chart3 = createChart("pressxalt", "Pressure x Altitude");

function resetCharts() {
    for (const c of [chart1, chart2, chart3]) {
        c.data.datasets[0].data = [];
        c.update();
    }
}

let evtSource = null;

function connectStream() {
    evtSource = new EventSource("/stream");
    evtSource.onmessage = (event) => {
        if (event.data == "done") {
            evtSource.close();
            document.querySelector(".altitude-charts").style.display = "none";
            document.getElementById("uptime-section").style.display = "none";
            document.getElementById("idle-state").style.display = "flex";
            return;
        }

        document.getElementById("idle-state").style.display = "none";
        document.getElementById("uptime-section").style.display = "block";
        document.querySelector(".altitude-charts").style.display = "grid";

        const mdata = JSON.parse(event.data);
        const alt = mdata.altitude_m;

        document.getElementById("uptime").textContent = mdata.uptime_s;

        chart1.data.datasets[0].data.push({ x: mdata.temp_pressure_c, y: alt });
        chart2.data.datasets[0].data.push({ x: mdata.humidity_pct, y: alt });
        chart3.data.datasets[0].data.push({ x: mdata.pressure_mb, y: alt });

        chart1.update();
        chart2.update();
        chart3.update();
    };
}

async function startFlight() {
    resetCharts();
    await fetch("/api/flights/start", { method: "POST" });
    if (!evtSource || evtSource.readyState === 2) connectStream();
}

async function stopFlight() {
    await fetch("/api/flights/stop", { method: "POST" });
}

document.querySelector(".altitude-charts").style.display = "none";
connectStream();

// start/stop controls only appear on a field laptop, never on the cloud site
fetch("/api/config")
    .then(r => r.json())
    .then(cfg => {
        if (cfg.mode === "field") {
            document.getElementById("controls").style.display = "block";
        }
    });
