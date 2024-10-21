#include <SoftwareSerial.h>
SoftwareSerial sim(10, 11);  // RX, TX for GSM module
int relay = 7;  // Pin for controlling the relay
String number = "+639089367868"; // Change with your number
String _buffer;
int _timeout;

void setup() {
  Serial.begin(9600);
  pinMode(relay, OUTPUT);  // Set relay pin as output
  digitalWrite(relay, LOW); // Ensure relay is off initially
  _buffer.reserve(50);
  sim.begin(9600);  // Start the GSM module communication
  delay(7000);  // Wait for the GSM module to connect to the network
  Serial.println("System Ready");
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the incoming serial command

    if (command.startsWith("SMS:")) {
      String message = command.substring(4);  // Extract the SMS message
      SendMessage(message);  // Send the message
    } else if (command == "ON") {
      digitalWrite(relay, HIGH);  // Turn the relay ON
      Serial.println("Relay is ON");
    } else if (command == "OFF") {
      digitalWrite(relay, LOW);  // Turn the relay OFF
      Serial.println("Relay is OFF");
    } else {
      Serial.println("Invalid command. Type 'ON', 'OFF', or 'SMS:<message>'.");
    }
  }

  if (sim.available() > 0) {
    Serial.write(sim.read());  // Print any GSM module output to Serial for debugging
  }
}

void SendMessage(String message) {
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
