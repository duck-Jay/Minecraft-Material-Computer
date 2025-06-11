import calculator
import customtkinter as ctk

class GUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("<UNK>")
        self.root.resizable(False, False)
        self.root.geometry("1200x800")
        self.calculator = calculator.App()
        self.main()

    def main(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
