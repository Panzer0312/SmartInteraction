# webcam_stream.py
import cv2
from flask import Flask, Response

app = Flask(__name__)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        _, buf = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '<h1>Webcam Stream läuft!</h1><p><a href="/video_feed">Video anzeigen</a></p>'

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080, threaded=True)
    finally:
        cap.release()
