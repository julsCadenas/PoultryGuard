import cv2
import csv
import os
import numpy as np
import threading
from datetime import datetime

from utils.helpers import pixelToTemperature, euclideanDistance, get_access_token, activate_buzzer, control_relay, send_sms

# Set the folder to save frames that detected heat stress
saveFolder = 'savedframes'
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)

# Set the excel/csv file where the temperature data will be saved
csvFile = 'templogs.csv'
if not os.path.exists(csvFile):
    with open(csvFile, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Frame", "Temperature"])  # columns

def webcamStream(webcam, model, thermalCamera, arduino, distanceThreshold):
    access_token = get_access_token()  # Get access token for Arduino IoT
    if access_token is None:
        print("Exiting due to access token error.")
        return
    
    while True:
        retWebcam, frameWebcam = webcam.read()
        if not retWebcam:
            break

        # Store the detections in a variable
        results = model.predict(source=frameWebcam)
        detections = results[0].boxes  # store results inside a list
        isolatedFlags = [True] * len(detections)  # initialize isolation
        temperatures = []  # initialize array to store temperature data
        # control_relay(arduino, command='0')

        for i, box in enumerate(detections):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Draw the bounding boxes with labels
            cv2.rectangle(frameWebcam, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frameWebcam, "Chicken", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Label the box

            # Extract the temperature data from the thermal video feed
            thermalX1 = int(x1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY1 = int(y1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))
            thermalX2 = int(x2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY2 = int(y2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))

            thermalCamera.set(cv2.CAP_PROP_POS_FRAMES, 0)

            retThermal, frameThermal = thermalCamera.read()
            if retThermal:
                thermalImage = cv2.cvtColor(frameThermal, cv2.COLOR_BGR2GRAY)
                # check if the coordinates are within the camera FOV
                if (0 <= thermalX1 < thermalImage.shape[1] and 0 <= thermalY1 < thermalImage.shape[0]
                        and 0 <= thermalX2 < thermalImage.shape[1] and 0 <= thermalY2 < thermalImage.shape[0]):
                    boundingBoxThermal = thermalImage[thermalY1:thermalY2, thermalX1:thermalX2]
                    maxPixelValue = np.max(boundingBoxThermal)
                    chickenTemperature = pixelToTemperature(maxPixelValue)
                    temperatures.append(chickenTemperature)

                    # if temperature > 35 degrees, save the frame and log it
                    if chickenTemperature > 35:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = os.path.join(saveFolder, f'frame_{timestamp}.jpg')
                        cv2.imwrite(filename, frameWebcam)
                        control_relay(arduino, command='1')

                        with open(csvFile, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([timestamp, filename, f'{chickenTemperature:.2f}'])
                    elif chickenTemperature < 35:
                        control_relay( arduino, command='0')
                else:
                    temperatures.append(None)
            else:
                temperatures.append(None)

        if len(detections) == len(temperatures):
            for i in range(len(detections)):
                for j in range(len(detections)):
                    if i != j:
                        x1, y1, _, _ = map(int, detections[i].xyxy[0].tolist())
                        x2, y2, _, _ = map(int, detections[j].xyxy[0].tolist())
                        dist = euclideanDistance([x1, y1], [x2, y2])
                        # If distance is less than the set threshold then isolation is false
                        if dist < distanceThreshold:
                            isolatedFlags[i] = False
                            isolatedFlags[j] = False

            for idx, (box, isolated) in enumerate(zip(detections, isolatedFlags)):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                if isolated:
                    # Print "Isolated" on top of the bounding box
                    cv2.putText(frameWebcam, "Isolated", (x1, y1 - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.rectangle(frameWebcam, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    
                    if temperatures[idx] is not None and temperatures[idx] > 35:
                        # Start a new thread to activate the buzzer and sms
                        message = "Heat stress detected"
                        threading.Thread(target=activate_buzzer, args=(access_token,)).start()
                        send_sms(arduino, message)
                        print("Isolated chicken detected. Buzzer activated. Email and SMS sent")

                if temperatures[idx] is not None:
                    # Print the temperature on top of the bounding box
                    cv2.putText(frameWebcam, f'Temp: {temperatures[idx]:.2f} C', (x1, y1 - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', frameWebcam)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')