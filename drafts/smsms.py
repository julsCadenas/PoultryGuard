import serial
import time

# Set up serial communication with Arduino
try:
    arduino = serial.Serial('COM8', 9600, timeout=0.1)
    time.sleep(2)  # Wait for the connection to establish
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    exit(1)

# Variables for phone number and message
phone_number = "+639089367868"  # Replace this with any number you want
message = "urmom"

# Function to control the relay
def control_relay(command):
    if command == '1':
        arduino.write(b'ON\n')  # Send 'ON' command to Arduino
        print("Relay is turned ON")
    elif command == '0':
        arduino.write(b'OFF\n')  # Send 'OFF' command to Arduino
        print("Relay is turned OFF")
    else:
        print("Invalid input. Please enter 1 to turn ON or 0 to turn OFF.")

# Function to send an SMS
def send_sms(phone_number, message):
    if phone_number and message:
        command = f"SMS:{phone_number}:{message}\n"
        arduino.write(command.encode())  # Send the phone number and SMS message to Arduino
        print(f"Sent SMS to {phone_number}: {message}")
    else:
        print("Phone number and message cannot be empty.")

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
            break

        elif user_input == 's':
            send_sms(phone_number, message)

        else:
            control_relay(user_input)

# Run the main function
try:
    main()
finally:
    arduino.close()
    print("Serial connection closed.")
