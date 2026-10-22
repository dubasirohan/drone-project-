"""
src/esp32_manager.py — Wireless TCP Bridge & Crowd Management Audio Synthesizer for ESP32.

Hardware Configuration:
  - ESP32 DAC Pin: GPIO 25 (Built-in 8-bit DAC Channel 1)
  - ESP32 Button Pin: GPIO 14 (Active LOW with internal pull-up)
  - Audio Spec: 8000 Hz sample rate, 8-bit unsigned PCM (0..255, silence = 128)
  - Header Protocol: 0xA5 0x5A + uint32_t little-endian audio byte length

Crowd Management Audio Signals:
  1. Synthetic Tones (Zero latency, 100% offline, pure Python math):
     - Siren: Frequency sweep (500Hz -> 1200Hz wail)
     - Chime: Two-tone attention bell (880Hz -> 587Hz with exponential decay)
     - Alarm: Alternating high-low horn (950Hz / 700Hz)
     - Beep: Rapid warning pulses
  2. Voice Announcements (Text-to-Speech via gTTS + FFmpeg resampler):
     - Disperse: "Attention: Please clear the walkway and move forward."
     - Warning: "Caution: High crowd density detected in this sector."
     - Evacuate: "Emergency alert: Please proceed calmly to the nearest exit."
     - Custom: Operator-typed dynamic voice messages in multiple languages.
"""

import asyncio
from datetime import datetime, timezone
from io import BytesIO
import os
import re
import socket
import struct
import subprocess
<<<<<<< Updated upstream
=======
import sys
>>>>>>> Stashed changes
import threading
import time
from typing import Callable, Optional

import numpy as np

<<<<<<< Updated upstream
=======
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

>>>>>>> Stashed changes
# Protocol Constants matching ESP32 firmware
ESP32_TCP_PORT = 8002
SAMPLE_RATE = 8000
MAGIC_HEADER = b"\xA5\x5A"
MAX_AUDIO_SIZE = 300000


<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
# ── Synthetic Tones Generation (Offline & Low Latency) ─────────────────

def generate_siren_pcm(duration: float = 3.0) -> bytes:
    """Generate sweeping emergency siren tone (500Hz -> 1200Hz)."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    f0, f1 = 500.0, 1200.0
    # 2 Hz modulation cycle
    mod = (np.sin(2 * np.pi * 2.0 * t - np.pi / 2) + 1) / 2.0
    inst_freq = f0 + (f1 - f0) * mod
    phase = 2 * np.pi * np.cumsum(inst_freq) / SAMPLE_RATE
    siren = 128 + 120 * np.sin(phase)
    return siren.astype(np.uint8).tobytes()


def generate_chime_pcm() -> bytes:
    """Generate two-tone pleasant attention chime (880Hz -> 587Hz ding-dong)."""
    # Tone 1: 880Hz (A5) for 0.35s
    t1 = np.linspace(0, 0.35, int(SAMPLE_RATE * 0.35), endpoint=False)
    env1 = np.exp(-5 * t1)
    tone1 = 128 + 115 * env1 * np.sin(2 * np.pi * 880 * t1)

    # Tone 2: 587Hz (D5) for 0.65s
    t2 = np.linspace(0, 0.65, int(SAMPLE_RATE * 0.65), endpoint=False)
    env2 = np.exp(-3.5 * t2)
    tone2 = 128 + 115 * env2 * np.sin(2 * np.pi * 587 * t2)

    chime = np.concatenate([tone1, tone2])
    return chime.astype(np.uint8).tobytes()


def generate_alarm_pcm(duration: float = 3.0) -> bytes:
    """Generate alternating high-low urgent evacuation horn (950Hz / 700Hz)."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = np.where((t % 0.4) < 0.2, 950.0, 700.0)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    alarm = 128 + 120 * np.sin(phase)
    return alarm.astype(np.uint8).tobytes()


def generate_beep_pcm(count: int = 3) -> bytes:
    """Generate rapid warning beeps."""
    chunk_list = []
    t_beep = np.linspace(0, 0.15, int(SAMPLE_RATE * 0.15), endpoint=False)
    beep = 128 + 120 * np.sin(2 * np.pi * 900 * t_beep)
    silence = np.full(int(SAMPLE_RATE * 0.1), 128, dtype=np.uint8)

    for _ in range(count):
        chunk_list.append(beep.astype(np.uint8))
        chunk_list.append(silence)

    full = np.concatenate(chunk_list)
    return full.tobytes()


<<<<<<< Updated upstream
# ── Text-To-Speech to ESP32 DAC PCM Resampler ────────────────────────
=======
# ── Text Translation & Text-To-Speech to ESP32 DAC ────────────────────

