int relay = 7;  // Pin for controlling the relay

void setup() {
  Serial.begin(9600);
  pinMode(relay, OUTPUT);  // Set relay pin as output
  digitalWrite(relay, LOW); // Ensure relay is off initially

  // Notify when Arduino is ready
  if (isSystemReady()) {
    Serial.println("Arduino system is ready.");
  } else {
    Serial.println("Arduino system is NOT ready.");
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');  // Read the incoming serial command

    if (command == "1") {
      digitalWrite(relay, HIGH);  // Turn the relay ON
      Serial.println("Relay is ON");
    } else if (command == "0") {
      digitalWrite(relay, LOW);  // Turn the relay OFF
      Serial.println("Relay is OFF");
    } else {
      Serial.println("Invalid command. Type '1' to turn ON or '0' to turn OFF.");
    }
  }
}

// Function to check if the Arduino system is ready
bool isSystemReady() {
  return Serial;  // Can add more conditions as needed
}
