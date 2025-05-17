import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import json
from jq_processor_logic import JQProcessorLogic, JQProcessorError

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import SUCCESS, DANGER, INFO, LIGHT
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    from tkinter import ttk
    SUCCESS = "success" 
    DANGER = "danger"
    INFO = "info"
    LIGHT = "light"
    TTKBOOTSTRAP_AVAILABLE = False


class JQProcessorApp:
    def __init__(self, root):
        self.root = root

        if TTKBOOTSTRAP_AVAILABLE:
            self.style = ttk.Style(theme="superhero") 

        self.root.title("JQ JSON Processor")
        self.root.geometry("700x650")

        try:
            self.jq_logic = JQProcessorLogic()
        except JQProcessorError as e:
            messagebox.showerror("Initialization Error", str(e))
            self.root.quit()
            return

        self.status_bar_widget = None
        self.build_ui()
        self.set_status("Ready. Load JSON and enter a JQ expression.", "info")

    def build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Configure grid weights for responsiveness
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=3) # JSON Input
        main_frame.rowconfigure(1, weight=0) # JQ Expression
        main_frame.rowconfigure(2, weight=0) # Buttons
        main_frame.rowconfigure(3, weight=3) # Result
        main_frame.rowconfigure(4, weight=0) # Status Bar

        # JSON Input 
        input_frame = ttk.LabelFrame(main_frame, text="JSON Input", padding="5")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)

        self.json_input_text = scrolledtext.ScrolledText(input_frame, width=80, height=10, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        self.json_input_text.grid(row=0, column=0, sticky="nsew")

        # JQ Expression
        expr_frame = ttk.LabelFrame(main_frame, text="JQ Expression", padding="5")
        expr_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0,5))
        expr_frame.columnconfigure(0, weight=1)

        self.jq_expression_entry = ttk.Entry(expr_frame, width=80, font=("Arial", 10))
        self.jq_expression_entry.grid(row=0, column=0, sticky="ew")
        self.jq_expression_entry.bind("<Return>", lambda event: self.apply_jq())


        # Buttons 
        btn_frame = ttk.Frame(main_frame, padding="5")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=5)
        # Center buttons in the frame
        btn_frame.columnconfigure(0, weight=1) 
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        btn_frame.columnconfigure(3, weight=1) 
        btn_frame.columnconfigure(4, weight=1) 

        self.load_btn = ttk.Button(btn_frame, text="Load JSON", command=self.load_json)
        self.load_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.apply_btn = ttk.Button(btn_frame, text="Apply JQ", command=self.apply_jq, style="Accent.TButton") 
        self.apply_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.copy_btn = ttk.Button(btn_frame, text="Copy Result", command=self.copy_result)
        self.copy_btn.grid(row=0, column=2, padx=5, sticky="ew")

        self.clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_all)
        self.clear_btn.grid(row=0, column=3, padx=5, sticky="ew")

        self.format_json_btn = ttk.Button(btn_frame, text="Format Input JSON", command=self.format_input_json)
        self.format_json_btn.grid(row=0, column=4, padx=5, sticky="ew")


        # Result
        result_frame = ttk.LabelFrame(main_frame, text="Result", padding="5")
        result_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0,5))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        self.result_text = scrolledtext.ScrolledText(result_frame, width=80, height=10, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1)
        self.result_text.grid(row=0, column=0, sticky="nsew")
        self.result_text.configure(state='disabled') 

        # Status Bar 
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding="2 5")
        self.status_bar_widget = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding="2 5")
        self.status_bar_widget.grid(row=4, column=0, sticky="ew", padx=5, pady=(5,0))

    def set_status(self, message: str, level: str = "info"):
        self.status_var.set(message)
        if TTKBOOTSTRAP_AVAILABLE and self.status_bar_widget:
            current_bootstyle = LIGHT 
            if level == "error":
                current_bootstyle = DANGER
            elif level == "success":
                current_bootstyle = SUCCESS
            elif level == "info":
                current_bootstyle = INFO
            try:
                self.status_bar_widget.configure(bootstyle=current_bootstyle)
            except tk.TclError as e:
                print(f"Warning: Could not apply bootstyle '{current_bootstyle}': {e}")
                if level == "error":
                     self.status_bar_widget.configure(foreground="red")
                elif level == "success":
                     self.status_bar_widget.configure(foreground="green")
                else:
                    try:
                        default_fg = ttk.Style().lookup("TLabel", "foreground")
                        self.status_bar_widget.configure(foreground=default_fg)
                    except tk.TclError:
                        self.status_bar_widget.configure(foreground="black") 
        elif self.status_bar_widget:
            if level == "error":
                self.status_bar_widget.configure(foreground="red")
            elif level == "success":
                self.status_bar_widget.configure(foreground="green")
            else: 
                try:
                    default_fg = ttk.Style().lookup("TLabel", "foreground")
                    self.status_bar_widget.configure(foreground=default_fg)
                except tk.TclError:
                     self.status_bar_widget.configure(foreground="black")

        

    def _update_result_text(self, content: str, is_error: bool = False):
        self.result_text.configure(state='normal')
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.INSERT, content)
        self.result_text.tag_remove("error_tag", "1.0", tk.END)
        if is_error:
            self.result_text.tag_add("error_tag", "1.0", tk.END)
            self.result_text.tag_config("error_tag", foreground="red")
        self.result_text.configure(state='disabled')

    def apply_jq(self):
        self._update_result_text("")
        json_input = self.json_input_text.get("1.0", "end-1c").strip()
        jq_expr = self.jq_expression_entry.get().strip()

        if not json_input:
            self._update_result_text("Error: JSON input is empty.", is_error=True)
            self.set_status("JSON input is empty.", "error")
            return
        
        if not jq_expr:
            self._update_result_text("Error: JQ expression is empty.", is_error=True)
            self.set_status("JQ expression is empty.", "error")
            return

        try:
            # Validate JSON input client-side first
            try:
                json.loads(json_input)
            except json.JSONDecodeError as je:
                self._update_result_text(f"Invalid JSON input: {str(je)}", is_error=True)
                self.set_status("Invalid JSON input.", "error")
                return

            # Process using the logic class
            result = self.jq_logic.process_json(json_input, jq_expr)

            # Try pretty-print if valid JSON, otherwise raw
            try:
                parsed_result = json.loads(result)
                formatted_result = json.dumps(parsed_result, indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                formatted_result = result 

            self._update_result_text(formatted_result)
            self.set_status("JQ expression applied successfully.", "success")

        except JQProcessorError as e:
            self._update_result_text(f"JQ Processing Error: {str(e)}", is_error=True)
            self.set_status("JQ processing failed.", "error")
        except Exception as e: 
            self._update_result_text(f"An unexpected application error occurred: {str(e)}", is_error=True)
            self.set_status("An unexpected error occurred.", "error")

    def load_json(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = file.read()
                json.loads(data) 
                self.json_input_text.delete("1.0", tk.END)
                self.json_input_text.insert(tk.INSERT, data)
                self.set_status(f"Loaded JSON from: {file_path}", "success")
                self._update_result_text("") 
            except json.JSONDecodeError as je:
                messagebox.showerror("JSON Load Error", f"The file does not contain valid JSON.\n\n{str(je)}")
                self.set_status("Failed to load invalid JSON file.", "error")
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load file: {str(e)}")
                self.set_status("File load error.", "error")

    def copy_result(self):
        result = self.result_text.get("1.0", "end-1c")
        if not result.strip():
            self.set_status("Nothing to copy.", "info")
            messagebox.showinfo("Copy Result", "Result is empty, nothing to copy.")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(result)
        self.root.update()
        self.set_status("Result copied to clipboard.", "success")
        messagebox.showinfo("Copied", "Result copied to clipboard.")

    def clear_all(self):
        self.json_input_text.delete("1.0", tk.END)
        self.jq_expression_entry.delete(0, tk.END)
        self._update_result_text("")
        self.set_status("All fields cleared.")

    def format_input_json(self):
        json_input = self.json_input_text.get("1.0", "end-1c").strip()
        if not json_input:
            self.set_status("JSON input is empty, nothing to format.", "info")
            return
        
        try:
            parsed_json = json.loads(json_input)
            formatted_json = json.dumps(parsed_json, indent=4, ensure_ascii=False)
            self.json_input_text.delete("1.0", tk.END)
            self.json_input_text.insert(tk.INSERT, formatted_json)
            self.set_status("Input JSON formatted successfully.", "success")
        except json.JSONDecodeError as e:
            self.set_status("Invalid JSON in input, cannot format.", "error")
            messagebox.showerror("Format Error", f"The input field does not contain valid JSON.\n\n{str(e)}")


def main():
    if TTKBOOTSTRAP_AVAILABLE:
        root = ttk.Window(themename="superhero")
    else:
        root = tk.Tk()

    app = JQProcessorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()