COMMON_PHRASES = {
    "hi": {
        "hello": "नमस्ते",
        "hi": "नमस्ते",
        "hey": "नमस्ते",
        "greetings": "नमस्ते",
        "stop": "कृपया रुकिए",
        "warning": "चेतावनी",
        "danger": "खतरा",
        "attention": "कृपया ध्यान दें",
        "attention please": "कृपया ध्यान दें",
        "disperse": "कृपया बिखर जाएं",
        "evacuate": "कृपया तुरंत बाहर निकलें",
        "move": "कृपया आगे बढ़ें",
        "move forward": "कृपया आगे बढ़ें",
        "please move forward": "कृपया आगे बढ़ें",
        "clear the walkway": "कृपया रास्ता साफ़ करें",
        "clear the road": "कृपया रास्ता साफ़ करें",
        "please clear the walkway": "कृपया पैदल रास्ता साफ़ करें",
    },
    "te": {
        "hello": "నమస్కారం",
        "hi": "నమస్కారం",
        "hey": "నమస్కారం",
        "stop": "దయచేసి ఆగండి",
        "warning": "హెచ్చరిక",
        "attention": "దయచేసి గమనించండి",
        "attention please": "దయచేసి గమనించండి",
        "disperse": "దయచేసి వెళ్ళిపోండి",
        "move": "దయచేసి ముందుకు సాగండి",
        "move forward": "దయచేసి ముందుకు సాగండి",
        "please move forward": "దయచేసి ముందుకు సాగండి",
        "clear the walkway": "దయచేసి నడక మార్గాన్ని క్లియర్ చేయండి",
    },
    "ta": {
        "hello": "வணக்கம்",
        "hi": "வணக்கம்",
        "hey": "வணக்கம்",
        "stop": "நில்லுங்கள்",
        "warning": "எச்சரிக்கை",
        "attention": "கவனிக்கவும்",
        "attention please": "கவனிக்கவும்",
        "disperse": "கலைந்து செல்லுங்கள்",
        "move": "முன்னோக்கி செல்லவும்",
        "move forward": "முன்னோக்கி செல்லவும்",
        "clear the walkway": "பாதையை அழிக்கவும்",
    },
    "mr": {
        "hello": "नमस्कार",
        "hi": "नमस्कार",
        "stop": "कृपया थांबा",
        "warning": "इशारा",
        "attention": "कृपया लक्ष द्या",
        "move": "कृपया पुढे चला",
        "move forward": "कृपया पुढे चला",
    },
    "bn": {
        "hello": "নমস্কার",
        "hi": "নমস্কার",
        "stop": "থামুন",
        "warning": "সতর্কতা",
        "attention": "অনুগ্রহ করে শুনুন",
        "move": "সামনে এগিয়ে যান",
        "move forward": "সামনে এগিয়ে যান",
    },
    "fr": {
        "hello": "Bonjour",
        "hi": "Salut",
        "stop": "Arrêtez-vous",
        "warning": "Attention",
        "disperse": "Veuillez vous disperser",
        "move forward": "Veuillez avancer",
        "clear the walkway": "Veuillez dégager le passage",
    }
}

MYMEMORY_LANG_MAP = {
    "hi": "hi-IN",
    "te": "te-IN",
    "ta": "ta-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "fr": "fr-FR",
    "es": "es-ES",
    "de": "de-DE",
}


def translate_text(text: str, target_lang: str) -> str:
    """Translate operator English input to target language."""
    if not text or target_lang == "en":
        return text

    t_clean = text.lower().strip().rstrip(".!?")

    # 1. Check local dictionary for fast, accurate crowd phrases
    if target_lang in COMMON_PHRASES and t_clean in COMMON_PHRASES[target_lang]:
        translated = COMMON_PHRASES[target_lang][t_clean]
        print(f"[esp32_manager] Dictionary translation: '{text}' -> '{translated}' ({target_lang})")
        return translated

    # 2. Use MyMemoryTranslator for arbitrary sentences
    try:
        from deep_translator import MyMemoryTranslator
        target_tag = MYMEMORY_LANG_MAP.get(target_lang, f"{target_lang}-IN")
        res = MyMemoryTranslator(source="en-US", target=target_tag).translate(text)
        if res and res.strip():
            print(f"[esp32_manager] MyMemory translation: '{text}' -> '{res.strip()}' ({target_lang})")
            return res.strip()
    except Exception as exc:
        print(f"[esp32_manager] MyMemory translation error: {exc}")

    # 3. Fallback: GoogleTranslator
    try:
        from deep_translator import GoogleTranslator
        res = GoogleTranslator(source="auto", target=target_lang).translate(text)
        if res and res.strip():
            print(f"[esp32_manager] Google translation: '{text}' -> '{res.strip()}' ({target_lang})")
            return res.strip()
    except Exception:
        pass

    return text

