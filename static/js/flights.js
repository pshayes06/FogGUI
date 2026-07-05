document.getElementById("fileInput").addEventListener("change", function() {
    document.getElementById("fileName").textContent = this.files[0]?.name || "No file chosen";
});

async function loadFlights() {
    const res = await fetch("/api/flights");
    const flights = await res.json();
    const tbody = document.getElementById("flightsList");
    tbody.innerHTML = "";
    for (const flight of flights) {
        const row = document.createElement("tr");
        const date = new Date(flight.started_at).toLocaleString();
        row.innerHTML = `
            <td style="cursor:pointer" onclick="window.location.href='/flights/${flight.id}'">${flight.label || "Flight"}</td>
            <td style="cursor:pointer" onclick="window.location.href='/flights/${flight.id}'">${date}</td>
            <td><button onclick="deleteFlight(${flight.id})">Delete</button></td>`;
        tbody.appendChild(row);
    }
}

async function upload() {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return alert("Choose a file first");

    const label = document.getElementById("label").value;
    const form = new FormData();
    form.append("file", file);
    if (label) form.append("label", label);

    const res = await fetch("/api/flights/upload", { method: "POST", body: form });
    if (res.ok) {
        document.getElementById("label").value = "";
        document.getElementById("fileName").textContent = "No file chosen";
        document.getElementById("fileInput").value = "";
        loadFlights();
    } else {
        alert("Upload failed");
    }
}

async function deleteFlight(id) {
    if (!confirm("Delete this flight?")) return;
    await fetch(`/api/flights/${id}`, { method: "DELETE" });
    loadFlights();
}

loadFlights();
