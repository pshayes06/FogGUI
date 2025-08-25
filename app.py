from flask import Flask, Response, send_from_directory
import time, random  # random is just for test purposes

app = Flask(__name__)
# serial stuff

@app.route("/")
def home():
    return send_from_directory('static', 'index.html')

@app.route("/stream")
def stream():
    def eventStream():
        while True:
            info = random.randint(1,
                                  100) #serial stuff later
            yield f"data: {info}\n\n"
            time.sleep(1)

    return Response(eventStream(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.run()