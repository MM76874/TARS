## Hi there 👋
Our TARS project aligns with Different SDGs:

🔹 SDG 4: Quality Education
How TARS AI supports it: By acting as a personalised learning assistant, TARS can help students better understand subjects, get homework support, and access quality information anytime.

Impact: Promotes inclusive and equitable quality education and lifelong learning for all.

🔹 SDG 9: Industry, Innovation, and Infrastructure
How TARS AI supports it: TARS represents innovation in AI and digital infrastructure. It encourages the development of intelligent systems that support businesses, education, and communication.

Impact: Builds resilient infrastructure, promotes sustainable industrialisation, and fosters innovation.

🔹 SDG 8: Decent Work and Economic Growth
How TARS AI supports it: TARS can help individuals develop 21st-century skills, prepare for AI-driven job markets, and enhance productivity through automation and information access.

Impact: Encourages higher levels of economic productivity through technological upgrading and innovation.

🔹 SDG 10: Reduced Inequalities
How TARS AI supports it: By providing AI support to users regardless of background, income, or location, TARS helps bridge the digital divide.

Impact: Promotes equal access to information and technology, especially in under-resourced communities.

## Tars UI evolution
![image](https://github.com/user-attachments/assets/d8d50d2f-f4c2-4b8a-8cc3-ef417a99d271)

                                                       Prototype

![image](https://github.com/user-attachments/assets/4a031818-2227-4827-ae46-5cfb835db107)

                                                       Current UI


## 📁 Project Files Overview

### `tars.html`

This is the main HTML frontend for the TARS AI Dashboard.

* Uses **TailwindCSS** for styling.
* Provides a two-panel layout:

  * **Adjust TARS**: Sliders to control the AI's sarcasm, humor, and seriousness levels.
  * **Ask TARS**: Input box to type questions and buttons for text/voice input.
* Includes a `canvas` for a dynamic particle background (`tars.js`).
* Loads Google Fonts and links to custom CSS (`tars.css`) and JavaScript (`tars.js`).

---

### `tars.css`

Custom CSS to support light/dark themes and UI transitions.

* Default theme is dark with a futuristic font (`Orbitron`).
* Light mode is activated by toggling a class on `<body>`.
* Smooth transitions are applied to background, color, and borders.
* Enhances the appearance of input fields, sections, and text contrast.

---

### `tars.js`

JavaScript for UI interactivity and background effects.

* **Particle system**:

  * Creates a glowing, animated background.
  * Lines connect particles to the mouse cursor for a responsive effect.
* **Theme toggle**: Switches between light and dark modes.
* **Voice interaction**:

  * Uses browser speech recognition for input.
  * Calls `/voice` API to get audio responses using ElevenLabs.
* **Chat functionality**:

  * Sends input + personality settings to the Flask API (`/chat`).
  * Displays the AI's response in the UI and plays voice output.

---

### `TARS.py`

Python Flask backend to power the AI logic.

* **Cohere API**: Handles text-based responses using a custom prompt for the TARS persona.
* **ElevenLabs API**: Converts responses into speech using a specific voice model.
* **Session History**:

  * Saves chat history per user in the `chat_histories` folder.
  * Provides endpoints to list and fetch past sessions.
* **Endpoints**:

  * `POST /chat`: Accepts input, parameters (sarcasm/humor/serious), returns response.
  * `POST /voice`: Accepts text, returns MP3 voice stream.
  * `GET /sessions`: Lists all session files.
  * `GET /session/<user_id>`: Returns a specific user's conversation history.

---
https://youtu.be/QJZCgvE4zzc
