import tkinter as tk
from tkinter import ttk
import webbrowser

class WebPageOpener(tk.Frame):
    def __init__(self, parent, config_file="open_web.txt"):
        super().__init__(parent)
        self.parent = parent
        self.config = self.read_config(config_file)
        self.input_entries = {}

        self.create_widgets()
        self.update_input_fields()

    def read_config(self, config_file):
        config = {}
        with open(config_file) as f:
            for line in f:
                name, url = line.strip().split(',')
                config[name] = url
        return config

    def create_widgets(self):
        self.combo = ttk.Combobox(self, values=list(self.config.keys()))
        self.combo.current(0)
        self.combo.bind("<<ComboboxSelected>>", self.update_input_fields)
        self.combo.pack(fill=tk.X, padx=5, pady=5)

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.open_button = tk.Button(self, text="OPEN", command=self.open_webpage)
        self.open_button.pack(fill=tk.X, padx=5, pady=5)

    def update_input_fields(self, *args):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

        selected = self.combo.get()
        if selected in self.config:
            url = self.config[selected]
            params = [part.split('#')[1] for part in url.split('##')[1:]]
            
            self.input_entries.clear()
            for param in params:
                label = tk.Label(self.input_frame, text=f"{param}:")
                label.pack(side=tk.TOP, anchor="w")
                entry = tk.Entry(self.input_frame)
                entry.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
                self.input_entries[param] = entry

    def open_webpage(self):
        selected = self.combo.get()
        if selected in self.config:
            url = self.config[selected]
            for param, entry in self.input_entries.items():
                value = entry.get()
                url = url.replace(f"#{param}#", param).replace(f"#value{param[-1]}#", value)
            webbrowser.open(url)

# Example usage in an existing Tkinter app
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Web Page Opener")

    opener = WebPageOpener(root)
    opener.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
