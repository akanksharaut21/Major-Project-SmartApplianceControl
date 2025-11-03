#include <WiFi.h>
#include <WebServer.h>

// ✅ WiFi credentials
const char* ssid = "vivo T3x 5G";
const char* password = "VaiLa2003@";

// ✅ Relay pin setup
const int lightRelay = 18;   // IN1 → Bulb
const int fanRelay   = 14;  // IN2 → Fan

WebServer server(80);

// ========== HANDLERS ==========

// Root route
void handleRoot() {
  server.send(200, "text/plain", "ESP32 Smart Control Server Running");
}

// Light ON/OFF
void handleLightOn() {
  digitalWrite(lightRelay, LOW);   // Active LOW relay: LOW = ON
  server.send(200, "text/plain", "Light ON");
  Serial.println("Light turned ON");
}
void handleLightOff() {
  digitalWrite(lightRelay, HIGH);  // HIGH = OFF
  server.send(200, "text/plain", "Light OFF");
  Serial.println("Light turned OFF");
}

// Fan ON/OFF
void handleFanOn() {
  digitalWrite(fanRelay, LOW);
  server.send(200, "text/plain", "Fan ON");
  Serial.println("Fan turned ON");
}
void handleFanOff() {
  digitalWrite(fanRelay, HIGH);
  server.send(200, "text/plain", "Fan OFF");
  Serial.println("Fan turned OFF");
}

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);

  pinMode(lightRelay, OUTPUT);
  pinMode(fanRelay, OUTPUT);

  digitalWrite(lightRelay, HIGH);  // Keep OFF initially
  digitalWrite(fanRelay, HIGH);

  Serial.print("Connecting to WiFi ");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connected! ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Routes
  server.on("/", handleRoot);
  server.on("/light/on", handleLightOn);
  server.on("/light/off", handleLightOff);
  server.on("/fan/on", handleFanOn);
  server.on("/fan/off", handleFanOff);

  server.begin();
  Serial.println("HTTP server started");
}

// ========== LOOP ==========
void loop() {
  server.handleClient();
}
