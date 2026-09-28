import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
import sys
from datetime import datetime
# DPI awareness
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.tk.call('tk', 'scaling', 1.5)
except:
    root = tk.Tk()


PASSWORDS_DIR = "passwords"

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

SETTINGS_FILE = resource_path("settings.json")

def SetIcon(rt):
    icon_path = resource_path("logo.ico")

    if os.path.exists(icon_path):
        rt.iconbitmap(icon_path)



def generate_password(length=12,
                      uppercase_ratio=0.25,
                      lowercase_ratio=0.25,
                      digits_ratio=0.25,
                      symbols_ratio=0.25):
    total_ratio = uppercase_ratio + lowercase_ratio + digits_ratio + symbols_ratio
    if not 0.99 <= total_ratio <= 1.01:
        raise ValueError("The sum of all parts must be equal to 1.")

    num_uppercase = round(length * uppercase_ratio)
    num_lowercase = round(length * lowercase_ratio)
    num_digits = round(length * digits_ratio)
    num_symbols = length - (num_uppercase + num_lowercase + num_digits)

    password_chars = (
        random.choices(string.ascii_uppercase, k=num_uppercase) +
        random.choices(string.ascii_lowercase, k=num_lowercase) +
        random.choices(string.digits, k=num_digits) +
        random.choices(string.punctuation, k=num_symbols)
    )

    random.shuffle(password_chars)
    return ''.join(password_chars)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return { # import from settings.json
        "uppercase_ratio": 0.0,
        "lowercase_ratio": 0.0,
        "digits_ratio": 0.0,
        "symbols_ratio": 0.0,
        "slider_min": 0,
        "slider_max": 0
    }


def save_settings():
    settings = {
        "uppercase_ratio": float(uppercase_entry.get()),
        "lowercase_ratio": float(lowercase_entry.get()),
        "digits_ratio": float(digits_entry.get()),
        "symbols_ratio": float(symbols_entry.get()),
        "slider_min": int(slider_min_entry.get()),
        "slider_max": int(slider_max_entry.get())
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    length_slider.config(from_=settings["slider_min"], to=settings["slider_max"])
    messagebox.showinfo("Settings", "Settings are saved and applied.")



def generate_and_display():
    try:
        length = length_slider.get()
        password = generate_password(
            length=length,
            uppercase_ratio=float(uppercase_entry.get()),
            lowercase_ratio=float(lowercase_entry.get()),
            digits_ratio=float(digits_entry.get()),
            symbols_ratio=float(symbols_entry.get())
        )
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(password_entry.get())
    root.update()
    messagebox.showinfo("Copy", "Password copied to clipboard.")


def save_password():
    def save_to_file():
        name = name_entry.get().strip() or f"NoName_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        login = login_entry.get().strip() or "-"
        password = password_entry.get().strip() or "-"
        comment = comment_entry.get().strip() or "-"

        if not os.path.exists(PASSWORDS_DIR):
            os.makedirs(PASSWORDS_DIR)

        filepath = os.path.join(PASSWORDS_DIR, f"{name}.passw")

        # Проверка: существует ли файл
        if os.path.exists(filepath):
            choice = messagebox.askyesnocancel(
                "File already exist",
                f"File '{name}.passw' already exist.\n"
                "Do you want to replace it?\n"
                "Yes - replace\n"
                "No - create new file (name-2)"
            )
            if choice is None:
                return
            elif choice is False:
                i = 2
                new_filepath = os.path.join(PASSWORDS_DIR, f"{name}-{i}.passw")
                while os.path.exists(new_filepath):
                    i += 1
                    new_filepath = os.path.join(PASSWORDS_DIR, f"{name}-{i}.passw")
                filepath = new_filepath

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(name + "\n")
            f.write(login + "\n")
            f.write(password + "\n")
            f.write(comment + "\n")

        messagebox.showinfo("Save", f"Password saved to {filepath}")
        save_win.destroy()

    save_win = tk.Toplevel(root)
    save_win.title("Save password")

    tk.Label(save_win, text="Name:").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(save_win, width=30)
    name_entry.grid(row=0, column=1)

    tk.Label(save_win, text="Login:").grid(row=1, column=0, sticky="w")
    login_entry = tk.Entry(save_win, width=30)
    login_entry.grid(row=1, column=1)

    tk.Label(save_win, text="Comment:").grid(row=2, column=0, sticky="w")
    comment_entry = tk.Entry(save_win, width=30)
    comment_entry.grid(row=2, column=1)

    tk.Button(save_win, text="Save", command=save_to_file).grid(row=3, column=0, columnspan=2)


# UI

root.title("Password generator")
SetIcon(root)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Вкладка генерации
frame_gen = ttk.Frame(notebook)
notebook.add(frame_gen, text="Generation")

password_entry = tk.Entry(frame_gen, width=40)
password_entry.pack(pady=10)

length_slider = tk.Scale(frame_gen, from_=6, to=20, orient="horizontal", label="Password length")
length_slider.pack(pady=10)

tk.Button(frame_gen, text="Generate", command=generate_and_display).pack(pady=5)
tk.Button(frame_gen, text="Copy", command=copy_to_clipboard).pack(pady=5)
tk.Button(frame_gen, text="Save password", command=save_password).pack(pady=5)

tk.Label(frame_gen, text="github.com/SDAN1040/PasswordGenerator").pack(pady=5)

# Вкладка настроек
frame_settings = ttk.Frame(notebook)
notebook.add(frame_settings, text="Settings")

settings = load_settings()

tk.Label(frame_settings, text="Uppercase ratio").grid(row=0, column=0)
uppercase_entry = tk.Entry(frame_settings)
uppercase_entry.insert(0, settings["uppercase_ratio"])
uppercase_entry.grid(row=0, column=1)

tk.Label(frame_settings, text="Lowercase ratio").grid(row=1, column=0)
lowercase_entry = tk.Entry(frame_settings)
lowercase_entry.insert(0, settings["lowercase_ratio"])
lowercase_entry.grid(row=1, column=1)

tk.Label(frame_settings, text="Digits ratio").grid(row=2, column=0)
digits_entry = tk.Entry(frame_settings)
digits_entry.insert(0, settings["digits_ratio"])
digits_entry.grid(row=2, column=1)

tk.Label(frame_settings, text="Symbols ratio").grid(row=3, column=0)
symbols_entry = tk.Entry(frame_settings)
symbols_entry.insert(0, settings["symbols_ratio"])
symbols_entry.grid(row=3, column=1)

tk.Label(frame_settings, text="Min. length").grid(row=4, column=0)
slider_min_entry = tk.Entry(frame_settings)
slider_min_entry.insert(0, settings["slider_min"])
slider_min_entry.grid(row=4, column=1)

tk.Label(frame_settings, text="Max. length").grid(row=5, column=0)
slider_max_entry = tk.Entry(frame_settings)
slider_max_entry.insert(0, settings["slider_max"])
slider_max_entry.grid(row=5, column=1)

tk.Button(frame_settings, text="Save", command=save_settings).grid(row=6, column=0, columnspan=2)




length_slider.config(from_=settings["slider_min"], to=settings["slider_max"])

root.mainloop()
