from flask import Flask, render_template, Response
import cv2
import time
import serial
from ultralytics import YOLO

# import functions
from streams.thermal import thermalStream
from streams.webcam import webcamStream

# initialize the flask server
app = Flask(__name__)

# import the model
modelPath = "C:/Users/Juls/Desktop/finaldraft/models/etian35.pt"
model = YOLO(modelPath)
names = model.model.names

# set the cameras
webcam = cv2.VideoCapture(1)
thermalCamera = cv2.VideoCapture(0)

try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    exit(1)

# dont forget to set the html template on templates/index.html
@app.route('/')
def index():
    return render_template('index.html')

# set the rgb camera feed and route
@app.route('/webcam_feed')
def webcam_feed():
    return Response(webcamStream(webcam, model, thermalCamera, arduino, distanceThreshold=300),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# set the thermal camera feed and route
@app.route('/thermal_feed')
def thermal_feed():
    return Response(thermalStream(webcam, thermalCamera, model),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# initialize the app on port 5000 
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()
            print("Serial port closed.")