import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import subprocess
import json


class JQProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JQ JSON Processor")
        self.build_ui()

    def build_ui(self):
        # JSON Input
        self.add_label("JSON Input")
        self.json_input_text = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.json_input_text.pack(padx=10, pady=(0, 10))

        # JQ Expression
        self.add_label("JQ Expression")
        self.jq_expression_entry = tk.Entry(self.root, width=80)
        self.jq_expression_entry.pack(padx=10, pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Apply JQ", command=self.apply_jq).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Load JSON", command=self.load_json).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Copy Result", command=self.copy_result).pack(side=tk.LEFT, padx=5)

        # Result
        self.add_label("Result")
        self.result_text = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.result_text.pack(padx=10, pady=(0, 10))

    def add_label(self, text):
        tk.Label(self.root, text=text, font=("Arial", 10, "bold")).pack(anchor="w", padx=10)

    def apply_jq(self):
        self.result_text.delete('1.0', tk.END)
        try:
            json_input = self.json_input_text.get("1.0", "end-1c")
            jq_expr = self.jq_expression_entry.get()

            # Validate JSON first
            json.loads(json_input)

            result = self.process_json(json_input, jq_expr)

            try:
                parsed = json.loads(result)
                formatted = json.dumps(parsed, indent=4)
            except json.JSONDecodeError:
                formatted = result  # Raw output

            self.result_text.insert(tk.INSERT, formatted)

        except Exception as e:
            self.result_text.insert(tk.INSERT, f"Error: {str(e)}")

    def process_json(self, json_input, jq_expr):
        process = subprocess.Popen(['jq', jq_expr],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True)
        stdout, stderr = process.communicate(json_input)
        if process.returncode != 0 or stderr:
            raise Exception(stderr.strip())
        return stdout.strip()

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    data = file.read()
                    json.loads(data)  # Validate
                    self.json_input_text.delete("1.0", tk.END)
                    self.json_input_text.insert(tk.INSERT, data)
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

    def copy_result(self):
        result = self.result_text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        self.root.update()
        messagebox.showinfo("Copied", "Result copied to clipboard.")


def main():
    root = tk.Tk()
    app = JQProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
