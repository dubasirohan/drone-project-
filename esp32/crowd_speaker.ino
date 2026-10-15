/*
 * crowd_speaker.ino — ESP32 Wireless Audio Receiver & Crowd Management Unit
 * 
 * Hardware Connections:
 *   - Audio DAC Output: GPIO 25 (Built-in DAC Channel 1) -> Audio Amplifier / Speaker Module (e.g. PAM8403 / LM386)
 *   - Physical Push Button: GPIO 14 (Active LOW with internal pull-up) -> Push button to GND
 *   - Ground: Connect ESP32 GND to Amplifier GND and Button GND
 * 
 * Wi-Fi & Network Configuration:
 *   - Connects as Wi-Fi Station to your Mobile Hotspot ("TPhone")
 *   - Connects as TCP Client to Laptop IP at Port 8002
 *   - Automatically reconnects if Wi-Fi or TCP server connection drops
 */

#include <Arduino.h>
#include <WiFi.h>

// ============================================================
// CONFIGURATION
// ============================================================

// 1. Wi-Fi credentials (Mobile Hotspot)
const char* WIFI_SSID     = "TPhone";
const char* WIFI_PASSWORD = "123tej247";

// 2. Laptop IP address on the Mobile Hotspot network
// Find this on the laptop by looking at the Dashboard header or running 'ipconfig'
const char* LAPTOP_IP     = "172.20.10.5"; 
const uint16_t SERVER_PORT = 8002;

// 3. Hardware Pins
const int BUTTON_PIN = 14;   // Physical emergency / trigger button on GPIO 14 (active LOW)
const int DAC_PIN    = 25;   // Built-in DAC channel 1 on GPIO 25

// Audio Constants
const uint32_t SAMPLE_RATE       = 8000;
const uint8_t  MAGIC_1           = 0xA5;
const uint8_t  MAGIC_2           = 0x5A;
const uint32_t MAX_AUDIO_SIZE    = 300000;
const int      AUDIO_BUFFER_SIZE = 2048;

uint8_t audioBuffer[AUDIO_BUFFER_SIZE];

// TCP Client connection to laptop
WiFiClient client;

// Button debounce tracking
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 250; // ms


// ============================================================
// PLAY AUDIO BUFFER THROUGH DAC (Exact prototype timing)
// ============================================================

void playBuffer(uint8_t *buffer, int length) {
  const uint32_t samplePeriod = 1000000UL / SAMPLE_RATE; // 125 microseconds per sample
  uint32_t nextSampleTime = micros();

  for (int i = 0; i < length; i++) {
    while ((int32_t)(micros() - nextSampleTime) < 0) {
      // Precise microsecond wait for 8 kHz playback
    }
    dacWrite(DAC_PIN, buffer[i]);
    nextSampleTime += samplePeriod;
  }
}


// ============================================================
// READ EXACT BYTES FROM TCP STREAM
// ============================================================

bool readExactTcp(uint8_t *buffer, size_t length, uint32_t timeoutMs) {
  size_t received = 0;
  unsigned long lastByteTime = millis();

  while (received < length) {
    if (client.available() > 0) {
      buffer[received] = client.read();
      received++;
      lastByteTime = millis();
    } else {
      if (!client.connected()) return false;
      if (millis() - lastByteTime > timeoutMs) return false;
      delay(1);
    }
  }
  return true;
}


// ============================================================
// RECEIVE & PLAY AUDIO STREAM OVER WI-FI
// ============================================================

bool receiveAndPlayAudio(uint32_t audioLength) {
  uint32_t bytesRemaining = audioLength;
  Serial.printf("[Audio] Receiving and playing %u bytes through DAC...\n", audioLength);

  while (bytesRemaining > 0) {
    int chunkSize = min((uint32_t)AUDIO_BUFFER_SIZE, bytesRemaining);

    if (!readExactTcp(audioBuffer, chunkSize, 15000)) {
      Serial.println("[Audio] TCP Receive Error!");
      return false;
    }

    playBuffer(audioBuffer, chunkSize);
    bytesRemaining -= chunkSize;
  }

  // Center DAC to silence (128)
  dacWrite(DAC_PIN, 128);
  Serial.println("[Audio] Playback Complete.");
  return true;
}


// ============================================================
// CONNECT TO WI-FI & TCP SERVER
// ============================================================

void ensureWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;

  Serial.print("[WiFi] Connecting to: ");
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(400);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected!");
    Serial.print("[WiFi] ESP32 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WiFi] Connection failed. Retrying...");
  }
}

void ensureServerConnection() {
  if (client.connected()) return;

  ensureWiFi();
  if (WiFi.status() != WL_CONNECTED) return;

  Serial.printf("[TCP] Connecting to Laptop at %s:%d...\n", LAPTOP_IP, SERVER_PORT);
  if (client.connect(LAPTOP_IP, SERVER_PORT)) {
    Serial.println("[TCP] Connected to Laptop Audio & Crowd Management Server!");
    client.print("ESP32_READY\n");
    client.flush();
  } else {
    Serial.println("[TCP] Connect failed. Will retry in loop.");
    delay(1000);
  }
}


// ============================================================
// SETUP
// ============================================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=============================================");
  Serial.println("  Drone Crowd Management ESP32 Speaker Unit  ");
  Serial.println("  DAC Pin: GPIO 25 | Button Pin: GPIO 14     ");
  Serial.println("=============================================");

  // Initialize button pin with internal pull-up
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Initialize DAC to center silence (128)
  dacWrite(DAC_PIN, 128);

  // Connect to Wi-Fi and Server
  ensureWiFi();
  ensureServerConnection();
}


// ============================================================
// MAIN LOOP
// ============================================================

void loop() {
  // 1. Maintain Wi-Fi and TCP connection to Laptop
  if (!client.connected()) {
    ensureServerConnection();
    delay(500);
    return;
  }

  // 2. Check Physical Button (Active LOW)
  int reading = digitalRead(BUTTON_PIN);
  if (reading == LOW && lastButtonState == HIGH && (millis() - lastDebounceTime) > debounceDelay) {
    lastDebounceTime = millis();
    Serial.println("[Button] Physical button pressed! Sending BTN event...");
    client.print("BTN\n");
    client.flush();
  }
  lastButtonState = reading;

  // 3. Check for Incoming Audio from Laptop (Magic Bytes 0xA5 0x5A)
  if (client.available() >= 6) {
    uint8_t b1 = client.read();
    if (b1 == MAGIC_1) {
      uint8_t b2 = client.read();
      if (b2 == MAGIC_2) {
        // Read 4-byte Little-Endian audio length
        uint8_t lenBytes[4];
        if (readExactTcp(lenBytes, 4, 3000)) {
          uint32_t audioLen = ((uint32_t)lenBytes[0]) |
                              ((uint32_t)lenBytes[1] << 8) |
                              ((uint32_t)lenBytes[2] << 16) |
                              ((uint32_t)lenBytes[3] << 24);

          if (audioLen > 0 && audioLen <= MAX_AUDIO_SIZE) {
            client.print("RECEIVING\n");
            client.flush();

            bool ok = receiveAndPlayAudio(audioLen);
            if (ok) {
              client.print("DONE\n");
              client.flush();
            } else {
              client.print("RECEIVE_ERROR\n");
              client.flush();
            }
          }
        }
      }
    }
  }

  delay(5);
}
