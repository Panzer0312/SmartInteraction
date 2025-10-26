import cv2
import datetime
import threading
import requests
import numpy as np
from deepface import DeepFace
from flask import Flask, Response
import os
import json
import time

VIDEO_URL = os.getenv("VIDEO_URL", "http://host.docker.internal:8080/video_feed")
DATA_ENDPOINT = os.getenv("DATA_ENDPOINT", "http://data-collector:5000/data")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 2))

app = Flask(__name__)

# Globale Variablen für DeepFace-Ergebnisse
results = {"age": "", "gender": "", "emotion": "", "race": ""}
last_update = datetime.datetime.min
frame_lock = threading.Lock()
current_frame = None

def fetch_frames():
    """Liest MJPEG-Frames vom HTTP-Stream"""
    global current_frame
    print("Verbinde mit Stream:", VIDEO_URL)
    resp = requests.get(VIDEO_URL, stream=True)
    bytes_data = b''
    for chunk in resp.iter_content(chunk_size=1024):
        bytes_data += chunk
        a = bytes_data.find(b'\xff\xd8')
        b = bytes_data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            with frame_lock:
                current_frame = frame

def analyze_faces():
    """Führt periodisch DeepFace-Analysen aus"""
    global results, last_update
    while True:
        if current_frame is None:
            continue
        now = datetime.datetime.now()
        if (now - last_update).total_seconds() < UPDATE_INTERVAL:
            continue
        with frame_lock:
            frame_copy = current_frame.copy()
        try:
            analysis = DeepFace.analyze(
                frame_copy,
                actions=['age', 'gender', 'race', 'emotion'],
                enforce_detection=False
            )[0]
            results = {
                "age": str(analysis['age']),
                "gender": str(analysis['dominant_gender']),
                "emotion": str(analysis['dominant_emotion']),
                "race": str(analysis['dominant_race']),
            }
            print("Analyse:", results)
            try:
                resp = requests.post(DATA_ENDPOINT, json=results, timeout=3)
                if resp.status_code != 200:
                    print("⚠️ Fehler beim Senden:", resp.text)
            except Exception as e:
                print("⚠️ Verbindung zu Data Collector fehlgeschlagen:", e)
            last_update = now
        except Exception as e:
            print("⚠️ DeepFace error:", e)

def generate_frames():
    """Erzeugt MJPEG-Ausgabe mit Overlay"""
    while True:
        with frame_lock:
            if current_frame is None:
                continue
            frame = current_frame.copy()

        cv2.putText(frame, f"Emotion: {results['emotion']}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(frame, f"Age: {results['age']}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(frame, f"Gender: {results['gender']}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.putText(frame, f"Race: {results['race']}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        ret, buf = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')

@app.route('/deepface_feed')
def deepface_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=fetch_frames, daemon=True).start()
    threading.Thread(target=analyze_faces, daemon=True).start()
    app.run(host='0.0.0.0', port=8090, threaded=True)