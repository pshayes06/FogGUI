import json
from flask import Flask, Response, send_from_directory, jsonify, request
from foggui.sources import ReplaySource, SerialSource
from foggui.parser import parse_packet
from foggui.db import start_flight, insert_reading, end_flight, get_flights, get_readings, get_flight, delete_flight
import threading
import queue

app = Flask(__name__)
subscribers = []
active_flight_id = None
worker_thread = None
stop_event = threading.Event()

def ingest_worker(flight_id, source):
    for line in source.lines():
        if stop_event.is_set():
            break
        reading = parse_packet(line)
        if reading is None:
            continue

        insert_reading(flight_id, reading)

        for sub in subscribers:
            sub.put(reading)
        
    end_flight(flight_id)
    for sub in subscribers:
        sub.put(None)
            
@app.route("/")
def home():
    return send_from_directory('static', 'index.html')

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

@app.route("/api/flights")
def api_get_flights():
    return jsonify(get_flights())

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
        return jsonify({"error": "ids paramater required"}), 400

    ids = ids.split(",")
    readings = {}
    for flight_id in ids:
        readings[int(flight_id)] = get_readings(flight_id)

    return jsonify(readings)

@app.route("/api/flights/<int:flight_id>", methods=["DELETE"])
def api_delete_flight(flight_id):
    delete_flight(flight_id)
    return "", 204

@app.route("/api/flights/start", methods=["POST"])
def api_start_flight():
    global worker_thread, active_flight_id
    if worker_thread is not None and worker_thread.is_alive():
        return jsonify({"error": "recording already in progress"}), 400
    flight_id = start_flight()
    source = ReplaySource("mockdata.txt", realtime=True)

    stop_event.clear()
    t = threading.Thread(target=ingest_worker, args=(flight_id, source))
    t.start()
    active_flight_id = flight_id
    worker_thread = t

    return jsonify({"flight_id": flight_id}), 201

@app.route("/api/flights/stop", methods=["POST"])
def api_stop_flight():
    stop_event.set()
    return "", 204

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)