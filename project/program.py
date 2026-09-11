import customtkinter as ctk
import sqlite3
import hashlib
import os
from PIL import Image
import sys

# Функция для корректной работы путей после компиляции в EXE
def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсам, работает и для dev, и для PyInstaller """
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Импортируем логику из нашего чистого main.py
from main import SerafinaBrain

# Файлы теперь ищем через resource_path
DB_FILE = resource_path("serafina_users.db")

SPRITES = {
    "happy": resource_path(os.path.join("avatar", "happy.png")),    
    "neutral": resource_path(os.path.join("avatar", "neutral.png")), 
    "angry": resource_path(os.path.join("avatar", "angry.png")),
    "shy": resource_path(os.path.join("avatar", "shy.png")), 
    "sad": resource_path(os.path.join("avatar", "sad.png")), 
    "default": resource_path(os.path.join("avatar", "neutral.png"))
}

class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        
        w, h = 400, 500
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        
        self.title("Project Serafina: Authentication")
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")

        self.label = ctk.CTkLabel(self, text="PROJECT SERAFINA\nNeural Access", font=("Consolas", 20, "bold"))
        self.label.pack(pady=(40, 30))

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Login", width=250)
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", width=250, show="*")
        self.pass_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(self, text="Authorize", command=self.check_login, fg_color="#333333", hover_color="#555555")
        self.login_btn.pack(pady=20)

        self.test_btn = ctk.CTkButton(self, text="Quick Test Access (Subaru)", command=self.quick_test, 
                                      fg_color="transparent", text_color="gray", hover_color="#f0f0f0")
        self.test_btn.pack(pady=10)

        self.error_label = ctk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()

    def check_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        input_hash = hashlib.sha256(password.encode()).hexdigest()

        if not os.path.exists(DB_FILE):
            self.error_label.configure(text="Error: Database file not found!")
            return

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE username=? AND password_hash=?", (username, input_hash))
            result = cursor.fetchone()
            conn.close()

            if result:
                self.destroy()
                self.on_success(username, result[0]) 
            else:
                self.error_label.configure(text="Access Denied: Invalid Credentials")
        except Exception as e:
            self.error_label.configure(text=f"Database error: {e}")

    def quick_test(self):
        self.destroy()
        self.on_success("Subaru", "admin")


class SerafinaProject(ctk.CTk):
    def __init__(self, username, role):
        super().__init__()
        
        self.brain = SerafinaBrain(username, role)
        
        window_width = 700
        window_height = 950
        x = (self.winfo_screenwidth() // 2) - (window_width // 2)
        y = (self.winfo_screenheight() // 2) - (window_height // 2)
        
        self.title(f"Project Serafina - Logged as {self.brain.username}")
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        ctk.set_appearance_mode("light")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- ВЕРХ: АВАТАР ---
        self.avatar_frame = ctk.CTkFrame(self, fg_color="#f0f0f0", corner_radius=0)
        self.avatar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.avatar_label = ctk.CTkLabel(self.avatar_frame, text="")
        self.avatar_label.pack(pady=15)

        self.progress_endo = ctk.CTkProgressBar(self.avatar_frame, width=450, height=6, progress_color="#333333")
        self.progress_endo.set(self.brain.stats['endorphin'] / 100)
        self.progress_endo.pack(pady=(0, 15))

        # --- ЦЕНТР: ЧАТ ---
        self.chat_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 0))
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.chat_frame, fg_color="#ffffff", text_color="#1a1a1a",
                                      font=("Consolas", 15), border_width=0, padx=20, pady=20)
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.configure(state="disabled")

        # --- НИЗ: ВВОД ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=20)
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Type message...",
                                  fg_color="#f9f9f9", text_color="#1a1a1a", font=("Consolas", 15), height=45)
        self.entry.grid(row=0, column=0, sticky="ew")
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.update_avatar("neutral")

    def update_avatar(self, emotion):
        img_path = SPRITES.get(emotion, SPRITES["default"])
        if os.path.exists(img_path):
            img = Image.open(img_path)
            w, h = img.size
            new_w = 320 
            new_h = int(new_w * (h / w))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
            self.avatar_label.configure(image=ctk_img, text="")

    def send_message(self):
        user_text = self.entry.get()
        if not user_text: return
        self.entry.delete(0, "end")

        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"{self.brain.username}: {user_text}\n")
        self.textbox.configure(state="disabled")

        reply_text, emotion, current_endo = self.brain.process_message(user_text)

        self.update_avatar(emotion)
        self.progress_endo.set(current_endo / 100)
        
        self.textbox.configure(state="normal")
        self.textbox.insert("end", f"Serafina: {reply_text}\n\n")
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

def start_main_app(username, role):
    app = SerafinaProject(username, role)
    app.mainloop()

if __name__ == "__main__":
    login_screen = LoginWindow(on_success=start_main_app)
    login_screen.mainloop()