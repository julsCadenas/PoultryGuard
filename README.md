# **POULTRYGUARD: Heat Stress Monitoring for Poultry**

## **Project Overview**
POULTRYGUARD is a heat stress monitoring system designed for poultry farms. It uses real-time data collection and analysis to detect heat stress in poultry, allowing farmers to take proactive measures to ensure the health and well-being of their livestock.

## **Team Members**
- Julian Sebastian Cadenas
- Joshua Cormier
- Daryl Guerzon
- Christian Lawrence Javier

## **Features**
- Real-time monitoring of chickens and temperature.
- Heat stress detection based on multiple factors (temperature and isolation).
- Detection of chicken isolation.
- Alerts and notifications for farmers when heat stress levels are critical.

## **Technology**
- Fine-tuned a **YOLOv8n model** using a custom dataset gathered by the researchers.
- **Computer Vision (OpenCV)** used to detect chickens with the aforementioned model.
- **Thermal Imaging** using **OpenCV** and **NumPy**.
- **Python** as the primary programming language.
- **CustomTkinter** for a minimalistic user interface.
- **Arduino IoT Cloud** API for remote microcontroller control.
- **PySerial** for serial communication with microcontrollers.
- **Threading** to improve system performance.
