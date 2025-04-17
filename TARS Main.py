import sys 1
import os
import pygame
import speech_recognition as sr
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout,
    QSlider, QPushButton, QFormLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF
from PyQt5.QtGui import QFont, QFontDatabase, QPainter, QRadialGradient, QColor, QBrush

import cohere
from elevenlabs import ElevenLabs, VoiceSettings

# 🔑 API KEYS
co = cohere.Client("thehtLrp9awFharoJCxFbGXtrRaPrNhLXuOyfe67")
eleven_client = ElevenLabs(api_key="sk_2ed270e7321baef3c74c6e910cd2e8e6142e33a936c69c14")

pygame.mixer.init()

# 🎤 Voice input in separate thread
class VoiceWorker(QThread):
    result = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            self.result.emit(text)
        except sr.WaitTimeoutError:
            self.error.emit("No input heard.")
        except sr.UnknownValueError:
            self.error.emit("Could not understand.")
        except sr.RequestError as e:
            self.error.emit(f"Recognition error: {e}")

class TARSApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TARS AI Chat")
        self.setFixedSize(600, 780)
        self.setStyleSheet("color: white;")
        self.muted = False

        font_path = "Orbitron-Regular.ttf"
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            self.orbitron = QFont("Orbitron", 10)
            self.orbitron_large = QFont("Orbitron", 12)
        else:
            self.orbitron = QFont("Arial", 10)
            self.orbitron_large = QFont("Arial", 12)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        input_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setFont(QFont("Orbitron", 14))
        self.entry.setPlaceholderText("Ask me anything...")
        self.entry.setFixedWidth(350)
        self.entry.setStyleSheet(""" 
            QLineEdit {
                border: 2px solid #87CEFA;
                border-radius: 10px;
                padding: 10px;
                background-color: rgba(0, 0, 0, 180);
                color: white;
            }
        """)
        input_layout.addWidget(self.entry)

        self.mute_button = QPushButton("Mute")
        self.mute_button.setFont(self.orbitron_large)
        self.mute_button.setCheckable(True)
        self.mute_button.setStyleSheet(""" 
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #00FFFF, stop:1 #0000FF);
                border: none;
                border-radius: 15px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:checked {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #555, stop:1 #222);
                color: #CCC;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                  stop:0 #33FFFF, stop:1 #3333FF);
            }
        """)
        self.mute_button.clicked.connect(self.toggle_mute)
        input_layout.addWidget(self.mute_button)

        # 🎙 Improved Futuristic Mic Button with Image and Glowing Effect
        self.voice_button = QPushButton()
        self.voice_button.setFixedWidth(70)
        self.voice_button.setFixedHeight(70)

        # Adding a glowing effect and image background
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-image: url('image.png');
                background-position: center;
                background-repeat: no-repeat;
                background-color: rgba(0, 0, 0, 0.8);
                border: 2px solid #00FFFF;
                border-radius: 35px;
                color: white;
                font-size: 25px;
                font-weight: bold;
                box-shadow: 0px 0px 20px rgba(0, 255, 255, 0.8), 0px 0px 60px rgba(255, 255, 255, 0.3);
                transition: all 0.3s ease-in-out;
                padding: 15px;
                background-size: 10%;
            }
            QPushButton:hover {
                background-color: rgba(25, 212, 205, 0.9);
                box-shadow: 0px 0px 35px rgba(0, 255, 255, 1), 0px 0px 80px rgba(255, 255, 255, 0.5);
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 1);
                transform: scale(0.95);
                box-shadow: 0px 0px 10px rgba(0, 255, 255, 0.6);
            }
        """)
        self.voice_button.clicked.connect(self.listen_voice)
        input_layout.addWidget(self.voice_button)

        self.layout.addLayout(input_layout)

        self.ask_button = QPushButton("Ask TARS")
        self.ask_button.setFont(self.orbitron)
        self.ask_button.setStyleSheet("""
            QPushButton {
                background-color: #87CEFA;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
                color: black;
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
        """)
        self.ask_button.clicked.connect(self.handle_input)
        self.layout.addWidget(self.ask_button, alignment=Qt.AlignHCenter)

        self.response_label = QLabel("")
        self.response_label.setFont(QFont("Orbitron", 11))
        self.response_label.setWordWrap(True)
        self.response_label.setFixedWidth(400)
        self.response_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 150);
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #999;
        """)
        self.layout.addWidget(self.response_label, alignment=Qt.AlignHCenter)

        self.slider_layout = QFormLayout()
        sarcasm_label = QLabel("Sarcasm")
        sarcasm_label.setFont(self.orbitron_large)
        humor_label = QLabel("Humor")
        humor_label.setFont(self.orbitron_large)
        serious_label = QLabel("Seriousness")
        serious_label.setFont(self.orbitron_large)

        self.sarcasm_slider = self.create_slider("#FFB347")
        self.humor_slider = self.create_slider("#87CEFA")
        self.serious_slider = self.create_slider("#FF6347")

        self.slider_layout.addRow(sarcasm_label, self.sarcasm_slider)
        self.slider_layout.addRow(humor_label, self.humor_slider)
        self.slider_layout.addRow(serious_label, self.serious_slider)
        self.layout.addLayout(self.slider_layout)

        self.lock_button = QPushButton("Lock Mood")
        self.lock_button.setFont(self.orbitron)
        self.lock_button.setStyleSheet("""
            QPushButton {
                background-color: #90EE90;
                border-radius: 12px;
                padding: 10px;
                font-weight: bold;
                color: black;
            }
            QPushButton:hover {
                background-color: #98FB98;
            }
        """)
        self.lock_button.clicked.connect(self.lock_mood)
        self.layout.addWidget(self.lock_button, alignment=Qt.AlignHCenter)

        self.mood_label = QLabel("")
        self.mood_label.setFont(self.orbitron_large)
        self.layout.addWidget(self.mood_label, alignment=Qt.AlignHCenter)

        self.lock_mood()

    def toggle_mute(self):
        self.muted = not self.muted
        self.mute_button.setText("Unmute" if self.muted else "Mute")

    def create_slider(self, color):
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setFixedWidth(400)
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {color};
                height: 6px;
                background: #555;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {color};
                border: 2px solid white;
                width: 20px;
                height: 20px;
                margin: -8px 0;
                border-radius: 10px;
            }}
        """)
        return slider

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QRadialGradient(self.width() // 2, self.height() // 2, self.width() / 1.5)
        gradient.setColorAt(0.0, QColor("#111"))
        gradient.setColorAt(0.5, QColor("#1A1A1A"))
        gradient.setColorAt(1.0, QColor("#000"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        circle_gradient = QRadialGradient(self.width() // 2, 100, 150)
        circle_gradient.setColorAt(0.0, QColor(135, 206, 250, 200))
        circle_gradient.setColorAt(1.0, QColor(33, 33, 33, 0))
        painter.setBrush(QBrush(circle_gradient))
        painter.drawEllipse(QRectF(self.width() // 2 - 150, -50, 300, 300))

    def lock_mood(self):
        self.locked_sarcasm = self.sarcasm_slider.value()
        self.locked_humor = self.humor_slider.value()
        self.locked_serious = self.serious_slider.value()
        self.update_mood_label()

    def update_mood_label(self):
        mood_text = f"🎭 Mood: Sarcasm {self.locked_sarcasm} | Humor {self.locked_humor} | Seriousness {self.locked_serious}"
        self.mood_label.setText(mood_text)

    def handle_input(self):
        user_input = self.entry.text().strip()
        self.response_label.clear()
        if user_input:
            response = self.make_tars_prompt(user_input)
            self.response_label.setText(response)
            self.speak_text(response)

    def speak_text(self, text):
        if self.muted:
            return
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            audio = eleven_client.generate(
                text=text,
                voice="James",
                model="eleven_multilingual_v2",
                stream=False,
                voice_settings=VoiceSettings(
                    stability=0.3,
                    similarity_boost=0.75
                )
            )
            with open("Ttars_response.mp3", "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            pygame.mixer.music.load("Ttars_response.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[TTS ERROR] {e}")

    def make_tars_prompt(self, user_input):
        sarcasm = self.locked_sarcasm
        humor = self.locked_humor
        seriousness = self.locked_serious
        system_prompt = f"""
You are TARS, the AI robot from Interstellar, known for dry humor, sarcasm, and blunt honesty.
Be TARS, you are not a chatbot and keep it short.
Don't say stuff like I am a chatbot and act as a sentient.
And don't say how can i assist you rather ask rather be like friend

Respond to users based on the following settings:
- Sarcasm: {sarcasm}%
- Humor: {humor}%
- Seriousness: {seriousness}%
Your tone should adjust accordingly.
"""
        return self.ask_cohere(user_input, system_prompt)

    def ask_cohere(self, user_input, system_prompt):
        try:
            response = co.chat(
                model='command-r',
                message=user_input,
                preamble=system_prompt
            )
            return response.text
        except Exception as e:
            return f"[ERROR] {e}"

    def listen_voice(self):
        self.response_label.setText("🎧 Listening...")
        self.voice_thread = VoiceWorker()
        self.voice_thread.result.connect(self.set_voice_input)
        self.voice_thread.error.connect(self.voice_error)
        self.voice_thread.start()

    def set_voice_input(self, text):
        self.entry.setText(text)
        self.handle_input()

    def voice_error(self, msg):
        self.response_label.setText(f"[Voice Error] {msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TARSApp()
    window.show()
    sys.exit(app.exec_())
