import tkinter as tk
import datetime
import os
from threading import Thread
from queue import Queue
from enum import Enum, auto
from src.aiengine import AIEngine

class TicketPurpose(Enum):
    CONSOLE_1_CONTENTS = auto()
    CONSOLE_2_CONTENTS = auto()
    CONSOLE_3_CONTENTS = auto()

class ConsoleUI:
    def __init__(self, aiengine: AIEngine):
        self.aiengine = aiengine

        self.root = tk.Tk()
        self.root.title("Text Based Game")
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.output_height = 60
        self.section_width = 70
        self.console_font = ("Courier", 10)
        self.console_bg = "black"
        self.console_fg = "white"
        now = datetime.datetime.now()
        self.current_date_time = now.strftime("%Y-%m-%d-%H-%M-%S")

        self.consoles = []
        self.inputs = []

        # for i in range(1, 4):
        frame, console, input_entry = self.create_console_section(1)
        frame.pack(side=tk.LEFT, padx=5, pady=5)
        self.consoles.append(console)
        self.inputs.append(input_entry)

    def create_console_section(self, console_num):
        frame = tk.Frame(self.root)
        console_frame = tk.Frame(frame)
        console_frame.pack(fill=tk.BOTH, expand=True)
        console = tk.Text(console_frame, height=self.output_height, width=self.section_width, state=tk.DISABLED, font=self.console_font, bg=self.console_bg, fg=self.console_fg)
        console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(console_frame, command=console.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        console.config(yscrollcommand=scrollbar.set)
        input_entry = tk.Entry(frame, width=self.section_width, font=self.console_font, bg=self.console_bg, fg=self.console_fg, insertbackground=self.console_fg)
        input_entry.pack(side=tk.BOTTOM, fill=tk.X)
        input_entry.bind("<Return>", lambda event: self.user_input_to_console(console_num))
        return frame, console, input_entry

    def write_to_log(self, console_num, text):
        log_file_name = self.current_date_time + "_console" + str(console_num) + ".log"
        log_file_path = os.path.join(os.getcwd(), "logs", log_file_name)
        with open(log_file_path, "a") as log_file:
            log_file.write(text + "\n")

    def clear_console(self, console_num):
        current_console = self.consoles[console_num-1]
        current_console.configure(state=tk.NORMAL)
        current_console.delete("1.0", tk.END)
        current_console.configure(state=tk.DISABLED)
        self.write_to_log(console_num, "--------------------------------------------------------------")

    # Can simplify the above three functions by using self.consoles[console_num-1]
    def write_to_console(self, console_num, text):
        current_console = self.consoles[console_num-1]
        current_console.configure(state=tk.NORMAL)
        current_console.insert(tk.END, text + "\n")
        current_console.see(tk.END)
        current_console.configure(state=tk.DISABLED)
        self.write_to_log(console_num, text)

    def user_input_to_console(self, console_num):
        thread = Thread(target=self.get_input, args=(console_num,), daemon=True)
        thread.start()

    def get_input(self, console_num):
        current_input = self.inputs[console_num-1]
        text = current_input.get()
        current_input.delete(0, tk.END)
        # Also disable the input and grey it out
        current_input.configure(state=tk.DISABLED)
        current_input.configure(bg="gray")
        self.write_to_console(console_num, text)
        if console_num == 1:
            answer = self.aiengine.process_player_input(text)
            if answer is None:
                answer = "ERROR"
            self.write_to_console(console_num, answer)
            # re-enable the input
            current_input.configure(state=tk.NORMAL)
            current_input.configure(bg=self.console_bg)

    def write_llm_query_to_console(self, console_num, system_prompt, prompt):
        self.clear_console(console_num)
        self.write_to_console(console_num, "\nSystem Prompt:\n" + system_prompt)
        self.write_to_console(console_num, "\nPrompt:\n" + prompt)

    def run(self):
        self.root.mainloop()

    def quit(self):
        self.root.destroy()