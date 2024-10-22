import numpy as np
import requests
import time
import os
from dotenv import load_dotenv

# load environmental variables
load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
token_url = os.getenv('TOKEN_URL')
base_url = os.getenv('BASE_URL')
thing_id = os.getenv('THING_ID')
property_id = os.getenv('PROPERTY_ID')

# known temperature values for pixel values (for calibration)
knownTemperature = np.array([0, 10, 20, 30, 32, 34, 35, 35.5, 36, 36.6, 37, 37.5, 38, 38.5, 39, 39.5, 40])
pixelValues = np.array([0, 30, 100, 150, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320])

last_activation_time = 0 

# numpy interpolation function to convert pixel value to temperature based on the calibration
def pixelToTemperature(pixelValue):
    return np.interp(pixelValue, pixelValues, knownTemperature)

# function/formula to calcualte distance and effectively identify isolation
def euclideanDistance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# get arduino iot cloud access token
def get_access_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'audience': 'https://api2.arduino.cc/iot'
    }
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_info = response.json()
        access_token = token_info['access_token']
        print("Access Token:", access_token)
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Error fetching access token: {e}")
        return None

# buzzer activation
def update_buzzer(state, access_token):
    url = f'{base_url}/things/{thing_id}/properties/{property_id}/publish'
    data = {'value': state}
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Buzzer {'activated' if state else 'deactivated'}!")
    except requests.exceptions.RequestException as e:
        print(f"Error updating buzzer: {e}")
        
def activate_buzzer(access_token):
    update_buzzer(True, access_token)  # Activate the buzzer
    time.sleep(3)  # Keep the buzzer on for 3 seconds
    update_buzzer(False, access_token)  # Deactivate the buzzer
    
def control_relay(arduino, command):
    global last_activation_time
    current_time = time.time()  # Get the current time in seconds

    # Check if enough time has passed since the last activation
    if current_time - last_activation_time < 30:
        print("Relay is in cooldown. Please wait before sending another command.")
        return

    if command == '1':
        arduino.write(b'ON\n')  # Send 'ON' command to Arduino
        print("Relay is turned ON")
        last_activation_time = current_time  # Update the last activation time
    elif command == '0':
        arduino.write(b'OFF\n')  # Send 'OFF' command to Arduino
        print("Relay is turned OFF")
        last_activation_time = current_time  # Update the last activation time
    else:
        print("Invalid input. Please enter 1 to turn ON or 0 to turn OFF.")

def send_sms(arduino, message, phoneNumber):
    if message and phoneNumber:
        command = f"SMS:{phoneNumber}:{message}\n"
        arduino.write(command.encode())  # Send the SMS command to Arduino
        print(f"Sent SMS to {phoneNumber}: {message}")
    else:
        print("Message cannot be empty.")
