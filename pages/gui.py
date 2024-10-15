import customtkinter as ctk
import threading
import subprocess
import os

server_process = None

# Function to start the Flask server in a new thread
def start_server():
    global server_process
    if server_process is None:
        # Start the Flask server using a subprocess
        server_process = subprocess.Popen(
            ["python", "main.py"],
            shell=True
        )

# Function to stop the Flask server on Windows
def stop_server():
    global server_process
    if server_process:
        # Use taskkill to terminate the process and its subprocesses on Windows
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(server_process.pid)])
        server_process = None

# Create the custom tkinter GUI window
def create_gui():
    # Set appearance and theme
    ctk.set_appearance_mode("dark")  # Options: "dark", "light", "system"
    ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

    # Initialize the window
    root = ctk.CTk()
    root.title("PoultrGuard")
    root.geometry("400x200")

    # Create a label
    label = ctk.CTkLabel(root, text="Heat Stress Monitoring", font=("Arial", 16))
    label.pack(pady=20)

    # Start Server Button
    start_button = ctk.CTkButton(root, text="Start Server", command=lambda: threading.Thread(target=start_server).start(), width=200, height=40)
    start_button.pack(pady=10)

    # Stop Server Button
    stop_button = ctk.CTkButton(root, text="Stop Server", command=stop_server, width=200, height=40)
    stop_button.pack(pady=10)

    # Run the GUI loop
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
