# **POULTRYGUARD: Heat Stress Monitoring for Poultry**

## **Project Overview**
POULTRYGUARD is a heat stress monitoring system designed for poultry farms. It uses real-time data collection and analysis to detect heat stress in poultry, allowing farmers to take proactive measures to ensure the health and well-being of their livestock.

## **Team Members**
- Julian Sebastian Cadenas | [LinkedIn](https://www.linkedin.com/in/julian-cadenas/) | [GitHub](https://github.com/julsCadenas)
- Joshua Cormier | [LinkedIn](https://www.linkedin.com/in/joshua-cormier-613802328/) | [GitHub](https://github.com/Tetsuii)
- Daryl Guerzon | [LinkedIn](https://www.linkedin.com/in/daryl-guerzon-0a980b212/) | [GitHub](https://github.com/ChristianLFJ)
- Christian Lawrence Javier | [LinkedIn](https://www.linkedin.com/in/christianlawrencejavier/) | [GitHub](https://github.com/DarealGuerzon)

## **Features**
- Real-time monitoring of chickens.
- Real-time monitoring of the temperature of each chicken.
- Heat stress detection based on multiple factors (temperature and isolation).
- Detection of chicken isolation.
- Alerts and notifications for farmers when heat stress levels are critical.
- Automated cooling system for the farm.
- Monitor the chickens through the website.

## **Technology**
- **Python** as the primary programming language.
- Fine-tuned a **YOLOv8n model** using a custom dataset collected by the researchers.
- **Computer Vision (OpenCV)** used to detect chickens with the model.
- **Thermal Imaging** using **OpenCV** and **NumPy**.
- **Flask** as the web server to serve the model and web interface.
- **CustomTkinter** for a modern & minimalist user interface.
- **Arduino IoT Cloud** for remote microcontroller control.
- **PySerial** for serial communication with microcontrollers.
- **Threading** to improve system performance.

## **Materials Used**
- Lenovo ThinkCentre M75q Gen2 Mini PC
- ESP32 Development Board
- Logitech C270 HD Webcam
- Mileseey TR160i Thermal Camera
- 5V Relay Module
- Sim800L v2 Board
- Buzzer
