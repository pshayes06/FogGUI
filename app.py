import os

import boto3
from flask import Flask, jsonify, request
from flask_cors import CORS

from foggui.parser import parse_packet
from foggui.db import start_flight, insert_readings, end_flight, get_flights, get_readings, get_flight, delete_flight, update_flight_label, update_s3_key

S3_BUCKET = os.environ.get("S3_BUCKET")

# Read-only mode for the demo (temporary)
FOGGUI_READONLY = os.environ.get("FOGGUI_READONLY", "false") == "true"

app = Flask(__name__)
CORS(app, origins=["https://pshayes06.github.io"])
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024 # 16MB payload limit

@app.route("/api/config")
def api_config():
    return jsonify({"readonly": FOGGUI_READONLY})

@app.route("/")
def home():
    return jsonify({"service": "foggui-api"}), 200

@app.route("/api/flights/upload", methods=["POST"])
def api_upload_flight():
    if FOGGUI_READONLY:
        return jsonify({"error": "read-only mode"}), 403
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
    insert_readings(flight_id, readings)
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

@app.route("/api/flights/<int:flight_id>/label", methods=["PATCH"])
def api_update_label(flight_id):
    if FOGGUI_READONLY:
        return jsonify({"error": "read-only mode"}), 403
    label = request.get_json().get("label")
    if not label:
        return jsonify({"error": "label required"}), 400
    update_flight_label(flight_id, label)
    return "", 204

@app.route("/api/flights/<int:flight_id>", methods=["DELETE"])
def api_delete_flight(flight_id):
    if FOGGUI_READONLY:
        return jsonify({"error": "read-only mode"}), 403
    s3_key = delete_flight(flight_id)
    if s3_key:
        s3 = boto3.client("s3", region_name="us-west-2")
        s3.delete_object(Bucket=S3_BUCKET, Key=s3_key)
    return "", 204
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))