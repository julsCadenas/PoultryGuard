import serial
import time

try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)
    print("Serial port opened successfully.")
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
