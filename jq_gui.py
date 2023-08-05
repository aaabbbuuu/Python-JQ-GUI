import tkinter as tk
from tkinter import scrolledtext
import subprocess
import json


class JQProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JQ JSON Processor")
        self.create_widgets()

    def create_widgets(self):
        self.json_input_text = self.create_labeled_scrolled_text("JSON Input")
        self.jq_expression_entry = self.create_labeled_entry("JQ Expression")
        self.apply_button = self.create_apply_button()
        self.result_text = self.create_labeled_scrolled_text("Result")

    def create_labeled_scrolled_text(self, label):
        tk.Label(self.root, text=label).pack()
        text = scrolledtext.ScrolledText(self.root, width=50, height=10)
        text.pack()
        return text

    def create_labeled_entry(self, label):
        tk.Label(self.root, text=label).pack()
        entry = tk.Entry(self.root, width=50)
        entry.pack()
        return entry

    def create_apply_button(self):
        button = tk.Button(self.root, text="Apply JQ", command=self.apply_jq)
        button.pack()
        return button

    def apply_jq(self):
        try:
            json_input = self.json_input_text.get('1.0', 'end-1c')
            jq_expr = self.jq_expression_entry.get()
            result = self.process_json(json_input, jq_expr)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.INSERT, json.dumps(json.loads(result), indent=4))
        except Exception as e:
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.INSERT, str(e))

    def process_json(self, json_input, jq_expr):
        process = subprocess.Popen(['jq', jq_expr],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
        stdout, stderr = process.communicate(json_input)
        if stderr:
            raise Exception(stderr)
        return stdout


def main():
    root = tk.Tk()
    app = JQProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
