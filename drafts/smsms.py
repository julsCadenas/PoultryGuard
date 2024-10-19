import serial
import time

# Set up serial communication with Arduino
# Change 'COM8' to the correct port for your Arduino (e.g., '/dev/ttyUSB0' on Linux)
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

# Function to send SMS through Arduino
def send_sms(message):
    # message = "Heat stress detected"
    if message:
        command = f"SMS:{message}\n"
        arduino.write(command.encode())  # Send the custom SMS message
        print(f"Sent SMS: {message}")
    else:
        print("Message cannot be empty.")

# Main function to interact with the user
def main():
    while True:
        print("\nOptions:")
        print("1 - Turn ON the relay")
        print("0 - Turn OFF the relay")
        print("s - Send an SMS")
        print("q - Quit")

        user_input = input("Enter your choice: ").strip()

        if user_input.lower() == 'q':
            print("Exiting program...")
            break  # Exit the loop if the user enters 'q'

        elif user_input == 's':
            send_sms()  # Send SMS based on user input

        else:
            # Control relay based on user input
            control_relay(user_input)

# Run the main function
try:
    main()
finally:
    # Close the serial connection gracefully
    arduino.close()
    print("Serial connection closed.")
