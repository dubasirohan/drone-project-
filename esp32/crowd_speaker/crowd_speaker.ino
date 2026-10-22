/*
 * homework_robot.ino — Wireless ESP32 Crowd Management & Audio Receiver Unit
 * Configured for PAM8403 Analog Audio Amplifier & 5Ω Speaker.
 * 
 * Hardware Connections:
 *   - Audio: ESP32 GPIO 25 (DAC) -> PAM8403 L_IN (Left Input)
 *   - Ground: ESP32 GND -> PAM8403 GND (Power GND and Audio G)
 *   - Power: ESP32 VIN (5V USB) -> PAM8403 +5V
 *   - Speaker: 5Ω Speaker across PAM8403 L+ and L-
 *   - Button: Push Button between GPIO 14 and GND
 */

#include <Arduino.h>
#include <WiFi.h>

// ============================================================
// CONFIGURATION
// ============================================================

// 1. Wi-Fi credentials (Mobile Hotspot)
const char* WIFI_SSID     = "TPhone";
const char* WIFI_PASSWORD = "123tej247";

// 2. Laptop IP address on the Wi-Fi Hotspot network
const char* LAPTOP_IP     = "172.20.10.2"; 
const uint16_t SERVER_PORT = 8002;

// 3. Hardware Pins
const int BUTTON_PIN = 14;   // Physical capture button on GPIO 14 (active LOW)
const int DAC_PIN    = 25;   // Built-in DAC channel 1 on GPIO 25 -> PAM8403 L_IN

// Audio Constants matching laptop server
const uint32_t SAMPLE_RATE      = 8000;
const uint8_t  MAGIC_1          = 0xA5;
const uint8_t  MAGIC_2          = 0x5A;
const uint32_t MAX_AUDIO_SIZE   = 300000;
const int      AUDIO_BUFFER_SIZE = 512;

uint8_t audioBuffer[AUDIO_BUFFER_SIZE];

// TCP Client connection to laptop
WiFiClient client;

// Button debounce tracking
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 250; // ms


// ============================================================
// PLAY AUDIO BUFFER THROUGH DAC (Exact 8 kHz timing)
// ============================================================

void playBuffer(uint8_t *buffer, int length) {
  const uint32_t samplePeriod = 1000000UL / SAMPLE_RATE;
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
    int avail = client.available();
    if (avail > 0) {
      size_t toRead = min((size_t)avail, length - received);
      int bytesRead = client.read(buffer + received, toRead);
      if (bytesRead > 0) {
        received += bytesRead;
        lastByteTime = millis();
      }
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
  Serial.printf("[Audio] Receiving and playing %u bytes...\n", audioLength);

  while (bytesRemaining > 0) {
    int chunkSize = min((uint32_t)AUDIO_BUFFER_SIZE, bytesRemaining);

    if (!readExactTcp(audioBuffer, chunkSize, 15000)) {
      Serial.println("[Audio] TCP Receive Error!");
      return false;
    }

    playBuffer(audioBuffer, chunkSize);
    bytesRemaining -= chunkSize;
  }

  // Center DAC to silence
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
    Serial.println("[TCP] Connected to Laptop Audio & Button Server!");
    client.print("ESP32_READY\n");
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
  Serial.println("  Wireless Homework Robot ESP32 Starting...  ");
  Serial.println("=============================================");

  // Initialize button pin with internal pull-up
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Initialize DAC to center silence (128)
  dacWrite(DAC_PIN, 128);

  // Connect to Wi-Fi
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
