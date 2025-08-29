from flask import Flask, Response, send_from_directory
import serial, time

app = Flask(__name__)
PORT = ""
BAUDRATE = 115200

ser = serial.Serial(PORT, BAUDRATE, timeout=1) # can write something to prompt user selection instead of hardcoding above later
                                               # also handle no connection and close port later
@app.route("/")
def home():
    return send_from_directory('static', 'index.html')

@app.route("/stream")
def stream():
    def eventStream():
        while True:
            data = ser.readline().decode("utf-8")
            if data[:6] != "905302": # could look into different way to check - sometimes imet provides incomplete data
                yield f"data: {data}\n\n"
            time.sleep(1)
    return Response(eventStream(), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run()