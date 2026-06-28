import json
from flask import Flask, Response, send_from_directory
from foggui.sources import ReplaySource, SerialSource
from foggui.parser import parse_packet

source = ReplaySource("mockdata.txt") # temp hardcode

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory('static', 'index.html')

@app.route("/stream")
def stream():
    def eventStream():
        for line in source.lines():
            reading = parse_packet(line)
            if reading is None:
                continue

            data = json.dumps({
                    "altitude_m": reading.altitude_m,
                    "pressure_mb": reading.pressure_mb,
                    "humidity_pct": reading.humidity_pct,
                    "temp_pressure_c": reading.temp_pressure_c,
                    "temp_humidity_c": reading.temp_humidity_c,
                    "uptime_s": reading.uptime_s,
                    })
            
            yield f"data: {data}\n\n"
            
    return Response(eventStream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run()

'''
some error inducing scenarios:
nothing in port? - so can have program running before plugging in 
disconnect from port midway - save data? maybe have check if connected function to call every time
what if no data being read? if its all like 9999 or whatever may be fine just filter it or smth. faulty data?

user may need to select the port in case there are others alr in use?
'''