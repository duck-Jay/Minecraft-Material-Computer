import calculator
import customtkinter as ctk

class GUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("<UNK>")
        self.root.resizable(False, False)
        self.root.geometry("1200x800")

    def mainloop(self):
        self.root.mainloop()