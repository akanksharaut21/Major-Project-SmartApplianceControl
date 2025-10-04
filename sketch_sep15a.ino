#include <WiFi.h>
#include <WebServer.h>

// ---------------- WiFi Credentials ----------------
const char* ssid = "vivo T3x 5G";
const char* password = "VaiLa2003@";

// ---------------- Device Pins ----------------
// External LED connected to GPIO 4
const int ledPin = 4;    // Light
const int fanPin = 5;    // Fan
const int tvPin = 18;    // TV
const int acPin = 19;    // AC

WebServer server(80);

// ---------------- Helper to control devices ----------------
void setDevice(int pin, bool state) {
  digitalWrite(pin, state ? HIGH : LOW);
}

// ---------------- HTTP Handlers ----------------
void handleDevice(String device, bool state) {
  if (device == "led") setDevice(ledPin, state);
  else if (device == "fan") setDevice(fanPin, state);
  else if (device == "tv") setDevice(tvPin, state);
  else if (device == "ac") setDevice(acPin, state);

  server.send(200, "text/plain", device + (state ? " ON" : " OFF"));
}

void setup() {
  Serial.begin(115200);

  // Initialize pins
  pinMode(ledPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(tvPin, OUTPUT);
  pinMode(acPin, OUTPUT);

  // Turn all devices OFF initially
  setDevice(ledPin, false);
  setDevice(fanPin, false);
  setDevice(tvPin, false);
  setDevice(acPin, false);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // ---------------- Define HTTP Endpoints ----------------
  // LED
  server.on("/led/on",  [](){ handleDevice("led", true); });
  server.on("/led/off", [](){ handleDevice("led", false); });

  // Fan
  server.on("/fan/on",  [](){ handleDevice("fan", true); });
  server.on("/fan/off", [](){ handleDevice("fan", false); });

  // TV
  server.on("/tv/on",   [](){ handleDevice("tv", true); });
  server.on("/tv/off",  [](){ handleDevice("tv", false); });

  // AC
  server.on("/ac/on",   [](){ handleDevice("ac", true); });
  server.on("/ac/off",  [](){ handleDevice("ac", false); });

  // All devices OFF
  server.on("/all/off", [](){
    setDevice(ledPin, false);
    setDevice(fanPin, false);
    setDevice(tvPin, false);
    setDevice(acPin, false);
    server.send(200, "text/plain", "All devices OFF");
  });

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}