>>>>>>> Stashed changes

def text_to_esp32_pcm(text: str, lang: str = "en") -> Optional[bytes]:
    """
    Convert text to 8000 Hz unsigned 8-bit PCM audio using gTTS and FFmpeg.
<<<<<<< Updated upstream
    Returns bytes ready to stream directly to ESP32 DAC channel 1.
    """
    cleaned = re.sub(r"[#*_`~>]+", " ", text)
    cleaned = re.sub(r"[^\w\s.,!?-]", "", cleaned).strip()
    if not cleaned:
        return None

    # Limit length so audio fits within ESP32 buffer limits (~35 seconds)
=======
    Automatically translates text to target language before synthesizing.
    Returns bytes ready to stream directly to ESP32 DAC channel 1.
    """
    if not text or not text.strip():
        return None

    # Translate text to target language if not English
    speech_text = translate_text(text, target_lang=lang) if lang != "en" else text

    # Clean unwanted formatting/control characters while fully preserving all Unicode scripts, matras & diacritics
    cleaned = re.sub(r"[\x00-\x1f\x7f#*_`~<>{}[\]\\]+", " ", speech_text).strip()
    if not cleaned:
        cleaned = speech_text.strip()

>>>>>>> Stashed changes
    cleaned = cleaned[:350]

    try:
        from gtts import gTTS

<<<<<<< Updated upstream
        # 1. Synthesize MP3 in memory
=======
        print(f"[esp32_manager] Synthesizing speech ({lang}): '{cleaned}'")
>>>>>>> Stashed changes
        tts = gTTS(text=cleaned, lang=lang, slow=False)
        mp3_buf = BytesIO()
        tts.write_to_fp(mp3_buf)
        mp3_buf.seek(0)
        mp3_bytes = mp3_buf.read()

        # 2. Resample via FFmpeg: mono, 8000Hz, signed 16-bit PCM
        process = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel", "error",
                "-i", "pipe:0",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=7",
                "-ac", "1",
                "-ar", str(SAMPLE_RATE),
                "-sample_fmt", "s16",
                "-f", "s16le",
                "pipe:1",
            ],
            input=mp3_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if process.returncode != 0:
            print(f"[esp32_manager] FFmpeg resample error: {process.stderr.decode(errors='ignore')}")
            return None

        pcm_signed16 = process.stdout
        if not pcm_signed16:
            return None

        # 3. Convert Signed 16-bit to Unsigned 8-bit PCM for DAC (0..255, center 128)
        num_samples = len(pcm_signed16) // 2
        pcm_u8 = bytearray(num_samples)

        for i in range(num_samples):
            sample = struct.unpack_from("<h", pcm_signed16, i * 2)[0]
            # Map -32768..32767 to 0..255
            sample8 = (sample + 32768) >> 8
            pcm_u8[i] = max(0, min(255, sample8))

        pcm_bytes = bytes(pcm_u8)
        if len(pcm_bytes) > MAX_AUDIO_SIZE:
            pcm_bytes = pcm_bytes[:MAX_AUDIO_SIZE]

        return pcm_bytes

    except Exception as exc:
        print(f"[esp32_manager] text_to_esp32_pcm exception: {exc}")
        return None


# Pre-defined preset announcements for rapid crowd dispersal
CROWD_PRESETS = {
    "siren": {
        "title": "Emergency Siren",
        "description": "High-urgency frequency sweeping wail tone",
        "generator": lambda: generate_siren_pcm(duration=3.5),
    },
    "chime": {
        "title": "Attention Chime",
        "description": "Two-tone bell to alert crowd before instructions",
        "generator": lambda: generate_chime_pcm(),
    },
    "alarm": {
        "title": "Evacuation Alarm",
        "description": "Urgent alternating two-tone horn signal",
        "generator": lambda: generate_alarm_pcm(duration=3.0),
    },
    "beep": {
        "title": "Warning Beeps",
        "description": "Three sharp warning pulses",
        "generator": lambda: generate_beep_pcm(count=3),
    },
    "disperse": {
        "title": "Disperse Notice",
        "description": "Voice: Clear the walkway and move forward",
        "text": "Attention! Please clear the walkway and keep moving forward.",
    },
    "warning": {
        "title": "Crowd Density Warning",
        "description": "Voice: High density detected, maintain distance",
        "text": "Caution: High crowd density detected in this sector. Please maintain calm and do not push.",
    },
    "evacuate": {
        "title": "Emergency Evacuate",
        "description": "Voice: Proceed calmly to emergency exits",
        "text": "Emergency announcement. Please proceed calmly to the nearest marked emergency exit.",
    },
}


# ── ESP32 Wireless TCP Manager ───────────────────────────────────────

class ESP32WirelessManager:
    """
    Manages wireless TCP connection to the ESP32 on port 8002.
    - Receives button events from GPIO 14 ('BTN')
    - Streams 8000 Hz 8-bit PCM audio to GPIO 25 (DAC)
    """

    def __init__(self, port: int = ESP32_TCP_PORT):
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.active_client: Optional[socket.socket] = None
        self.client_address: Optional[tuple] = None
        self.connected = False
        self.running = False
        self._lock = threading.Lock()
        self._server_thread: Optional[threading.Thread] = None
        self.button_callback: Optional[Callable[[], None]] = None

        self._last_btn_time: float = 0.0
        self.last_button_event_iso: Optional[str] = None
        self.current_playing_label: Optional[str] = None
        self.is_streaming_audio: bool = False
        self._stop_requested: bool = False

    def start(self, on_button_press: Optional[Callable[[], None]] = None):
        self.button_callback = on_button_press
        self.running = True
        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        self._server_thread.start()
        print(f"[esp32_manager] TCP Server running on port {self.port} (DAC Pin 25, Button Pin 14)")

    def stop(self):
        self.running = False
        self._stop_requested = True
        with self._lock:
            if self.active_client:
                try:
                    self.active_client.close()
                except Exception:
                    pass
                self.active_client = None
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass

    def is_esp32_connected(self) -> bool:
        with self._lock:
            return self.connected and (self.active_client is not None)

    def get_status(self) -> dict:
        with self._lock:
            client_ip = self.client_address[0] if self.client_address else None
            client_port = self.client_address[1] if self.client_address else None
            return {
                "connected": self.connected and (self.active_client is not None),
                "client_ip": client_ip,
                "client_port": client_port,
                "server_port": self.port,
                "is_streaming": self.is_streaming_audio,
                "current_audio": self.current_playing_label,
                "last_button_event": self.last_button_event_iso,
            }

    def _run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("0.0.0.0", self.port))
            self.server_socket.listen(2)
        except Exception as e:
            print(f"[esp32_manager] Failed to bind TCP server on port {self.port}: {e}")
            return

        while self.running:
            try:
                client_sock, client_addr = self.server_socket.accept()
                with self._lock:
                    if self.active_client:
                        try:
                            self.active_client.close()
                        except Exception:
                            pass
                    self.active_client = client_sock
                    self.client_address = client_addr
                    self.connected = True

<<<<<<< Updated upstream
                print(f"[esp32_manager] ✓ Wireless ESP32 connected from {client_addr[0]}:{client_addr[1]}")
=======
                print(f"[esp32_manager] [OK] Wireless ESP32 connected from {client_addr[0]}:{client_addr[1]}")
>>>>>>> Stashed changes
                self._handle_client(client_sock)
            except Exception as e:
                if self.running:
                    print(f"[esp32_manager] Server accept exception: {e}")
                time.sleep(1)

    def _handle_client(self, client_sock: socket.socket):
        buffer = ""
        while self.running:
            try:
                data = client_sock.recv(256)
                if not data:
                    break

                text = data.decode(errors="ignore")
                buffer += text

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        print(f"[esp32_manager] ESP32 -> {line}")
                        if "BTN" in line:
                            now = time.time()
                            if now - self._last_btn_time > 0.4:
                                self._last_btn_time = now
                                self.last_button_event_iso = datetime.now(timezone.utc).isoformat()
<<<<<<< Updated upstream
                                print("[esp32_manager] 🔘 Button Press on ESP32 (GPIO 14)!")
=======
                                print("[esp32_manager] [BUTTON] Button Press on ESP32 (GPIO 14)!")
>>>>>>> Stashed changes
                                if self.button_callback:
                                    try:
                                        self.button_callback()
                                    except Exception as cb_err:
                                        print(f"[esp32_manager] Button callback error: {cb_err}")
            except Exception:
                break

        print("[esp32_manager] ESP32 disconnected.")
        with self._lock:
            if self.active_client == client_sock:
                self.active_client = None
                self.connected = False

    def stop_audio(self):
        """Signal current audio transmission to stop."""
        self._stop_requested = True

    def send_pcm(self, pcm_bytes: bytes, label: str = "Audio") -> bool:
        """
        Send unsigned 8-bit PCM audio stream to the wireless ESP32 in a background thread.
        Uses exact packet format: 0xA5 0x5A + uint32 length + paced 128-byte chunks.
        """
        if not pcm_bytes:
            print("[esp32_manager] Empty PCM bytes provided.")
            return False

        with self._lock:
            client = self.active_client
            is_conn = self.connected and (client is not None)

        if not is_conn or not client:
            print("[esp32_manager] Cannot send audio: ESP32 is not connected via Wi-Fi.")
            return False

        self._stop_requested = False

        def _worker():
            self.is_streaming_audio = True
            self.current_playing_label = label
            try:
                print(f"[esp32_manager] Streaming '{label}' ({len(pcm_bytes)} bytes) to ESP32 DAC...")
                header = MAGIC_HEADER + struct.pack("<I", len(pcm_bytes))
                client.sendall(header)

<<<<<<< Updated upstream
                CHUNK_SIZE = 128
                bytes_sent = 0
                start_time = time.time()
=======
                CHUNK_SIZE = 512
                bytes_sent = 0
                start_time = time.time()
                lead_buffer = 0.5  # Allow 500ms pre-buffer in TCP to prevent jitter/underrun
>>>>>>> Stashed changes

                while bytes_sent < len(pcm_bytes) and not self._stop_requested:
                    chunk = pcm_bytes[bytes_sent : bytes_sent + CHUNK_SIZE]
                    client.sendall(chunk)
                    bytes_sent += len(chunk)

<<<<<<< Updated upstream
                    # Pace transmission according to 8000 Hz sample rate
                    expected_time = bytes_sent / SAMPLE_RATE
=======
                    # Pace transmission according to 8000 Hz sample rate with lead buffer
                    expected_time = (bytes_sent / SAMPLE_RATE) - lead_buffer
>>>>>>> Stashed changes
                    elapsed = time.time() - start_time
                    if expected_time > elapsed:
                        time.sleep(expected_time - elapsed)

                print(f"[esp32_manager] Audio stream '{label}' complete.")
            except Exception as exc:
                print(f"[esp32_manager] Audio transmit error: {exc}")
            finally:
                self.is_streaming_audio = False
                self.current_playing_label = None

        threading.Thread(target=_worker, daemon=True).start()
        return True

    def play_preset(self, preset_key: str) -> tuple[bool, str]:
        """Play one of the pre-defined tones or announcements."""
        preset = CROWD_PRESETS.get(preset_key.lower())
        if not preset:
            return False, f"Unknown preset: {preset_key}"

        if not self.is_esp32_connected():
            return False, "ESP32 is not connected on port 8002"

        # Check if it has a direct waveform generator
        if "generator" in preset:
            pcm = preset["generator"]()
            ok = self.send_pcm(pcm, label=preset["title"])
            return ok, f"Playing {preset['title']}"

        # Otherwise synthesize voice announcement
        if "text" in preset:
            pcm = text_to_esp32_pcm(preset["text"], lang="en")
            if not pcm:
                # Fallback to siren if TTS unavailable
                pcm = generate_siren_pcm(duration=2.5)
            ok = self.send_pcm(pcm, label=preset["title"])
            return ok, f"Broadcasting {preset['title']}"

        return False, "Invalid preset definition"

    def play_custom_tts(self, text: str, lang: str = "en") -> tuple[bool, str]:
<<<<<<< Updated upstream
        """Convert custom text to speech and stream to ESP32."""
=======
        """Convert custom text to speech, translating if needed, and stream to ESP32."""
>>>>>>> Stashed changes
        if not text or not text.strip():
            return False, "Text cannot be empty"

        if not self.is_esp32_connected():
            return False, "ESP32 is not connected on port 8002"

<<<<<<< Updated upstream
=======
        translated_display = translate_text(text, target_lang=lang) if lang != "en" else text
>>>>>>> Stashed changes
        pcm = text_to_esp32_pcm(text, lang=lang)
        if not pcm:
            return False, "Failed to generate speech audio from text"

<<<<<<< Updated upstream
        ok = self.send_pcm(pcm, label=f"Custom: {text[:25]}...")
        return ok, f"Broadcasting announcement: '{text[:30]}...'"
=======
        label = f"[{lang.upper()}] {translated_display[:25]}"
        ok = self.send_pcm(pcm, label=label)
        return ok, f"Broadcasting: '{translated_display[:35]}' ({lang.upper()})"
>>>>>>> Stashed changes


# Global singleton instance
esp32_manager = ESP32WirelessManager()
