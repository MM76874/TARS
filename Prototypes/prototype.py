import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout,
    QSlider, QPushButton, QFormLayout
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QFontDatabase, QPainter, QRadialGradient, QColor, QBrush
import cohere
from elevenlabs import generate, play, set_api_key

# 🔑 Initialize Cohere
co = cohere.Client("thehtLrp9awFharoJCxFbGXtrRaPrNhLXuOyfe67")

# Set up ElevenLabs API key
set_api_key(os.getenv("sk_067850dde3fcc8de4309fc3303e8d71508d1921a1bf165e9"))

class TARSApp(QWidget):
    def __init__(self):
        super().__init__()

        # --- Font loading ---
        font_path = "Orbitron-Regular.ttf"
        if os.path.exists(font_path):
            QFontDatabase.addApplicationFont(font_path)
            self.orbitron = QFont("Orbitron", 10)
        else:
            self.orbitron = QFont("Arial", 10)

        # --- Window setup ---
        self.setWindowTitle("TARS AI Chat")
        self.setFixedSize(600, 780)
        self.setStyleSheet("color: white;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)

        # --- Entry Box ---
        self.entry = QLineEdit()
        self.entry.setFont(QFont("Orbitron", 14))
        self.entry.setPlaceholderText("Ask me anything...")
        self.entry.setFixedWidth(400)
        self.entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #87CEFA;
                border-radius: 10px;
                padding: 10px;
                background-color: rgba(0, 0, 0, 180);
                color: white;
            }
        """)
        self.layout.addWidget(self.entry, alignment=Qt.AlignHCenter)

        # --- Ask Button ---
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

        # --- Response Label ---
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

        # --- Sliders ---
        self.sarcasm_slider = self.create_slider("#FFB347")
        self.humor_slider = self.create_slider("#87CEFA")
        self.serious_slider = self.create_slider("#FF6347")

        self.slider_layout = QFormLayout()
        self.slider_layout.addRow("Sarcasm", self.sarcasm_slider)
        self.slider_layout.addRow("Humor", self.humor_slider)
        self.slider_layout.addRow("Seriousness", self.serious_slider)
        self.layout.addLayout(self.slider_layout)

        # --- Lock Mood Button ---
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

        # --- Mood Label ---
        self.mood_label = QLabel("")
        self.mood_label.setFont(QFont("Orbitron", 10, QFont.Bold))
        self.layout.addWidget(self.mood_label, alignment=Qt.AlignHCenter)

        self.lock_mood()

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

        # Gradient Background
        gradient = QRadialGradient(self.width() // 2, self.height() // 2, self.width() // 1.5)
        gradient.setColorAt(0.0, QColor("#111"))
        gradient.setColorAt(0.5, QColor("#1A1A1A"))
        gradient.setColorAt(1.0, QColor("#000000"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # Central Glowing Circle
        circle_gradient = QRadialGradient(self.width() // 2, 100, 150)
        circle_gradient.setColorAt(0.0, QColor(135, 206, 250, 200))  # Sky blue
        circle_gradient.setColorAt(1.0, QColor(33, 33, 33, 0))

        painter.setBrush(QBrush(circle_gradient))
        painter.drawEllipse(QRectF(self.width()//2 - 150, -50, 300, 300))

    def lock_mood(self):
        self.locked_sarcasm = self.sarcasm_slider.value()
        self.locked_humor = self.humor_slider.value()
        self.locked_serious = self.serious_slider.value()
        self.update_mood_label()

    def update_mood_label(self):
        mood_text = f"🎭 Locked Mood: Sarcasm {self.locked_sarcasm} | Humor {self.locked_humor} | Seriousness {self.locked_serious}"
        self.mood_label.setText(mood_text)

    def handle_input(self):
        user_input = self.entry.text().strip()
        self.response_label.clear()
        if user_input:
            response = self.make_tars_prompt(user_input)
            self.response_label.setText(response)
            self.speak_text(response)  # TTS with ElevenLabs

    def speak_text(self, text):
        # Use ElevenLabs to generate and play the speech
        audio = generate(
            text=text,
            voice="John Doe - Deep",  # Replace with your selected voice
            model="eleven_multilingual_v2"
        )
        play(audio)

    def make_tars_prompt(self, user_input):
        system_prompt = f"""
You are TARS, the AI robot from Interstellar, known for dry humor, sarcasm, and blunt honesty.
Be TARS, you are not a chatbot and keep it short
Respond to users based on the following settings:
- Sarcasm: {self.locked_sarcasm}%
- Humor: {self.locked_humor}%
- Seriousness: {self.locked_serious}%

You speak like a witty human. Keep responses short, confident, and sarcastic when appropriate. If the user says something silly, gently roast them.
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TARSApp()
    window.show()
    sys.exit(app.exec_())