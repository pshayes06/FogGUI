import json
import os
import queue
import threading
from datetime import datetime

import boto3
from flask import Flask, Response, send_from_directory, jsonify, request, redirect

from foggui.sources import ReplaySource, SerialSource
from foggui.parser import parse_packet
from foggui.db import start_flight, insert_reading, end_flight, get_flights, get_readings, get_flight, delete_flight, update_flight_label, update_s3_key

# "field" = laptop with a sensor (live capture, no DB, writes a log file)
# "cloud" = server (upload/analysis only, no live capture)
FOGGUI_MODE = os.environ.get("FOGGUI_MODE", "cloud")
# "serial" = real sensor; "replay" = replay mockdata.txt for demo/dev
FOGGUI_SOURCE = os.environ.get("FOGGUI_SOURCE", "replay")
S3_BUCKET = os.environ.get("S3_BUCKET")

app = Flask(__name__)
subscribers = []
worker_thread = None
stop_event = threading.Event()

def ingest_worker(flight_id, source, log_path):
    with open(log_path, "w") as logf:
        for line in source.lines():
            if stop_event.is_set():
                break
            logf.write(line.rstrip("\n") + "\n")
            logf.flush()
            reading = parse_packet(line)
            if reading is None:
                continue

            # flight_id is None in field mode: no DB, log file is the record
            if flight_id is not None:
                insert_reading(flight_id, reading)

            for sub in subscribers:
                sub.put(reading)

    if flight_id is not None:
        end_flight(flight_id)
    for sub in subscribers:
        sub.put(None)

# ---- always available ----

@app.route("/api/config")
def api_config():
    return jsonify({"mode": FOGGUI_MODE})

@app.route("/")
def home():
    # field laptop lands on the live page; cloud lands on the analysis pages
    if FOGGUI_MODE == "field":
        return send_from_directory('static', 'index.html')
    return redirect("/flights")

# ---- field mode: live capture ----

if FOGGUI_MODE == "field":

    @app.route("/stream")
    def stream():
        q = queue.Queue()
        subscribers.append(q)
        def eventStream():
            try:
                while True:
                    reading = q.get()
                    if reading is None:
                        yield "data: done\n\n"
                        break
                    data = json.dumps({
                        "altitude_m": reading.altitude_m,
                        "pressure_mb": reading.pressure_mb,
                        "humidity_pct": reading.humidity_pct,
                        "temp_pressure_c": reading.temp_pressure_c,
                        "temp_humidity_c": reading.temp_humidity_c,
                        "uptime_s": reading.uptime_s,
                    })
                    yield f"data: {data}\n\n"
            except GeneratorExit:
                subscribers.remove(q)

        return Response(eventStream(), mimetype="text/event-stream")

    @app.route("/api/flights/start", methods=["POST"])
    def api_start_flight():
        global worker_thread
        if worker_thread is not None and worker_thread.is_alive():
            return jsonify({"error": "recording already in progress"}), 400

        if FOGGUI_SOURCE == "serial":
            source = SerialSource()
        else:
            source = ReplaySource("mockdata.txt", realtime=True)

        os.makedirs("logs", exist_ok=True)
        log_path = os.path.join("logs", f"flight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        stop_event.clear()
        t = threading.Thread(target=ingest_worker, args=(None, source, log_path))
        t.start()
        worker_thread = t

        return jsonify({"flight_id": None}), 201

    @app.route("/api/flights/stop", methods=["POST"])
    def api_stop_flight():
        stop_event.set()
        return "", 204

# ---- cloud mode: analysis + upload ----

else:

    @app.route("/flights")
    def flights():
        return send_from_directory('static', 'flights.html')

    @app.route("/flights/<int:flight_id>")
    def flight_detail(flight_id):
        return send_from_directory('static', 'flight.html')

    @app.route("/api/flights/upload", methods=["POST"])
    def api_upload_flight():
        if "file" not in request.files:
            return jsonify({"error": "no file provided"}), 400

        raw_bytes = request.files["file"].read()
        readings = []
        for line in raw_bytes.decode("utf-8", errors="ignore").splitlines():
            reading = parse_packet(line)
            if reading is not None:
                readings.append(reading)

        if not readings:
            return jsonify({"error": "no valid readings in file"}), 400

        flight_id = start_flight(request.form.get("label"), started_at=readings[0].recorded_at)
        for reading in readings:
            insert_reading(flight_id, reading)
        end_flight(flight_id, ended_at=readings[-1].recorded_at)

        s3_key = f"flights/{flight_id}/raw.txt"
        s3 = boto3.client("s3", region_name="us-west-2")
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=raw_bytes)
        update_s3_key(flight_id, s3_key)

        return jsonify({"flight_id": flight_id}), 201

    @app.route("/api/flights")
    def api_get_flights():
        return jsonify(get_flights())

    @app.route("/api/flights/<int:flight_id>")
    def api_get_flight(flight_id):
        flight = get_flight(flight_id)
        if flight is None:
            return jsonify({"error": "flight not found"}), 404
        return jsonify(flight)

    @app.route("/api/flights/<int:flight_id>/readings")
    def api_get_readings(flight_id):
        if get_flight(flight_id) is None:
            return jsonify({"error": "flight not found"}), 404
        try:
            min_alt = float(request.args["min_alt"]) if "min_alt" in request.args else None
            max_alt = float(request.args["max_alt"]) if "max_alt" in request.args else None
        except ValueError:
            return jsonify({"error": "min_alt and max_alt must be numbers"}), 400
        return jsonify(get_readings(flight_id, min_alt, max_alt))

    @app.route("/api/flights/compare")
    def api_compare_flights():
        ids = request.args.get("ids")
        if ids is None:
            return jsonify({"error": "ids parameter required"}), 400
        readings = {}
        for flight_id in ids.split(","):
            readings[int(flight_id)] = get_readings(flight_id)
        return jsonify(readings)

    @app.route("/api/flights/<int:flight_id>/label", methods=["PATCH"])
    def api_update_label(flight_id):
        label = request.get_json().get("label")
        if not label:
            return jsonify({"error": "label required"}), 400
        update_flight_label(flight_id, label)
        return "", 204

    @app.route("/api/flights/<int:flight_id>", methods=["DELETE"])
    def api_delete_flight(flight_id):
        delete_flight(flight_id)
        return "", 204
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
