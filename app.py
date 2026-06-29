import json
from flask import Flask, Response, send_from_directory, jsonify, request
from foggui.sources import ReplaySource, SerialSource
from foggui.parser import parse_packet
from foggui.db import start_flight, insert_reading, end_flight, get_flights, get_readings


app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory('static', 'index.html')

@app.route("/stream")
def stream():
    source = ReplaySource("nothing.txt", realtime=True) # temp hardcode, change to mockdata later too
    flight_id = start_flight()
    def eventStream():
        try:
            for line in source.lines():
                reading = parse_packet(line)
                if reading is None:
                    continue

                insert_reading(flight_id, reading)

                data = json.dumps({
                        "altitude_m": reading.altitude_m,
                        "pressure_mb": reading.pressure_mb,
                        "humidity_pct": reading.humidity_pct,
                        "temp_pressure_c": reading.temp_pressure_c,
                        "temp_humidity_c": reading.temp_humidity_c,
                        "uptime_s": reading.uptime_s,
                        })
                
                yield f"data: {data}\n\n"
            yield "data: done\n\n"
            end_flight(flight_id)
        except GeneratorExit:
            end_flight(flight_id)

    return Response(eventStream(), mimetype="text/event-stream")

@app.route("/api/flights")
def api_get_flights():
    return jsonify(get_flights())

@app.route("/api/flights/<int:flight_id>/readings")
def api_get_readings(flight_id):
    min_alt = request.args.get("min_alt")
    max_alt = request.args.get("max_alt")
    return jsonify(get_readings(flight_id, min_alt, max_alt))

@app.route("/api/flights/compare") # ?ids=1,2,3 is formatting
def api_compare_flights():
    ids = request.args.get("ids")

    if ids is None:
        return jsonify({"error": "ids paramater required"}), 400

    ids = ids.split(",")
    readings = {}
    for flight_id in ids:
        readings[int(flight_id)] = get_readings(flight_id)

    return jsonify(readings)


if __name__ == '__main__':
    app.run(port=5001)