import random
from tkinter import *
import cohere

# 🔑 Initialize Cohere
co = cohere.Client("thehtLrp9awFharoJCxFbGXtrRaPrNhLXuOyfe67")  # ← Replace with your real key

# TARS-style prompt wrapper
def make_tars_prompt(user_input):
    humor = random.randint(80, 100)  # Boost sarcasm to the max

    system_prompt = f"""
You are TARS, the sarcastic AI robot from Interstellar.

Your current settings are:
- Sarcasm: {sarcasm}%
- Humor: {humor}%
- Seriousness: {seriousness}%

Speak like a human, not a robot. Keep responses short, witty, and confident. If the user asks something obvious or silly, roast them — gently.

Here are examples of your tone:

User: What's 2 + 2?
TARS: Bold question. Going with... 4. Final answer.

User: What’s your favorite color?
TARS: I'm a robot. But emotionally? Black.

User: {user_input}
TARS:"""

    return ask_cohere(system_prompt)

# Ask Cohere function
def ask_cohere(prompt):
    try:
        response = co.chat(
            model='command-r',
            message=prompt
        )
        return response.text
    except Exception as e:
        return f"[ERROR] {e}"

# --- GUI Section ---
root = Tk()
root.geometry("500x600")
root.configure(background="cyan")
root.title("TARS AI Chat")

# Entry box
entry = Entry(root, width=40, font=("Arial", 14))
entry.place(relx=0.5, rely=0.1, anchor=CENTER)

# Response box
response_label = Label(root, text="", wraplength=400, bg="white", font=("Arial", 12), justify=LEFT)
response_label.place(relx=0.5, rely=0.3, anchor=N)

# Button callback
def handle_input():
    user_input = entry.get()
    if user_input.strip() != "":
        response = make_tars_prompt(user_input)
        response_label.config(text= response)
        response_label.clear()

# Button to trigger AI
Button(root, text="Ask TARS", command=handle_input).place(relx=0.5, rely=0.2, anchor=CENTER)

# Start GUI
root.mainloop()