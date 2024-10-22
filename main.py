import threading
import customtkinter as ctk
import cv2
import time
import webbrowser
import serial
from ultralytics import YOLO
from flask import Flask, render_template, Response
import subprocess
import sys

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

try:
    arduino = serial.Serial('COM8', 9600, timeout=1)
    time.sleep(2)  # Wait for the connection to establish
except serial.SerialException as e:
    print(f"Error: Could not open serial port: {e}")
    arduino = None

# Global variable to store the phone number
phoneNumber = ""

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webcam_feed')
def webcam_feed():
    return Response(webcamStream(webcam, model, thermalCamera, arduino, phoneNumber, distanceThreshold=300),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/thermal_feed')
def thermal_feed():
    return Response(thermalStream(webcam, thermalCamera, model),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Flask server control in a separate thread
def run_flask():
    # Start a new terminal and run the Flask app
    subprocess.Popen([sys.executable, '-m', 'flask', 'run', '--host=0.0.0.0', '--port=5000'], shell=True)
    print("Server started")

# Start the server in a thread
server_thread = None

def start_server():
    global server_thread
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=run_flask)
        server_thread.daemon = True
        server_thread.start()

def open_arduino_link():
    webbrowser.open("https://id.arduino.cc/?iss=https%3A%2F%2Flogin.arduino.cc%2F#/sso/login")

# Create GUI with customtkinter
def create_gui():
    ctk.set_appearance_mode("dark")  # "system", "dark", "light"
    ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

    # Initialize GUI window
    root = ctk.CTk()
    root.geometry("400x300")
    root.title("Poultry Guard")

    # Frame for inputs
    input_frame = ctk.CTkFrame(root)
    input_frame.pack(pady=20, padx=20, fill="x")

    # Phone Number Entry
    phone_label = ctk.CTkLabel(input_frame, text="Enter Phone Number:")
    phone_label.pack(pady=(10, 5))

    phone_entry = ctk.CTkEntry(input_frame, placeholder_text="Phone Number")
    phone_entry.pack(pady=(0, 10))

    def set_phone_number():
        global phoneNumber
        phoneNumber = phone_entry.get()
        print(f"Phone Number Set: {phoneNumber}")

    # Set Phone Number button
    set_phone_button = ctk.CTkButton(input_frame, text="Set Phone Number", command=set_phone_number)
    set_phone_button.pack(pady=(0, 20))

    # Frame for server controls
    control_frame = ctk.CTkFrame(root)
    control_frame.pack(pady=10, padx=20, fill="both", expand=True)

    # Start Server button
    start_button = ctk.CTkButton(control_frame, text="Start Server", command=start_server)
    start_button.pack(side="top", padx=(0, 10), pady=(0, 0), expand=True) 

    def on_enter(e):
        arduino_link.configure(text_color=("#3B8ED0"))  # Button color

    def on_leave(e):
        arduino_link.configure(text_color="white")  # Reset to label's default

    # Replace CTkLabel with a hoverable link
    arduino_link = ctk.CTkLabel(control_frame, text="Click here to view Arduino IoT Cloud Status")
    arduino_link.pack(pady=(0, 0))
    arduino_link.bind("<Button-1>", lambda e: open_arduino_link())

    # Bind hover events
    arduino_link.bind("<Enter>", on_enter)
    arduino_link.bind("<Leave>", on_leave)

    close_note = ctk.CTkLabel(control_frame, text="Close the window to stop the server.", text_color="red")
    close_note.pack(pady=(0, 0))

    # Run the GUI main loop
    root.mainloop()

if __name__ == '__main__':
    create_gui()
