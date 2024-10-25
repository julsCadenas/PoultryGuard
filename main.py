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

# Initialize the Flask server
app = Flask(__name__)

# Import the model
modelPath = "C:/Users/Juls/Desktop/finaldraft/models/etian35.pt"
model = YOLO(modelPath)
names = model.model.names

# Set the cameras
webcam = cv2.VideoCapture(1)
thermalCamera = cv2.VideoCapture(0)

phoneNumber = ""
arduino_status = "Not connected"
gsm_status = "Not connected"
tempThreshold = 35

server_thread = None

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
    return Response(webcamStream(webcam, model, thermalCamera, arduino, phoneNumber, tempThreshold, distanceThreshold=300),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/thermal_feed')
def thermal_feed():
    return Response(thermalStream(webcam, thermalCamera, model),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    return jsonify({
        'phoneNumber': phoneNumber,
        'arduinoStatus': arduino_status,
        'gsmStatus': gsm_status
    })

# Flask server control in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)


def start_server():
    global server_thread
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=run_flask)
        server_thread.daemon = True
        server_thread.start()
        print('Server started')
        time.sleep(1)  
        webbrowser.open("http://localhost:5000")

def open_arduino_link():
    webbrowser.open("https://id.arduino.cc/?iss=https%3A%2F%2Flogin.arduino.cc%2F#/sso/login")

# Create GUI with customtkinter
def create_gui():
    ctk.set_appearance_mode("dark")  # "system", "dark", "light"
    ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

    # Initialize GUI window
    root = ctk.CTk()
    root.geometry("400x500")  
    root.title("Poultry Guard")

    # Frame for inputs
    input_frame = ctk.CTkFrame(root)
    input_frame.pack(pady=20, padx=20, fill="x")

    # Phone Number Entry
    phone_label = ctk.CTkLabel(input_frame, text="Enter Phone Number:")
    phone_label.pack(pady=(10, 5))

    phone_entry = ctk.CTkEntry(input_frame, placeholder_text="Phone Number")
    phone_entry.pack(pady=(0, 10))

    # Status label to display the saved phone number
    saved_number_label = ctk.CTkLabel(input_frame, text="Saved Phone Number: Not set", text_color="white")
    saved_number_label.pack(pady=(10, 0))
        
    def set_phone_number():
        global phoneNumber
        phoneNumber = phone_entry.get()
        print(f"Phone Number Set: {phoneNumber}")
        saved_number_label.configure(text=f"Saved Phone Number: {phoneNumber}")  

    # Set Phone Number button
    set_phone_button = ctk.CTkButton(input_frame, text="Set Phone Number", command=set_phone_number)
    set_phone_button.pack(pady=(0, 20))
    
    def setTemperature():
        global tempThreshold
        tempThreshold = float(tempEntry.get())
        print(f"Temperature threshold: {tempThreshold}")
        temp_label.configure(text=f"Saved temperature threshold: {tempThreshold}")  

    tempEntry = ctk.CTkEntry(input_frame, placeholder_text="Enter temperature threshold:")
    tempEntry.pack(pady=(0, 10))

    temp_label = ctk.CTkLabel(input_frame, text="Saved Temperature: Not set", text_color="white")
    temp_label.pack(pady=(10, 0))

    setTempButton = ctk.CTkButton(input_frame, text="Set Temperature", command=setTemperature)
    setTempButton.pack(pady=(0, 20))
    
    # Frame for server controls
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Start Server button
    start_button = ctk.CTkButton(control_frame, text="Start Server", command=start_server)
    start_button.pack(side="top", padx=(0, 10), pady=(0, 0), expand=True) 

    def on_enter(e):
        arduino_link.configure(text_color=("#3B8ED0"))  

    def on_leave(e):
        arduino_link.configure(text_color="white")  

    # Replace CTkLabel with a hoverable link
    arduino_link = ctk.CTkLabel(control_frame, text="Click here to view Arduino IoT Cloud Status")
    arduino_link.pack(pady=(0, 0))
    arduino_link.bind("<Button-1>", lambda e: open_arduino_link())

    # Bind hover events
    arduino_link.bind("<Enter>", on_enter)
    arduino_link.bind("<Leave>", on_leave)

    close_note = ctk.CTkLabel(control_frame, text="Close the window to stop the server.", text_color="red")
    close_note.pack(pady=(0, 0))

    # Status label
    status_label = ctk.CTkLabel(root, text="Status: Not connected", text_color="white")
    status_label.pack(pady=(10, 0))

    # Function to update status from Arduino
    def update_status():    
        global arduino_status, gsm_status
        while True:
            if arduino and arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').rstrip()
                print(line)  # Print to console for debugging

                # Schedule the GUI update in the main thread
                root.after(0, update_gui_status, line)

            time.sleep(1)  # Check every second

    # Function to update GUI status safely
    def update_gui_status(line):
        global arduino_status, gsm_status
        if "GSM" in line:
            gsm_status = line.split(':')[-1].strip()
            status_label.configure(text=f"GSM Status: {gsm_status}")
        elif "Arduino" in line:
            arduino_status = line.split(':')[-1].strip()
            status_label.configure(text=f"Arduino Status: {arduino_status}")
        elif "Arduino" in line and "GSM" in line:
            arduino_status = "Connected"
            gsm_status = "Connected"
            status_label.configure(text="Status: System Ready")
        else:
            status_label.configure(text=f"Status: {line}")

    # Start the status update thread
    status_thread = threading.Thread(target=update_status)
    status_thread.daemon = True
    status_thread.start()

    # Run the GUI main loop
    root.mainloop()

if __name__ == '__main__':
    create_gui()