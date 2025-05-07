import sys
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

# 🔑 API KEY
co = cohere.Client("thehtLrp9awFharoJCxFbGXtrRaPrNhLXuOyfe67")

pygame.mixer.init()

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

        self.voice_button = QPushButton()
        self.voice_button.setFixedSize(70, 70)
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
            }
            QPushButton:hover {
                background-color: rgba(25, 212, 205, 0.9);
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 1);
                transform: scale(0.95);
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
        self.sarcasm_slider = self.create_slider("#FFB347")
        self.humor_slider = self.create_slider("#87CEFA")
        self.serious_slider = self.create_slider("#FF6347")
        self.slider_layout.addRow(QLabel("Sarcasm", font=self.orbitron_large), self.sarcasm_slider)
        self.slider_layout.addRow(QLabel("Humor", font=self.orbitron_large), self.humor_slider)
        self.slider_layout.addRow(QLabel("Seriousness", font=self.orbitron_large), self.serious_slider)
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
        self.mood_label.setText(f"🎭 Mood: Sarcasm {self.locked_sarcasm} | Humor {self.locked_humor} | Seriousness {self.locked_serious}")

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

            with open("tts_input.txt", "w", encoding="utf-8") as f:
                f.write(text)

            os.system("python inference.py --text_file tts_input.txt --output_file TTtars_response.wav")

            pygame.mixer.music.load("TTtars_response.wav")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[TTS ERROR] {e}")

    def make_tars_prompt(self, user_input):
        prompt = f"""
You are TARS from Interstellar, known for dry humor, sarcasm, and blunt honesty.
Be brief. Talk like a sentient AI buddy, not a chatbot.
Mood: Sarcasm {self.locked_sarcasm} | Humor {self.locked_humor} | Seriousness {self.locked_serious}
"""
        return self.ask_cohere(user_input, prompt)

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
