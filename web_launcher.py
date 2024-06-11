import tkinter as tk
from tkinter import ttk
import re
import webbrowser

class WebPageOpener:
    def __init__(self, root, paramter_string):
        self.root = root
        self.paramter_string = paramter_string

        self.frame = ttk.Frame(root, padding="10")
        self.frame.pack(fill="both", expand=True)

        self.placeholders = self.extract_placeholders(paramter_string)
        self.entry_vars = {}

        self.create_input_fields()
        self.create_link_frame()

    def extract_placeholders(self, param_string):
        placeholders = set(re.findall(r"#(.*?)#", param_string))
        return placeholders

    def update_links(self, *args):
        values = {placeholder: self.entry_vars[placeholder].get().strip() for placeholder in self.placeholders}
        
        links = []
        
        for line in self.paramter_string.strip().split('\n'):
            name, url = line.split(',')
            
            for placeholder, value in values.items():
                url = url.replace(f'#{placeholder}#', value)
            
            # Check if all required values are provided
            if any(f'#{placeholder}#' in line and not values[placeholder] for placeholder in self.placeholders):
                continue
            
            links.append((name, url))
        
        self.display_links(links)

    def display_links(self, links):
        for widget in self.link_frame.winfo_children():
            widget.destroy()
        
        link_frame = tk.Frame(self.link_frame)
        link_frame.pack()

        for i, (name, url) in enumerate(links):
            link_label = tk.Label(link_frame, text=name, foreground="blue", cursor="hand2")
            link_label.grid(row=0, column=2*i)
            link_label.bind("<Button-1>", lambda e, url=url: self.open_link(url))
            
            if i < len(links) - 1:
                separator_label = tk.Label(link_frame, text=" | ")
                separator_label.grid(row=0, column=2*i+1)

    def open_link(self, url):
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        webbrowser.open(url)

    def create_input_fields(self):
        row = 0
        for placeholder in self.placeholders:
            ttk.Label(self.frame, text=f"{placeholder}:").grid(column=0, row=row, sticky="w")
            entry_var = tk.StringVar()
            self.entry_vars[placeholder] = entry_var
            entry = ttk.Entry(self.frame, textvariable=entry_var, width=30)
            entry.grid(column=1, row=row, sticky="ew")
            entry_var.trace_add("write", self.update_links)
            row += 1

    def create_link_frame(self):
        self.link_frame = ttk.Frame(self.frame)
        self.link_frame.grid(column=0, row=len(self.placeholders), columnspan=2, sticky="ew")

if __name__ == "__main__":
    paramter_string = '''
    SNOW,https:\\aaa.bbb.com\\search?CHANGE=#change#
    ICR,https:\\aaa.bbb.com\\search?CHANGE=#change#&BB=#server#
    IN,https:\\aaa.bbb.com\\search?IN#value1#&BB=#incident#
    '''

    root = tk.Tk()
    root.title("Web Page Opener")

    app = WebPageOpener(root, paramter_string)

    root.mainloop()
