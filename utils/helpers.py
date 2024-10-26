import numpy as np
import requests
import time
import os
from dotenv import load_dotenv

# load environmental variables
load_dotenv()

clientId = os.getenv('CLIENT_ID')
clientSecret = os.getenv('CLIENT_SECRET')
tokenUrl = os.getenv('TOKEN_URL')
baseUrl = os.getenv('BASE_URL')
thingId = os.getenv('THING_ID')
propertyId = os.getenv('PROPERTY_ID')

# known temperature values for pixel values (for calibration)
knownTemperature = np.array([0, 10, 20, 30, 32, 34, 35, 35.5, 36, 36.6, 37, 37.5, 38, 38.5, 39, 39.5, 40])
pixelValues = np.array([0, 30, 100, 150, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320])

lastActivationTime = 0

class AccessToken:
    def __init__(self):
        self.token = None
        self.expires_at = 0  # Unix timestamp

    def isExpired(self):
        return time.time() >= self.expires_at

    def setToken(self, token, expires_in):
        self.token = token
        self.expires_at = time.time() + expires_in

# Instantiate the AccessToken class
accessTokenManager = AccessToken()

# numpy interpolation function to convert pixel value to temperature based on the calibration
def pixelToTemperature(pixelValue):
    return np.interp(pixelValue, pixelValues, knownTemperature)

# function/formula to calculate distance and effectively identify isolation
def euclideanDistance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# get Arduino IoT cloud access token
def getAccessToken():
    if accessTokenManager.isExpired():
        data = {
            'grant_type': 'client_credentials',
            'clientId': clientId,
            'clientSecret': clientSecret,
            'audience': 'https://api2.arduino.cc/iot'
        }
        try:
            response = requests.post(tokenUrl, data=data)
            response.raise_for_status()
            token_info = response.json()
            accessTokenManager.setToken(token_info['access_token'], token_info['expires_in'])
            print("New Access Token:", accessTokenManager.token)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching access token: {e}")
            return None
    return accessTokenManager.token

# buzzer activation
def updateBuzzer(state):
    access_token = getAccessToken()
    url = f'{baseUrl}/things/{thingId}/properties/{propertyId}/publish'
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

def activateBuzzer():
    updateBuzzer(True)  # Activate the buzzer
    time.sleep(3)  # Keep the buzzer on for 3 seconds
    updateBuzzer(False)  # Deactivate the buzzer

def controlRelay(arduino, command):
    global lastActivationTime
    currentTime = time.time()  # Get the current time in seconds

    # Check if enough time has passed since the last activation
    if currentTime - lastActivationTime < 30:
        print("Relay is in cooldown. Please wait before sending another command.")
        return
    
    if arduino is None:
        print("Arduino connection is not established.")
        return

    if command == '1':
        arduino.write(b'ON\n')  # Send 'ON' command to Arduino
        print("Relay is turned ON")
        lastActivationTime = currentTime  # Update the last activation time
    elif command == '0':
        arduino.write(b'OFF\n')  # Send 'OFF' command to Arduino
        print("Relay is turned OFF")
        lastActivationTime = currentTime  # Update the last activation time
    else:
        print("Invalid input. Please enter 1 to turn ON or 0 to turn OFF.")

def sendSms(arduino, message, phoneNumber):
    if message and phoneNumber:
        command = f"SMS:{phoneNumber}:{message}\n"
        arduino.write(command.encode())  # Send the SMS command to Arduino
        print(f"Sent SMS to {phoneNumber}: {message}")
    else:
        print("Message cannot be empty.")
