import json
from flask import Flask, Response, send_from_directory
from foggui.sources import ReplaySource, SerialSource
from foggui.parser import parse_packet
from foggui.db import start_flight, insert_reading, end_flight


app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory('static', 'index.html')

@app.route("/stream")
def stream():
    source = ReplaySource("mockdata.txt", realtime=True) # temp hardcode
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
        except GeneratorExit:
            end_flight(flight_id)

    return Response(eventStream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(port=5001)