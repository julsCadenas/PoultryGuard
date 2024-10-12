# import libraries
import cv2
import numpy as np

# import functions
from utils.helpers import pixelToTemperature

def thermalStream(webcam, thermalCamera, model):
    while True:
        retWebcam, frameWebcam = webcam.read() 
        retThermal, frameThermal = thermalCamera.read() 
        if not retThermal or not retWebcam:
            break
        
        # remove the second video feed from the thermal camera
        height, width, _ = frameThermal.shape
        frameThermal = frameThermal[:height // 2, :]

        # colorize the thermal video feed (originally grayscale) for better visualization
        thermalImage = cv2.cvtColor(frameThermal, cv2.COLOR_BGR2GRAY)
        thermalImageNormalized = cv2.normalize(thermalImage, None, 0, 255, cv2.NORM_MINMAX)
        thermalImageColored = cv2.applyColorMap(thermalImageNormalized, cv2.COLORMAP_JET)

        # map the detections from the webcam to the thermal camera
        results = model.predict(source=frameWebcam) # get the predictions from the webcam video feed
        detections = results[0].boxes # store in a list
        
        # map the bounding boxes        
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            thermalX1 = int(x1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY1 = int(y1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))
            thermalX2 = int(x2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
            thermalY2 = int(y2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))

            cv2.rectangle(thermalImageColored, (thermalX1, thermalY1), (thermalX2, thermalY2), (0, 255, 0), 2)

            boundingBoxThermal = thermalImage[thermalY1:thermalY2, thermalX1:thermalX2] # extract the thermal data
            if boundingBoxThermal.size > 0:
                maxPixelValue = np.max(boundingBoxThermal)
                chickenTemperature = pixelToTemperature(maxPixelValue) # calcualte pixel to temperature data
                # print the temperature number
                cv2.putText(thermalImageColored, f'Temp: {chickenTemperature:.2f} C', 
                            (thermalX1, thermalY1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', thermalImageColored)
        frame = jpeg.tobytes()
        # yield not return
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')