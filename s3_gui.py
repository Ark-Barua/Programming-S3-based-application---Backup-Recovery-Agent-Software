import customtkinter as ctk
import json, os, threading
from tkinter import messagebox
from s3_operations import *
from s3_operations import upload_custom_image


ctk.set_default_color_theme("blue")
SESSION_FILE = "session.json"
USER_DB = "users.json"

# ---------------- AUTH ----------------
class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x400")
        ctk.set_appearance_mode("light")
        self.build_login_screen()

        # Auto-login if session exists
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE) as f:
                session = json.load(f)
                if session.get("remember") and session.get("username"):
                    self.destroy()
                    DashboardApp(session["username"]).mainloop()

    def build_login_screen(self):
        self.clear()
        ctk.CTkLabel(self, text="Login to AWS S3 Automation", font=("Arial", 20)).pack(pady=20)
        self.username = ctk.CTkEntry(self, placeholder_text="Username")
        self.username.pack(pady=10)
        self.password = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.password.pack(pady=10)
        self.remember_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Remember Me", variable=self.remember_var).pack(pady=5)
        ctk.CTkButton(self, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(self, text="Sign Up", fg_color="transparent", command=self.build_signup_screen).pack()

    def build_signup_screen(self):
        self.clear()
        ctk.CTkLabel(self, text="Create Account", font=("Arial", 20)).pack(pady=20)
        self.new_username = ctk.CTkEntry(self, placeholder_text="New Username")
        self.new_username.pack(pady=10)
        self.new_password = ctk.CTkEntry(self, placeholder_text="New Password", show="*")
        self.new_password.pack(pady=10)
        ctk.CTkButton(self, text="Sign Up", command=self.signup).pack(pady=10)
        ctk.CTkButton(self, text="Back", fg_color="transparent", command=self.build_login_screen).pack()

    def login(self):
        uname, pword = self.username.get(), self.password.get()
        if self.validate_user(uname, pword):
            with open(SESSION_FILE, 'w') as f:
                json.dump({"username": uname, "remember": self.remember_var.get()}, f)
            self.destroy()
            DashboardApp(uname).mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    def signup(self):
        uname, pword = self.new_username.get(), self.new_password.get()
        if self.register_user(uname, pword):
            messagebox.showinfo("Success", "Account created.")
            self.build_login_screen()
        else:
            messagebox.showerror("Error", "User already exists.")

    def validate_user(self, uname, pword):
        if not os.path.exists(USER_DB): return False
        with open(USER_DB, 'r') as f:
            users = json.load(f)
        return users.get(uname) == pword

    def register_user(self, uname, pword):
        users = {}
        if os.path.exists(USER_DB):
            with open(USER_DB, 'r') as f:
                users = json.load(f)
        if uname in users: return False
        users[uname] = pword
        with open(USER_DB, 'w') as f:
            json.dump(users, f)
        return True

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

# ---------------- DASHBOARD ----------------
class DashboardApp(ctk.CTk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"Welcome, {username}")
        self.geometry("1000x670")
        self.mode = "light"
        self.progress = None
        self.build_ui()

    def build_ui(self):
        ctk.set_appearance_mode("light")
        ctk.CTkLabel(self, text="AWS S3 Automation", font=("Arial", 24, "bold")).pack(pady=20)

        frame = ctk.CTkFrame(self)
        frame.pack(pady=10)

        actions = [
            ("Create Bucket", create_bucket_if_not_exists),
            ("Enable Versioning", enable_versioning),
            ("Upload JPG", upload_jpg_file),
	    ("Upload Custom Image", upload_custom_image),
            ("Validated Upload", validated_upload),
            ("Modify & Upload", modify_and_upload),
            ("Simple Upload", simple_upload),
            ("Create ZIP", create_zip),
            ("Upload ZIP", upload_zip),
            ("Move JPGs", move_jpg_files),
            ("List Bucket Files", list_bucket_files),
            ("Start Sync & Backup", self.start_sync_backup),
        ]

        for label, func in actions:
            ctk.CTkButton(frame, text=label, width=250,
                          command=lambda f=func: threading.Thread(target=self.call_with_progress, args=(f,), daemon=True).start()
                          ).pack(pady=5)

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, orientation="horizontal", width=300)
        self.progress.set(0)
        self.progress.pack(pady=15)

        # Output log
        self.output = ctk.CTkTextbox(self, height=250, width=950)
        self.output.pack(pady=10)
        self.redirect_logs()

        # Toggle mode + logout
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(pady=10)

        ctk.CTkButton(bottom_frame, text="Toggle Theme", command=self.toggle_mode).pack(side="left", padx=20)
        ctk.CTkButton(bottom_frame, text="Logout", fg_color="red", command=self.logout).pack(side="left", padx=20)

    def call_with_progress(self, func):
        self.progress.set(0)
        self.progress.start()
        try:
            func()
        except Exception as e:
            print(f"[ERROR] {e}")
        self.progress.stop()
        self.progress.set(1.0)

    def toggle_mode(self):
        self.mode = "dark" if self.mode == "light" else "light"
        ctk.set_appearance_mode(self.mode)

    def logout(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        self.destroy()
        AuthApp().mainloop()

    def start_sync_backup(self):
        threading.Thread(target=start_sync, daemon=True).start()
        threading.Thread(target=start_backup, daemon=True).start()
        print("Sync & Backup started.")

    def redirect_logs(self):
        import sys
        class Redirect:
            def __init__(self, widget): self.widget = widget
            def write(self, text): self.widget.insert("end", text); self.widget.see("end")
            def flush(self): pass
        sys.stdout = Redirect(self.output)
        sys.stderr = Redirect(self.output)

# ---------- MAIN ----------
if __name__ == "__main__":
    AuthApp().mainloop()
