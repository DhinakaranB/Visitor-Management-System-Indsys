# import tkinter as tk
# from tkinter import messagebox
# import os, sys, runpy

# # 🧭 Path Setup
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# API_DIR = os.path.join(BASE_DIR, "Api")
# HOMEPAGE_DIR = os.path.join(BASE_DIR, "Homepage")

# if API_DIR not in sys.path:
#     sys.path.insert(0, API_DIR)
# if HOMEPAGE_DIR not in sys.path:
#     sys.path.insert(0, HOMEPAGE_DIR)

# # Optional future import (for Hikvision validation)
# # from Api import common_signature_api as api

# # ---------------- GUI SETUP ---------------- #
# root = tk.Tk()
# root.title("Visitor Management System - Login")
# root.geometry("400x320")
# root.config(bg="white")

# # 🎨 Styles
# TITLE_COLOR = "#2C3E50"
# BUTTON_COLOR = "#3498DB"

# # ---------------- Widgets ---------------- #
# tk.Label(
#     root, text="🔐 Visitor Management System",
#     font=("Segoe UI", 16, "bold"), bg="white", fg=TITLE_COLOR
# ).pack(pady=(30, 5))

# tk.Label(root, text="Sign in to continue", font=("Segoe UI", 10), bg="white", fg="#7F8C8D").pack(pady=(0, 20))

# # Username
# tk.Label(root, text="Username", font=("Segoe UI", 10), bg="white").pack(anchor="w", padx=50)
# username_entry = tk.Entry(root, width=30, font=("Segoe UI", 11))
# username_entry.pack(pady=(5, 15))

# # Password
# tk.Label(root, text="Password", font=("Segoe UI", 10), bg="white").pack(anchor="w", padx=50)
# password_entry = tk.Entry(root, show="*", width=30, font=("Segoe UI", 11))
# password_entry.pack(pady=(5, 20))


# # ---------------- Login Function ---------------- #
# def validate_login():
#     user = username_entry.get().strip()
#     pwd = password_entry.get().strip()

#     if not user or not pwd:
#         messagebox.showwarning("Missing Info", "Please enter both username and password!")
#         return

#     # 🔒 Hardcoded login (you can replace later)
#     if user == "admin" and pwd == "1234":
#         messagebox.showinfo("Login Success", f"Welcome {user} 😎")

#         # Optional: validate Hikvision connection (future)
#         # success, info = api.validate_hikvision_connection()
#         # if not success:
#         #     messagebox.showerror("API Error", f"Hikvision API not reachable.\nDetails: {info}")
#         #     return

#         root.destroy()  # close login window
#         runpy.run_path(os.path.join(HOMEPAGE_DIR, "Ui.py"), run_name="__main__")

#     else:
#         messagebox.showerror("Login Failed", "Invalid username or password!")


# # ---------------- Button ---------------- #
# tk.Button(
#     root,
#     text="Login",
#     command=validate_login,
#     bg=BUTTON_COLOR,
#     fg="white",
#     font=("Segoe UI", 11, "bold"),
#     relief="flat",
#     width=15
# ).pack(pady=10)

# # Footer
# tk.Label(
#     root,
#     text="© 2025 Indsys Holdings. All Rights Reserved.",
#     font=("Segoe UI", 9),
#     bg="white",
#     fg="#95A5A6"
# ).pack(side="bottom", pady=10)

# # Run window
# root.mainloop()
