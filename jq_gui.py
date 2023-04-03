import tkinter as tk
import json
import subprocess

class JQTool:
    def __init__(self, master):
        self.master = master
        self.master.title("JQ Tool")
        self.json_label = tk.Label(self.master, text="JSON:")
        self.json_label.pack()
        self.json_input = tk.Text(self.master, height=10)
        self.json_input.pack()
        self.jq_label = tk.Label(self.master, text="JQ Expression:")
        self.jq_label.pack()
        self.jq_input = tk.Entry(self.master, width=50)
        self.jq_input.pack()
        self.run_button = tk.Button(self.master, text="Run", command=self.run_jq)
        self.run_button.pack()
        self.result_label = tk.Label(self.master, text="Result:")
        self.result_label.pack()
        self.result_output = tk.Text(self.master, height=10)
        self.result_output.pack()

    def run_jq(self):
        try:
            json_input = json.loads(self.json_input.get("1.0", tk.END))
            jq_expression = self.jq_input.get()
            result = subprocess.run(["C:\Program Files\JQ\jq.exe", jq_expression], input=json.dumps(json_input), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.result_output.delete("1.0", tk.END)
                self.result_output.insert(tk.END, result.stdout.strip())
            else:
                self.result_output.delete("1.0", tk.END)
                self.result_output.insert(tk.END, f"Error: {result.stderr.strip()}")
        except Exception as e:
            self.result_output.delete("1.0", tk.END)
            self.result_output.insert(tk.END, f"Error: {e}")

root = tk.Tk()
app = JQTool(root)
root.mainloop()
