import numpy as np

# known temperature values for pixel values (for calibration)
knownTemperature = np.array([10, 20, 30, 40])
pixelValues = np.array([30, 100, 150, 255])

# numpy interpolation function to convert pixel value to temperature based on the calibration
def pixelToTemperature(pixelValue):
    return np.interp(pixelValue, pixelValues, knownTemperature)

# function/formula to calcualte distance and effectively identify isolation
def euclideanDistance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)