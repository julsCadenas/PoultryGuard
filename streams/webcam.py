import cv2
import csv
import os
import numpy as np
from datetime import datetime

from utils.helpers import pixelToTemperature, euclideanDistance

# set the folder to save frames that detected heat stress
saveFolder = 'savedframes'
if not os.path.exists(saveFolder):
    os.makedirs(saveFolder)

# set the excel/csv file where the temperature data will be saved
csvFile = 'templogs.csv'
if not os.path.exists(csvFile):
    with open(csvFile, mode='w') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Frame", "Temperature"]) # columns

def webcamStream(webcam, model, thermalCamera, distanceThreshold):
    while True:
        retWebcam, frameWebcam = webcam.read()
        if not retWebcam:
            break
        
        # store the detections in a variable
        results = model.predict(source=frameWebcam)  
        
        
        detections = results[0].boxes # store results inside a list
        isolatedFlags = [True] * len(detections) # initialize isolation
        temperatures = [] # initialize array to store temperature data

        
        for i, box in enumerate(detections):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())  

            # draw the bounding boxes
            cv2.rectangle(frameWebcam, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # extract the temperature data from the thermal video feed
            thermalX1 = int(x1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY1 = int(y1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))
            thermalX2 = int(x2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY2 = int(y2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))

            thermalCamera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            retThermal, frameThermal = thermalCamera.read()
            if retThermal:
                thermalImage = cv2.cvtColor(frameThermal, cv2.COLOR_BGR2GRAY)
                # function to calculate the temperature
                if (0 <= thermalX1 < thermalImage.shape[1] and 0 <= thermalY1 < thermalImage.shape[0]
                        and 0 <= thermalX2 < thermalImage.shape[1] and 0 <= thermalY2 < thermalImage.shape[0]): # checks if the coorindates are within the camera fov
                    boundingBoxThermal = thermalImage[thermalY1:thermalY2, thermalX1:thermalX2] # get the bounding box from the coordinates 
                    maxPixelValue = np.max(boundingBoxThermal) # get the maximum temperature inside the bounding box
                    chickenTemperature = pixelToTemperature(maxPixelValue) # set the maximum temperature as the temperature detected
                    temperatures.append(chickenTemperature) # set the value
                    
                    # function for heat stress stuff
                    # if temperature greater than 35 degrees, save the date, time, temperature into the csv file and capture the frame with bounding boxes
                    if chickenTemperature > 35:
                        # data to input to the csv file
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = os.path.join(saveFolder, f'frame_{timestamp}.jpg')
                        cv2.imwrite(filename, frameWebcam)

                        with open(csvFile, mode='a', newline='') as file:
                            writer = csv.writer(file)
                            writer.writerow([timestamp, filename, f'{chickenTemperature:.2f}'])
                    
                else:
                    temperatures.append(None)
            else:
                temperatures.append(None)

        if len(detections) == len(temperatures):
            for i in range(len(detections)):
                for j in range(len(detections)):
                    if i != j:
                        dist = euclideanDistance([x1, y1], [x2, y2]) # calculate the distance
                        # if distance is less than the set threshold then isolation is false
                        if dist < distanceThreshold:
                            isolatedFlags[i] = False
                            isolatedFlags[j] = False

            for idx, (box, isolated) in enumerate(zip(detections, isolatedFlags)):
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

                if isolated:
                    # print "isolation" on top of bounding box
                    cv2.putText(frameWebcam, "Isolated", (x1, y1 - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.rectangle(frameWebcam, (x1, y1), (x2, y2), (0, 0, 255), 2)

                if temperatures[idx] is not None:
                    # print the temperature on top of bounding box
                    cv2.putText(frameWebcam, f'Temp: {temperatures[idx]:.2f} C', (x1, y1 - 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', frameWebcam)
        frame = jpeg.tobytes()
        # yield not return
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')