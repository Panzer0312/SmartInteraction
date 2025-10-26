from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)
DATA_FILE = "collected_data.json"

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.get_json()
    data["received_at"] = time.time()
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"status": "ok"}), 200

@app.route("/data", methods=["GET"])
def get_data():
    if not os.path.exists(DATA_FILE):
        return jsonify([])
    with open(DATA_FILE) as f:
        return jsonify([json.loads(line) for line in f])
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)