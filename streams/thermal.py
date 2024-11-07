# import libraries
import cv2
import numpy as np

# import functions
from utils.helpers import pixelToTemperature

def thermalStream(webcam, thermalCamera, model):
    # Define your offsets here
    x_offset = 5  # Example value, adjust based on your observation
    y_offset = -20  # Example value, adjust based on your observation

    while True:
        retWebcam, frameWebcam = webcam.read() 
        retThermal, frameThermal = thermalCamera.read() 
        if not retThermal or not retWebcam:
            break
        
        # Get dimensions of both streams
        webcam_height, webcam_width = frameWebcam.shape[:2]
        thermal_height, thermal_width = frameThermal.shape[:2]
        
        # Remove the second video feed from the thermal camera
        frameThermal = frameThermal[:thermal_height // 2, :]

        # Colorize the thermal video feed (originally grayscale) for better visualization
        thermalImage = cv2.cvtColor(frameThermal, cv2.COLOR_BGR2GRAY)
        thermalImageNormalized = cv2.normalize(thermalImage, None, 0, 255, cv2.NORM_MINMAX)
        thermalImageColored = cv2.applyColorMap(thermalImageNormalized, cv2.COLORMAP_JET)

        # Map the detections from the webcam to the thermal camera
        results = model.predict(source=frameWebcam)  # Get predictions from the webcam video feed
        detections = results[0].boxes  # Store in a list

        # Calculate scaling factors
        width_scale = thermal_width / webcam_width
        height_scale = thermal_height / webcam_height

        # Map the bounding boxes        
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

            # Scale the coordinates to match the thermal camera dimensions with offsets
            thermalX1 = int(x1 * width_scale) + x_offset
            thermalY1 = int(y1 * height_scale) + y_offset
            thermalX2 = int(x2 * width_scale) + x_offset
            thermalY2 = int(y2 * height_scale) + y_offset

            # Ensure that the coordinates do not exceed the image dimensions
            thermalX1 = max(0, min(thermalX1, thermal_width - 1))
            thermalY1 = max(0, min(thermalY1, thermal_height - 1))
            thermalX2 = max(0, min(thermalX2, thermal_width - 1))
            thermalY2 = max(0, min(thermalY2, thermal_height - 1))

            cv2.rectangle(thermalImageColored, (thermalX1, thermalY1), (thermalX2, thermalY2), (0, 255, 0), 2)

            boundingBoxThermal = thermalImage[thermalY1:thermalY2, thermalX1:thermalX2]  # Extract the thermal data
            if boundingBoxThermal.size > 0:
                maxPixelValue = np.max(boundingBoxThermal)
                chickenTemperature = pixelToTemperature(maxPixelValue)  # Calculate pixel to temperature data
                # Print the temperature number
                # cv2.putText(thermalImageColored, f'Temp: {chickenTemperature:.2f} C', 
                #             (thermalX1, thermalY1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', thermalImageColored)
        frame = jpeg.tobytes()
        # Yield, not return
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# # import libraries
# import cv2
# import numpy as np

# # import functions
# from utils.helpers import pixelToTemperature

# def thermalStream(webcam, thermalCamera, model):
#     while True:
#         retWebcam, frameWebcam = webcam.read() 
#         retThermal, frameThermal = thermalCamera.read() 
#         if not retThermal or not retWebcam:
#             break
        
#         # remove the second video feed from the thermal camera
#         height, width, _ = frameThermal.shape
#         frameThermal = frameThermal[:height // 2, :]

#         # colorize the thermal video feed (originally grayscale) for better visualization
#         thermalImage = cv2.cvtColor(frameThermal, cv2.COLOR_BGR2GRAY)
#         thermalImageNormalized = cv2.normalize(thermalImage, None, 0, 255, cv2.NORM_MINMAX)
#         thermalImageColored = cv2.applyColorMap(thermalImageNormalized, cv2.COLORMAP_JET)

#         # map the detections from the webcam to the thermal camera
#         results = model.predict(source=frameWebcam) # get the predictions from the webcam video feed
#         detections = results[0].boxes # store in a list
        
#         # map the bounding boxes        
#         for box in detections:
#             x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

#             thermalX1 = int(x1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
#             thermalY1 = int(y1 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))
#             thermalX2 = int(x2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_WIDTH) / frameWebcam.shape[1]))
#             thermalY2 = int(y2 * (thermalCamera.get(cv2.CAP_PROP_FRAME_HEIGHT) / frameWebcam.shape[0]))

#             cv2.rectangle(thermalImageColored, (thermalX1, thermalY1), (thermalX2, thermalY2), (0, 255, 0), 2)

#             boundingBoxThermal = thermalImage[thermalY1:thermalY2, thermalX1:thermalX2] # extract the thermal data
#             if boundingBoxThermal.size > 0:
#                 maxPixelValue = np.max(boundingBoxThermal)
#                 chickenTemperature = pixelToTemperature(maxPixelValue) # calcualte pixel to temperature data
#                 # print the temperature number
#                 cv2.putText(thermalImageColored, f'Temp: {chickenTemperature:.2f} C', 
#                             (thermalX1, thermalY1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

#         ret, jpeg = cv2.imencode('.jpg', thermalImageColored)
#         frame = jpeg.tobytes()
#         # yield not return
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')