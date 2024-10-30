import threading
import customtkinter as ctk
import cv2
import time
import webbrowser
import serial
from ultralytics import YOLO
from flask import Flask, render_template, Response, jsonify

# Import functions
from streams.thermal import thermalStream
from streams.webcam import webcamStream

# try push

# Initialize the Flask server
app = Flask(__name__)

# Import the model
modelPath = "C:/Users/Juls/Desktop/finaldraft/models/etian35.pt"
model = YOLO(modelPath)
names = model.model.names

# Set the cameras
webcam = cv2.VideoCapture(1)
thermalCamera = cv2.VideoCapture(0)

# check cameras
if webcam.isOpened() and thermalCamera.isOpened():
    cameraStatus = "Cameras initialized"
else:
    cameraStatus = "Cameras not found"

print(cameraStatus)

phoneNumber = ""
arduinoStatus = "Not connected"
gsmStatus = "Not connected"
tempThreshold = 35
distanceThreshold = 300

serverThread = None

try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
except serial.SerialException as e:
    arduino = None
    print(f"Error: Could not open serial port: {e}")

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webcam_feed')
def webcam_feed():
    return Response(webcamStream(webcam, model, thermalCamera, arduino, phoneNumber, tempThreshold, distanceThreshold),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/thermal_feed')
def thermal_feed():
    return Response(thermalStream(webcam, thermalCamera, model),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    return jsonify({
        'phoneNumber': phoneNumber,
        'arduinoStatus': arduinoStatus,
        'gsmStatus': gsmStatus,
        'tempThreshold': tempThreshold
    })

# Flask server control in a separate thread
def runFlask():
    app.run(host='0.0.0.0', port=5000, debug=False)


def startServer(startButton):
    global serverThread
    if serverThread is None or not serverThread.is_alive():
        serverThread = threading.Thread(target=runFlask)
        serverThread.daemon = True
        serverThread.start()
        print('Server started')
        startButton.configure(state="disabled")
        time.sleep(1)  
        webbrowser.open("http://localhost:5000")

def openArduinoLink():
    webbrowser.open("https://id.arduino.cc/?iss=https%3A%2F%2Flogin.arduino.cc%2F#/sso/login")

# Create GUI with customtkinter
def createGui():
    ctk.set_appearance_mode("dark")  # "system", "dark", "light"
    ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

    def checkStartButton():
        if phoneEntry.get() and tempEntry.get() and distanceEntry.get():
            startButton.configure(state="normal")
        else:
            startButton.configure(state="disabled")
    
    # Initialize GUI window
    root = ctk.CTk()
    root.geometry("400x650")  
    root.title("Poultry Guard")

    # Frame for inputs
    inputFrame = ctk.CTkFrame(root)
    inputFrame.pack(pady=20, padx=20, fill="x")

    # Phone Number Entry
    phoneLabel = ctk.CTkLabel(inputFrame, text="Enter Phone Number:")
    phoneLabel.pack(pady=(10, 5))

    phoneEntry = ctk.CTkEntry(inputFrame, placeholder_text="Phone Number")
    phoneEntry.pack(pady=(0, 10))

    # Status label to display the saved phone number
    savedNumberLabel = ctk.CTkLabel(inputFrame, text="Saved Phone Number: Not set", text_color="white")
    savedNumberLabel.pack(pady=(10, 0))
        
    def setPhoneNumber():
        global phoneNumber
        phoneNumber = phoneEntry.get()
        print(f"Phone Number Set: {phoneNumber}")
        savedNumberLabel.configure(text=f"Saved Phone Number: {phoneNumber}")  
        checkStartButton()

    # Set Phone Number button
    setPhoneButton = ctk.CTkButton(inputFrame, text="Set Phone Number", command=setPhoneNumber)
    setPhoneButton.pack(pady=(0, 20))
    
    def setTemperature():
        global tempThreshold
        tempThreshold = float(tempEntry.get())
        print(f"Temperature threshold: {tempThreshold}")
        tempLabel.configure(text=f"Saved temperature threshold: {tempThreshold}")  
        checkStartButton()

    # Temperature Threshold Entry
    tempEntry = ctk.CTkEntry(inputFrame, placeholder_text="Enter temperature threshold:")
    tempEntry.pack(pady=(0, 10))

    tempLabel = ctk.CTkLabel(inputFrame, text="Saved Temperature: Not set", text_color="white")
    tempLabel.pack(pady=(10, 0))

    setTempButton = ctk.CTkButton(inputFrame, text="Set Temperature", command=setTemperature)
    setTempButton.pack(pady=(0, 20))
    
    # Distance Threshold Entry
    def setDistanceThreshold():
        global distanceThreshold
        distanceThreshold = int(distanceEntry.get())
        print(f"Distance threshold: {distanceThreshold}")
        distanceLabel.configure(text=f"Saved Distance Threshold: {distanceThreshold}")
        checkStartButton()

    distanceEntry = ctk.CTkEntry(inputFrame, placeholder_text="Enter distance threshold:")
    distanceEntry.pack(pady=(0, 10))

    distanceLabel = ctk.CTkLabel(inputFrame, text="Saved Distance Threshold: Not set", text_color="white")
    distanceLabel.pack(pady=(10, 0))

    setDistanceButton = ctk.CTkButton(inputFrame, text="Set Distance Threshold", command=setDistanceThreshold)
    setDistanceButton.pack(pady=(0, 20))

    # Frame for server controls
    controlFrame = ctk.CTkFrame(root)
    controlFrame.pack(pady=10, padx=20, fill="both", expand=True)

    # Start Server button
    startButton = ctk.CTkButton(controlFrame, text="Start Server", command=lambda: startServer(startButton), state='disabled')
    startButton.pack(side="top", padx=(0, 10), pady=(0, 0), expand=True) 

    def onEnter(e):
        arduinoLink.configure(text_color=("#3B8ED0"))  

    def onLeave(e):
        arduinoLink.configure(text_color="white")  

    # Replace CTkLabel with a hoverable link
    arduinoLink = ctk.CTkLabel(controlFrame, text="Click here to view Arduino IoT Cloud Status")
    arduinoLink.pack(pady=(0, 0))
    arduinoLink.bind("<Button-1>", lambda e: openArduinoLink())

    # Bind hover events
    arduinoLink.bind("<Enter>", onEnter)
    arduinoLink.bind("<Leave>", onLeave)

    closeNote = ctk.CTkLabel(controlFrame, text="Close the window to stop the server.", text_color="red")
    closeNote.pack(pady=(0, 0))

    # camera status
    cameraLabel = ctk.CTkLabel(root, text=cameraStatus, text_color="white")
    cameraLabel.pack(pady=(0, 0))
    
    # Status label
    statusLabel = ctk.CTkLabel(root, text="Status: Not connected", text_color="white")
    statusLabel.pack(pady=(0, 0))

    # Function to update status from Arduino
    def updateStatus():    
        global arduinoStatus, gsmStatus
        while True:
            if arduino and arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').rstrip()
                print(line)  # Print to console for debugging

                # Schedule the GUI update in the main thread
                root.after(0, updateGuiStatus, line)

            time.sleep(1)  # Check every second

    # Function to update GUI status safely
    def updateGuiStatus(line):
        global arduinoStatus, gsmStatus
        if "GSM" in line:
            gsmStatus = line.split(':')[-1].strip()
            statusLabel.configure(text=f"GSM Status: {gsmStatus}")
        elif "Arduino" in line:
            arduinoStatus = line.split(':')[-1].strip()
            statusLabel.configure(text=f"Arduino Status: {arduinoStatus}")
        elif "Arduino" in line and "GSM" in line:
            arduinoStatus = "Connected"
            gsmStatus = "Connected"
            statusLabel.configure(text="Status: System Ready")
        else:
            statusLabel.configure(text=f"Status: {line}")

    # Start the status update thread
    statusThread = threading.Thread(target=updateStatus)
    statusThread.daemon = True
    statusThread.start()

    # Run the GUI main loop
    root.mainloop()


if __name__ == '__main__':
    createGui()