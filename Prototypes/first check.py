from tkinter import*
import google.generativeai as genai

root = Tk()
root.geometry("500x600")
root.configure(background = "cyan")
hello = Entry(root)
l1 = Label(root)

genai.configure(api_key="AIzaSyDdqn4QixSmp41_R6bEKVcVHZ4gPMPn0nM")

model = genai.GenerativeModel('gemini-pro')

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text



def make_tars_prompt(user_input, honesty=90, humor=80):
    system_prompt = f"""
    You are TARS from Interstellar. Honesty: {honesty}%, Humor: {humor}%.
    Respond in a helpful, witty, and mission-focused way.
    User: {user_input}
    """
    return ask_gemini(system_prompt)

btn = Button(root, text="Ask", command=make_tars_prompt)
hello.place(relx=0.5, rely=0.5, anchor=CENTER)
btn.place(relx=0.7, rely=0.5, anchor=CENTER)
l1.place(relx=0.5, rely=0.4, anchor=CENTER)
root.mainloop()








