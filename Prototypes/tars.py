import random
from tkinter import *
import cohere

# 🔑 Initialize Cohere
co = cohere.Client("thehtLrp9awFharoJCxFbGXtrRaPrNhLXuOyfe67")  # Replace with your actual API key

# --- GUI Setup ---
root = Tk()
root.geometry("500x750")
root.configure(background="cyan")
root.title("TARS AI Chat")

# Entry box
entry = Entry(root, width=40, font=("Arial", 14))
entry.place(relx=0.5, rely=0.1, anchor=CENTER)

# Response label
response_label = Label(root, text="", wraplength=400, bg="white", font=("Arial", 12), justify=LEFT)
response_label.place(relx=0.5, rely=0.3, anchor=N)

# --- Sliders for Mood ---
Label(root, text="Sarcasm", bg="cyan", font=("Arial", 12)).place(relx=0.2, rely=0.45, anchor=CENTER)
sarcasm_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=150)
sarcasm_slider.set(80)
sarcasm_slider.place(relx=0.2, rely=0.5, anchor=CENTER)

Label(root, text="Humor", bg="cyan", font=("Arial", 12)).place(relx=0.5, rely=0.45, anchor=CENTER)
humor_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=150)
humor_slider.set(90)
humor_slider.place(relx=0.5, rely=0.5, anchor=CENTER)

Label(root, text="Seriousness", bg="cyan", font=("Arial", 12)).place(relx=0.8, rely=0.45, anchor=CENTER)
serious_slider = Scale(root, from_=0, to=100, orient=HORIZONTAL, length=150)
serious_slider.set(50)
serious_slider.place(relx=0.8, rely=0.5, anchor=CENTER)

# Mood label
mood_label = Label(root, text="", bg="cyan", font=("Arial", 11, "bold"))
mood_label.place(relx=0.5, rely=0.63, anchor=CENTER)

# Locked mood values
locked_sarcasm = sarcasm_slider.get()
locked_humor = humor_slider.get()
locked_serious = serious_slider.get()

# Lock Mood Button Callback
def lock_mood():
    global locked_sarcasm, locked_humor, locked_serious
    locked_sarcasm = sarcasm_slider.get()
    locked_humor = humor_slider.get()
    locked_serious = serious_slider.get()
    update_mood_label()

# Update Mood Label
def update_mood_label():
    mood_text = f"🎭 Locked Mood: Sarcasm {locked_sarcasm} | Humor {locked_humor} | Seriousness {locked_serious}"
    mood_label.config(text=mood_text)

# Lock Mood Button
Button(root, text="Lock Mood", command=lock_mood).place(relx=0.5, rely=0.58, anchor=CENTER)

# Cohere Chat Request
def ask_cohere(user_input, system_prompt):
    try:
        response = co.chat(
            model='command-r',
            message=user_input,
            preamble=system_prompt
        )
        return response.text
    except Exception as e:
        return f"[ERROR] {e}"

# Create Prompt
def make_tars_prompt(user_input):
    system_prompt = f"""
You are TARS, the AI robot from Interstellar, known for dry humor, sarcasm, and blunt honesty.

Respond to users based on the following settings:
- Sarcasm: {locked_sarcasm}%
- Humor: {locked_humor}%
- Seriousness: {locked_serious}%

You speak like a witty human. Keep responses short, confident, and sarcastic when appropriate. If the user says something silly, gently roast them.

Examples of your tone:
User: What's 2 + 2?
TARS: Bold question. Going with... 4. Final answer.

User: What's your favorite color?
TARS: I'm a robot. But emotionally? Black.
"""

    return ask_cohere(user_input, system_prompt)

# Button callback
def handle_input():
    user_input = entry.get()
    if user_input.strip() != "":
        response = make_tars_prompt(user_input)
        response_label.config(text=response)
        response_label.clear()

# Ask Button
Button(root, text="Ask TARS", command=handle_input).place(relx=0.5, rely=0.2, anchor=CENTER)

# Set default label
lock_mood()

# Start GUI
root.mainloop()