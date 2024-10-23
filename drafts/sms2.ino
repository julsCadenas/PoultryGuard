#include <SoftwareSerial.h>

SoftwareSerial sim(10, 11);  // RX, TX for GSM module
int relay = 7;  // Pin for controlling the relay
String phoneNumber; // Store phone number
String message; // Store SMS message
String _buffer;
int _timeout;
bool gsmConnected = false;  // Variable to track GSM connection status
unsigned long previousMillis = 0;  // For timing
const long interval = 5000;  // Interval to check GSM connection (in milliseconds)

void setup() {
  Serial.begin(9600);
  pinMode(relay, OUTPUT);  // Set relay pin as output
  digitalWrite(relay, LOW); // Ensure relay is off initially
  _buffer.reserve(50);
  sim.begin(9600);  // Start the GSM module communication
  delay(7000);  // Wait for the GSM module to connect to the network
  checkGsmConnection();  // Initial check

  // Notify when Arduino is ready if conditions are satisfied
  if (isSystemReady()) {
    Serial.println("Arduino system is ready.");
  } else {
    Serial.println("Arduino system is NOT ready.");
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the incoming serial command

    if (command.startsWith("  :")) {
      int firstColon = command.indexOf(':');
      int secondColon = command.indexOf(':', firstColon + 1);
      phoneNumber = command.substring(firstColon + 1, secondColon);  // Extract phone number
      message = command.substring(secondColon + 1);  // Extract the SMS message
      SendMessage(phoneNumber, message);  // Send the message
    } else if (command == "ON") {
      digitalWrite(relay, HIGH);  // Turn the relay ON
      Serial.println("Relay is ON");
    } else if (command == "OFF") {
      digitalWrite(relay, LOW);  // Turn the relay OFF
      Serial.println("Relay is OFF");
    } else {
      Serial.println("Invalid command. Type 'ON', 'OFF', or 'SMS:<number>:<message>'.");
    }
  }

  if (sim.available() > 0) {
    Serial.write(sim.read());  // Print any GSM module output to Serial for debugging
  }

  // Periodically check GSM connection status
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    checkGsmConnection();
    if (!isSystemReady()) {
      Serial.println("Arduino system is NOT ready.");
    }
  }
}

void SendMessage(String number, String message) {
  Serial.println("Sending SMS...");
  sim.println("AT+CMGF=1");  // Set GSM module to text mode
  delay(200);
  sim.println("AT+CMGS=\"" + number + "\"\r");  // Set the recipient's number
  delay(200);
  sim.println(message);  // Send the actual SMS message
  delay(100);
  sim.println((char)26);  // Send CTRL+Z to indicate the end of the message
  delay(2000);
  _buffer = _readSerial();
  Serial.println(_buffer);  // Print the response from the GSM module for debugging
}

String _readSerial() {
  _timeout = 0;
  while (!sim.available() && _timeout < 12000) {
    delay(13);
    _timeout++;
  }
  if (sim.available()) {
    return sim.readString();  // Read the available data from the GSM module
  }
  return "Timeout: No response";
}

void checkGsmConnection() {
  sim.println("AT");  // Send a test command to the GSM module
  delay(1000);
  _buffer = _readSerial();
  if (_buffer.indexOf("OK") != -1) {
    gsmConnected = true;  // GSM module is connected
  } else {
    gsmConnected = false;  // GSM module is not connected
  }
  Serial.println(gsmConnected ? "GSM module connected." : "GSM module not connected.");
}

bool isSystemReady() {
  return gsmConnected && Serial;  // Add more conditions as needed
}
