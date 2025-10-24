import cv2
import datetime
from deepface import DeepFace
from flask import Flask, Response

VIDEO_URL = "http://host.docker.internal:8080/video_feed"
cap = cv2.VideoCapture(VIDEO_URL)
# print(cap)
app = Flask(__name__)
start = 0
end = datetime.datetime.now()
dominant_emotion = ""
age = ""
gender = ""
race = ""
UPDATE_INTERVALL = 2

def generate_frames():
    global start,end,age,dominant_emotion,gender,race
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        if datetime.datetime.now() >= end:
            now = datetime.datetime.now()
            end = now + datetime.timedelta(0,UPDATE_INTERVALL)
        
            try:
                analysis = DeepFace.analyze(frame, actions=['age', 'gender', 'race', 'emotion'], enforce_detection=False)
                
                dominant_emotion = str(analysis[0]['dominant_emotion'])
                age = str(analysis[0]['age'])
                gender = str(analysis[0]['dominant_gender'])
                race = str(analysis[0]['dominant_race'])
                print(analysis)
                

            except Exception as e:
                print(f"⚠️ DeepFace error: {e}")   
        cv2.putText(frame, dominant_emotion, (30, 20),
                cv2.FONT_HERSHEY_COMPLEX, .7, (0, 255, 0), 2)
        cv2.putText(frame, age, (30, 50),
                cv2.FONT_HERSHEY_COMPLEX, .7, (0, 255, 0), 2)
        cv2.putText(frame, gender, (30, 80),
                cv2.FONT_HERSHEY_COMPLEX, .7, (0, 255, 0), 2)
        cv2.putText(frame, race, (30, 110),
                cv2.FONT_HERSHEY_COMPLEX, .7, (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/deepface_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
