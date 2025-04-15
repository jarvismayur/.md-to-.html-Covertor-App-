import markdown
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.scrolledtext as scrolledtext
from tkhtmlview import HTMLLabel
import os
import re

class MarkdownConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Markdown to HTML Converter")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Theme variables
        self.is_dark_theme = False
        self.show_raw_html = False
        self.light_theme = {
            'bg': '#ffffff',
            'fg': '#000000',
            'text_bg': '#ffffff',
            'text_fg': '#000000',
            'button_bg': '#f0f0f0',
            'button_fg': '#000000',
            'status_bg': '#e0e0e0'
        }
        self.dark_theme = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'text_bg': '#1e1e1e',
            'text_fg': '#ffffff',
            'button_bg': '#3c3c3c',
            'button_fg': '#ffffff',
            'status_bg': '#1e1e1e'
        }
        
        self.setup_ui()
        self.apply_theme()
        
    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create toolbar
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        self.open_button = ttk.Button(toolbar, text="Open Markdown File", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.convert_button = ttk.Button(toolbar, text="Convert", command=self.convert)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(toolbar, text="Save HTML", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # Toggle buttons
        self.theme_button = ttk.Button(toolbar, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.pack(side=tk.RIGHT, padx=5)
        
        self.toggle_view_button = ttk.Button(toolbar, text="Toggle HTML/Preview", command=self.toggle_view)
        self.toggle_view_button.pack(side=tk.RIGHT, padx=5)
        
        # Create paned window for split view
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (Markdown)
        left_frame = ttk.Frame(paned)
        ttk.Label(left_frame, text="Markdown Input").pack()
        self.markdown_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD)
        self.markdown_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        paned.add(left_frame, weight=1)
        
        # Right panel (HTML Preview/Raw HTML)
        right_frame = ttk.Frame(paned)
        self.right_label = ttk.Label(right_frame, text="HTML Preview")
        self.right_label.pack()
        
        # Create both HTML preview and raw HTML text widgets
        self.html_preview = HTMLLabel(right_frame)
        self.html_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        
        # Initially show HTML preview
        self.html_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.html_text.pack_forget()
        
        paned.add(right_frame, weight=1)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        # Bind text change event
        self.markdown_text.bind('<<Modified>>', self.on_text_change)
        
    def apply_theme(self):
        theme = self.dark_theme if self.is_dark_theme else self.light_theme
        self.root.configure(bg=theme['bg'])
        
        # Apply theme to all widgets
        for widget in self.root.winfo_children():
            if isinstance(widget, (ttk.Frame, ttk.Label, ttk.Button)):
                widget.configure(style='Custom.TFrame' if isinstance(widget, ttk.Frame) else 'Custom.TLabel' if isinstance(widget, ttk.Label) else 'Custom.TButton')
        
        self.markdown_text.configure(
            bg=theme['text_bg'],
            fg=theme['text_fg'],
            insertbackground=theme['text_fg']
        )
        
        self.html_text.configure(
            bg=theme['text_bg'],
            fg=theme['text_fg'],
            insertbackground=theme['text_fg']
        )
        
        self.status_bar.configure(
            background=theme['status_bg'],
            foreground=theme['fg']
        )
        
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        self.convert()
        
    def toggle_view(self):
        self.show_raw_html = not self.show_raw_html
        if self.show_raw_html:
            self.right_label.config(text="Raw HTML")
            self.html_preview.pack_forget()
            self.html_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            self.right_label.config(text="HTML Preview")
            self.html_text.pack_forget()
            self.html_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.convert()
        
    def on_text_change(self, event):
        if self.markdown_text.edit_modified():
            self.convert()
            self.markdown_text.edit_modified(False)
            
    def convert_markdown_to_html(self, md_text):
        try:
            # Convert Markdown to HTML with table extension
            html = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
            
            # Create a proper HTML structure
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    {html}
</body>
</html>"""
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(full_html, 'html.parser')
            
            # Apply classes based on style.css
            for i in range(1, 7):  # h1 to h6
                for tag in soup.find_all(f'h{i}'):
                    tag['class'] = f'h{i}'
            
            for tag in soup.find_all('p'):
                tag['class'] = 'text-large-normal'
            
            # Handle code blocks with language specification
            for pre in soup.find_all('pre'):
                code = pre.find('code')
                if code:
                    # Extract language from class
                    lang_class = code.get('class', [''])[0]
                    if lang_class.startswith('language-'):
                        lang = lang_class[9:]  # Remove 'language-' prefix
                        pre['class'] = f'pre pre-{lang}'
                        code['class'] = f'code code-{lang}'
                    else:
                        pre['class'] = 'pre'
                        code['class'] = 'code'
            
            for tag in soup.find_all('blockquote'):
                tag['class'] = 'blockquote'
            
            for tag in soup.find_all('ul'):
                tag['class'] = 'ul'
            
            for tag in soup.find_all('ol'):
                tag['class'] = 'ol'
            
            for tag in soup.find_all('li'):
                tag['class'] = 'li'
            
            for tag in soup.find_all('a'):
                tag['class'] = 'default-link'
            
            # Enhanced table handling
            for table in soup.find_all('table'):
                table['class'] = 'table'
                # Add thead and tbody if not present
                if not table.find('thead'):
                    first_row = table.find('tr')
                    if first_row:
                        thead = soup.new_tag('thead')
                        thead.append(first_row.extract())
                        table.insert(0, thead)
                if not table.find('tbody'):
                    tbody = soup.new_tag('tbody')
                    for row in table.find_all('tr'):
                        tbody.append(row.extract())
                    table.append(tbody)
            
            for tag in soup.find_all('th'):
                tag['class'] = 'th'
            
            for tag in soup.find_all('td'):
                tag['class'] = 'td'
            
            for tag in soup.find_all('tr'):
                tag['class'] = 'tr'
            
            return str(soup)
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error converting Markdown to HTML: {str(e)}")
            return ""
            
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.markdown_text.delete("1.0", tk.END)
                    self.markdown_text.insert(tk.END, file.read())
                self.status_bar.config(text=f"Opened: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error opening file: {str(e)}")
                
    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.html_preview.html)
                self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "HTML file saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                
    def convert(self):
        md_text = self.markdown_text.get("1.0", tk.END)
        converted_html = self.convert_markdown_to_html(md_text)
        if self.show_raw_html:
            self.html_text.delete("1.0", tk.END)
            self.html_text.insert(tk.END, converted_html)
        else:
            self.html_preview.set_html(converted_html)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownConverter(root)
root.mainloop()
