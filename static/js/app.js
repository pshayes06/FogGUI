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

window.onload = () => {
    if (sessionStorage.getItem("chartData")) {
        chart1.data.datasets[0].data = JSON.parse(sessionStorage.getItem("chartData"));
        console.log(JSON.parse(sessionStorage.getItem("chartData")))
    }
};

function saveToSession() { // consider switching to localstorage
    sessionStorage.setItem("chartData", JSON.stringify(chart1.data.datasets[0].data));
}

const chart1 = createChart("tempxalt", "Temperature x Altitude");
const chart2 = createChart("relhumxalt", "Relative Humidity x Altitude");
const chart3 = createChart("pressxalt", "Pressure x Altitude");

const evtSource = new EventSource("/stream")
evtSource.onmessage = (event) => {
    const mdata = event.data.split(',');
    const alt = mdata[13]; // may need to apply a conversion
    const mtemp = mdata[21]; //how accessing the 820000 val?
    const mhum = mdata[16];
    const mpress = mdata[5];

    document.getElementById("uptime").textContent = mdata[3];
    document.getElementById("battlife").textContent = mdata[4];

    chart1.data.datasets[0].data.push({x: mtemp, y: alt}); //maybe use colors to indicate time later
    chart2.data.datasets[0].data.push({x: mhum, y: alt});
    chart3.data.datasets[0].data.push({x: mpress, y: alt});

    chart1.update();
    saveToSession() // only for chart1 to test at the moment
    chart2.update();
    chart3.update();
};
