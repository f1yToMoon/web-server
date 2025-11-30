from flask import Flask, request, jsonify
import json
import time
import os

CONFIG_PATH = "config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

FILE_PATH = config["current_state_path"]
SNAPSHOT_FILE = config["snapshot_path"]
SNAPSHOT_INTERVAL = config["snapshot_interval_sec"]

LAST_SNAPSHOT_TIME = 0

app = Flask(__name__)

@app.put("/replace")
def replace():
    global LAST_SNAPSHOT_TIME

    data = request.get_json()
    if not data or "source" not in data or "id" not in data or "payload" not in data:
        return jsonify({"error": "invalid json"}), 400

    payload = data["payload"]

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(payload)

    now = time.time()
    if now - LAST_SNAPSHOT_TIME >= SNAPSHOT_INTERVAL:
        with open(SNAPSHOT_FILE, "a", encoding="utf-8") as f:
            f.write(payload + "\n")
        LAST_SNAPSHOT_TIME = now

    return jsonify({"status": "ok"}), 200


@app.get("/get")
def get():
    if not os.path.exists(FILE_PATH):
        return jsonify({"payload": ""}), 200

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    return jsonify({"payload": content}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)