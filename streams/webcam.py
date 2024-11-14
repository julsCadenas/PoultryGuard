import cv2
import csv
import os
import numpy as np
import threading
from datetime import datetime
import signal
import time
from utils.helpers import pixelToTemperature, euclideanDistance, get_access_token, send_sms

# Set the folder to save frames that detected heat stress
saveFolder = 'savedframes'
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)

# Set the excel/csv file where the temperature data and events will be saved
csvFile = 'templogs.csv'
if not os.path.exists(csvFile):
    with open(csvFile, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Frame", "Temperature", "Relay Activated", "Buzzer Activated", "SMS Sent"])

# Video writer initialization
videoFileName = None
videoWriter = None

# Relay cooldown management
relay_cooldown = 5  # Cooldown period in seconds
last_activation_time = time.time() - relay_cooldown  # Initialize to allow immediate activation
relay_activated = False

def start_video_recording(frame_size, fps=20):
    global videoFileName, videoWriter
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    videoFileName = os.path.join(saveFolder, f'webcam_{timestamp}.avi')
    
    # Define codec and create VideoWriter object (use 'XVID' or 'MJPG' for .avi file)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    videoWriter = cv2.VideoWriter(videoFileName, fourcc, fps, frame_size)

def stop_video_recording():
    global videoWriter
    if videoWriter is not None:
        videoWriter.release()
        print(f"Video saved as {videoFileName}")
        videoWriter = None

def signal_handler(sig, frame):
    # Handle shutdown to close video recording properly
    stop_video_recording()
    print("Application closed.")
    exit(0)

# Attach signal handler to handle program exit
signal.signal(signal.SIGINT, signal_handler)

def webcamStream(webcam, model, thermalCamera, arduino, phoneNumber, tempThreshold, distanceThreshold):
    global videoWriter, last_activation_time, relay_activated

    # Get the access token for Arduino IoT
    access_token = get_access_token()
    if access_token is None:
        print("Exiting due to access token error.")
        return

    # Start video recording
    retWebcam, frameWebcam = webcam.read()
    if retWebcam:
        frame_size = (frameWebcam.shape[1], frameWebcam.shape[0])
        start_video_recording(frame_size)

    isolation_start_time = {}
    while True:
        retWebcam, frameWebcam = webcam.read()
        if not retWebcam:
            break

        # Store the detections in a variable
        results = model.predict(source=frameWebcam)
        detections = results[0].boxes
        isolatedFlags = [True] * len(detections)
        temperatures = []
        high_temp_detected = False

        for i, box in enumerate(detections):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cv2.rectangle(frameWebcam, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frameWebcam, "Chicken", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Calculate temperature using thermal camera coordinates
            thermalX1 = int(x1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY1 = int(y1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))
            thermalX2 = int(x2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY2 = int(y2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))

            thermalCamera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            retThermal, frameThermal = thermalCamera.read()

            if retThermal:
                thermalImage = cv2.cvtColor(frameThermal, cv2.COLOR_BGR2GRAY)
                if (0 <= thermalX1 < thermalImage.shape[1] and 0 <= thermalY1 < thermalImage.shape[0]
                        and 0 <= thermalX2 < thermalImage.shape[1] and 0 <= thermalY2 < thermalImage.shape[0]):
                    boundingBoxThermal = thermalImage[thermalY1:thermalY2, thermalX1:thermalX2]
                    maxPixelValue = np.max(boundingBoxThermal)
                    chickenTemperature = pixelToTemperature(maxPixelValue)
                    temperatures.append(chickenTemperature)

                    if isinstance(chickenTemperature, (int, float)) and isinstance(tempThreshold, (int, float)):
                        if chickenTemperature > tempThreshold:
                            high_temp_detected = True
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = os.path.join(saveFolder, f'frame_{timestamp}.jpg')
                            cv2.imwrite(filename, frameWebcam)
                            
                        with open(csvFile, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([datetime.now().strftime('%Y%m%d_%H%M%S'), "None", f'{chickenTemperature:.2f}', relay_activated, False, False])
                    else:
                        print(f"Type mismatch: chickenTemperature={chickenTemperature}, tempThreshold={tempThreshold}")
                else:
                    temperatures.append(None)
            else:
                temperatures.append(None)

        # Relay activation based on high_temp_detected flag
        current_time = time.time()
        if high_temp_detected:
            if (current_time - last_activation_time >= relay_cooldown) and not relay_activated:
                arduino.write(b'1\n')  # Turn ON relay
                print("High temperature detected. Relay ON.")
                last_activation_time = current_time
                relay_activated = True
        else:
            if relay_activated:
                arduino.write(b'0\n')  # Turn OFF relay
                print("Relay OFF.")
                relay_activated = False

        # Checking for isolation and adding related text
        if len(detections) == len(temperatures):
            for i in range(len(detections)):
                for j in range(len(detections)):
                    if i != j:
                        x1, y1, _, _ = map(int, detections[i].xyxy[0].tolist())
                        x2, y2, _, _ = map(int, detections[j].xyxy[0].tolist())
                        dist = euclideanDistance([x1, y1], [x2, y2])
                        if dist < distanceThreshold:
                            isolatedFlags[i] = False
                            isolatedFlags[j] = False

            for idx, (box, isolated) in enumerate(zip(detections, isolatedFlags)):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                
                if isolated:
                    if idx not in isolation_start_time:
                        isolation_start_time[idx] = time.time()  # Start isolation timer
                    elif time.time() - isolation_start_time[idx] >= 5:  # 5-second delay
                        cv2.putText(frameWebcam, "Isolated", (x1, y1 - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        cv2.rectangle(frameWebcam, (x1, y1), (x2, y2), (0, 0, 255), 2)

                        if temperatures[idx] is not None and temperatures[idx] > tempThreshold:
                            message = "Heat stress detected"
                            threading.Thread(target=send_sms, args=(phoneNumber, message)).start()
                            print("Isolated chicken detected. SMS sent.")

                            with open(csvFile, mode='a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow([datetime.now().strftime('%Y%m%d_%H%M%S'), "None", f'{temperatures[idx]:.2f}', True, True, True])
                        else:
                            with open(csvFile, mode='a', newline='') as file:
                                writer = csv.writer(file)
                                writer.writerow([datetime.now().strftime('%Y%m%d_%H%M%S'), "None", 'N/A', False, False, False])
                else:
                    isolation_start_time.pop(idx, None)  # Reset if no longer isolated

                if temperatures[idx] is not None:
                    cv2.putText(frameWebcam, f'Temp: {temperatures[idx]:.2f} C', (x1, y1 - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Record the frame with annotations in the video
        if videoWriter is not None:
            videoWriter.write(frameWebcam)  # Write the frame with boxes and text

        # Yield the frame for the live stream
        ret, jpeg = cv2.imencode('.jpg', frameWebcam)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    # Stop video recording if streaming ends
    stop_video_recording()
