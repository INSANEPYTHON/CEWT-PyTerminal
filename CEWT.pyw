import tkinter as tk
from tkinter import font, colorchooser, Toplevel, ttk
from tkinter.scrolledtext import ScrolledText
import subprocess
import json
import os
import time  # time kütüphanesini ekledik

class TerminalApp:
    CONFIG_FILE = "terminal_config.json"

    def __init__(self, root):
        self.root = root
        self.root.title("Custom Editable Windows Terminal (CEWT)")

        # Varsayılan Ayarlar
        self.default_config = {
            "font": ("Courier", 10),
            "bg_color": "black",
            "fg_color": "white"
        }

        # Ayarları Yükle
        self.load_config()

        # Menü Çubuğu
        self.menu_bar = tk.Menu(root)
        self.root.config(menu=self.menu_bar)

        # "Edit" Menüsü
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Preferences", command=self.open_preferences_window)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Terminal Çıktı Alanı
        self.output_area = ScrolledText(root, wrap=tk.WORD, font=self.config["font"], bg=self.config["bg_color"], fg=self.config["fg_color"], insertbackground=self.config["fg_color"])
        self.output_area.pack(fill=tk.BOTH, expand=True)
        self.output_area.configure(state=tk.DISABLED)

        # Komut Giriş Alanı
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill=tk.X)

        self.input_label = tk.Label(self.input_frame, text=">>>", font=("Courier", 12))
        self.input_label.pack(side=tk.LEFT, padx=5)

        self.command_entry = tk.Entry(self.input_frame, font=self.config["font"], bg=self.config["bg_color"], fg=self.config["fg_color"], insertbackground=self.config["fg_color"])
        self.command_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.command_entry.bind("<Return>", self.execute_command)

        # Karşılama Mesajı
        self.show_welcome_message()

    def show_welcome_message(self):
        """Show a welcome message at startup."""
        welcome_message = (
            "Welcome to CEWT, Custom Editable Windows Terminal\n"
            "Type your commands below and press Enter.\n"
            "Type 'exit' to close the terminal."
        )
        self.log_output(welcome_message)

    def log_output(self, text):
        """Log text to the terminal output area."""
        self.output_area.configure(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)
        self.output_area.configure(state=tk.DISABLED)

    def execute_command(self, event):
        """Execute a command and display its output."""
        command = self.command_entry.get()
        if not command.strip():
            return

        self.log_output(f">>> {command}")
        self.command_entry.delete(0, tk.END)

        if command.lower() == "exit":
            self.log_output("Closing the terminal...")
            self.root.quit()
        elif command.lower() == "time":
            self.display_time()  # time komutunu işleyelim
        elif command.lower() == "settings":
            self.open_settings()  # Settings komutunu işleyelim
        elif command.lower() == "paint":
            self.open_paint()  # Paint komutunu işleyelim
        elif command.lower() == "notepad":
            self.open_notepad()  # Notepad komutunu işleyelim
        else:
            try:
                result = subprocess.run(command, shell=True, text=True, capture_output=True)
                if result.stdout:
                    self.log_output(result.stdout.strip())
                if result.stderr:
                    self.log_output(result.stderr.strip())
            except Exception as e:
                self.log_output(f"Error: {str(e)}")

    def display_time(self):
        """Display the current local time."""
        current_time = time.localtime()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
        self.log_output(f"Current local time: {formatted_time}")

    def open_settings(self):
        """Open Windows Settings."""
        try:
            subprocess.run("ms-settings:", shell=True)
        except Exception as e:
            self.log_output(f"Error opening Settings: {str(e)}")

    def open_paint(self):
        """Open Paint application."""
        try:
            subprocess.run("mspaint", shell=True)
        except Exception as e:
            self.log_output(f"Error opening Paint: {str(e)}")

    def open_notepad(self):
        """Open Notepad application."""
        try:
            subprocess.run("notepad", shell=True)
        except Exception as e:
            self.log_output(f"Error opening Notepad: {str(e)}")

    def open_preferences_window(self):
        """Open the preferences window to change font and colors."""
        preferences_window = Toplevel(self.root)
        preferences_window.title("Preferences")
        preferences_window.geometry("400x300")

        # Font Seçimi
        tk.Label(preferences_window, text="Font:").pack(anchor=tk.W, padx=10, pady=5)
        font_selector = ttk.Combobox(preferences_window, values=["Courier", "Arial", "Times New Roman", "Verdana", "Helvetica"])
        font_selector.set(self.config["font"][0])
        font_selector.pack(anchor=tk.W, padx=20)

        # Yazı Rengi Seçimi
        tk.Label(preferences_window, text="Text Color:").pack(anchor=tk.W, padx=10, pady=5)
        color_button_fg = tk.Button(preferences_window, text="Select Text Color", command=self.change_text_color)
        color_button_fg.pack(anchor=tk.W, padx=20)

        # Arka Plan Rengi Seçimi
        tk.Label(preferences_window, text="Background Color:").pack(anchor=tk.W, padx=10, pady=5)
        color_button_bg = tk.Button(preferences_window, text="Select Background Color", command=self.change_background_color)
        color_button_bg.pack(anchor=tk.W, padx=20)

        # Ayarları Güncelle
        def apply_preferences():
            selected_font = font_selector.get()
            if selected_font:
                self.config["font"] = (selected_font, 10)
                self.output_area.configure(font=self.config["font"])
                self.command_entry.configure(font=self.config["font"])

            self.save_config()
            preferences_window.destroy()

        def warn_unsaved_changes():
            """Warn the user if preferences are not saved."""
            self.log_output("Warning: Preferences are not saved yet. Make sure to press 'Apply'.")

        apply_button = tk.Button(preferences_window, text="Apply", command=apply_preferences)
        apply_button.pack(anchor=tk.CENTER, pady=20)

        # Uyarı butonu ekleyelim (Eğer kullanıcı Apply'e basmazsa)
        warn_button = tk.Button(preferences_window, text="Warning: Unsaved Changes", command=warn_unsaved_changes, fg="red")
        warn_button.pack(anchor=tk.CENTER, pady=10)

    def change_text_color(self):
        """Change the text color of the terminal."""
        color = colorchooser.askcolor(title="Select Text Color")[1]
        if color:
            self.config["fg_color"] = color
            self.output_area.configure(fg=self.config["fg_color"], insertbackground=self.config["fg_color"])
            self.command_entry.configure(fg=self.config["fg_color"], insertbackground=self.config["fg_color"])

    def change_background_color(self):
        """Change the background color of the terminal."""
        color = colorchooser.askcolor(title="Select Background Color")[1]
        if color:
            self.config["bg_color"] = color
            self.output_area.configure(bg=self.config["bg_color"])
            self.command_entry.configure(bg=self.config["bg_color"])

    def save_config(self):
        """Save the current configuration to a file."""
        try:
            with open(self.CONFIG_FILE, "w") as config_file:
                json.dump(self.config, config_file)
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")

    def load_config(self):
        """Load configuration from a file or use default settings."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as config_file:
                    self.config = json.load(config_file)
            except json.JSONDecodeError:
                print("Error reading config file, using default settings.")
                self.config = self.default_config
        else:
            self.config = self.default_config

# Tkinter Window
if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalApp(root)
    root.geometry("800x600")
    root.mainloop()
