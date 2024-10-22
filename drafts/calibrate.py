# calibration.py
import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load thermal image
def load_thermal_image(image_path="C:/Users/Juls/Downloads/2024-10-19-23-03-45-454cf.jpg"):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not load image at {image_path}")
    return image

# Function to calibrate using known pixel values and temperatures
def calibrate_temperature(known_temperatures, pixel_values):
    # Perform calibration by interpolating between pixel values and known temperatures
    calibration_curve = np.interp(np.arange(0, 256), pixel_values, known_temperatures)
    
    # Plot the calibration curve
    plt.plot(pixel_values, known_temperatures, 'ro')  # known points
    plt.plot(np.arange(0, 256), calibration_curve, 'b-')  # interpolation
    plt.xlabel('Pixel Value')
    plt.ylabel('Temperature (°C)')
    plt.title('Calibration Curve')
    plt.show()

    return calibration_curve

# Function to print the calibration values in the desired format
def print_calibration_values(calibration_curve):
    pixel_values = np.arange(0, 256)
    corresponding_temperatures = calibration_curve

    # Filter out the points where you had actual pixel values from calibration
    print("Updated Calibration:")
    print(f"knownTemperature = np.array({np.round(corresponding_temperatures, 2).tolist()})")
    print(f"pixelValues = np.array({pixel_values.tolist()})")

# Main function to perform calibration
def main():
    # Known temperatures and pixel values for calibration
    knownTemperature = np.array([10, 20, 30, 40])
    pixelValues = np.array([30, 100, 150, 255])

    # Load thermal image (optional step, can be used if you want to visualize or further process it)
    image = load_thermal_image()  # This step loads the thermal image

    # Calibrate temperature using known pixel values and corresponding temperatures
    calibration_curve = calibrate_temperature(knownTemperature, pixelValues)
    
    # Print the updated calibration values
    print_calibration_values(calibration_curve)

if __name__ == "__main__":
    main()
