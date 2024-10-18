import serial
import time

# Set up serial communication with Arduino
# Change 'COM3' to the correct port for your Arduino (e.g., '/dev/ttyUSB0' on Linux)
try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    exit(1)

# Function to send command to Arduino
def control_relay(command):
    if command == '1':
        arduino.write(b'ON\n')  # Send 'ON' command to Arduino
        print("Relay is turned ON")
    elif command == '0':
        arduino.write(b'OFF\n')  # Send 'OFF' command to Arduino
        print("Relay is turned OFF")
    else:
        print("Invalid input. Please enter 1 to turn ON or 0 to turn OFF.")

# Main function to interact with the user
def main():
    while True:
        user_input = input("Enter 1 to turn ON or 0 to turn OFF (q to quit): ").strip()

        if user_input.lower() == 'q':
            print("Exiting program...")
            break  # Exit the loop if the user enters 'q'
        
        # Control relay based on user input
        control_relay(user_input)

# Run the main function
try:
    main()
finally:
    # Close the serial connection gracefully
    arduino.close()
    print("Serial connection closed.")
