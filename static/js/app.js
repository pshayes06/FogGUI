function createChart(ctxId, label) {
    return new Chart(document.getElementById(ctxId), {
       type: 'line',
        data: {
            datasets: [{
                label: label,
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear'
                }
            }
        }
    });
}

const chart1 = createChart("tempxalt", "Temperature x Altitude");
const chart2 = createChart("relhumxalt", "Relative Humidity x Altitude");
const chart3 = createChart("pressxalt", "Pressure x Altitude");

const evtSource = new EventSource("/stream")
evtSource.onmessage = (event) => {
    if (event.data == "done") {
        evtSource.close();
        return;
    }
    const mdata = JSON.parse(event.data)
    const alt = mdata.altitude_m; 
    const mtemp = mdata.temp_pressure_c;
    const mhum = mdata.humidity_pct;
    const mpress = mdata.pressure_mb;

    document.getElementById("uptime").textContent = mdata.uptime_s;

    chart1.data.datasets[0].data.push({x: mtemp, y: alt});
    chart2.data.datasets[0].data.push({x: mhum, y: alt});
    chart3.data.datasets[0].data.push({x: mpress, y: alt});

    chart1.update();
    chart2.update();
    chart3.update();
};
