# import tkinter as tk
# import requests
# import datetime

# def show_main_screen():
#     clear_screen()
#     title = tk.Label(root, text="Visitor Management System", font=("Arial", 16, "bold"))
#     title.pack(pady=15)
#     create_btn = tk.Button(root, text="Add Visitor", font=("Arial", 12), command=show_create_form)
#     create_btn.pack(anchor="w", padx=20, pady=10)

# def show_create_form():
#     clear_screen()
#     tk.Label(root, text="Create Visitor", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=10)

#     global name_entry, mobile_entry
#     tk.Label(root, text="Name:").pack(anchor="w", padx=20)
#     name_entry = tk.Entry(root, width=30)
#     name_entry.pack(anchor="w", padx=20, pady=5)

#     tk.Label(root, text="Mobile:").pack(anchor="w", padx=20)
#     mobile_entry = tk.Entry(root, width=30)
#     mobile_entry.pack(anchor="w", padx=20, pady=5)

#     tk.Button(root, text="Save", command=save_visitor).pack(anchor="w", padx=20, pady=10)
#     tk.Button(root, text="⬅ Back", command=show_main_screen).pack(anchor="w", padx=20, pady=5)

# def save_visitor():
#     name = name_entry.get()
#     phone = mobile_entry.get()
    
#     now = datetime.datetime.now().isoformat()

#     payload = {
#         "receptionistId": "1",
#         "visitStartTime": now,
#         "visitEndTime": now,
#         "visitorInfoList": [
#             {
#                 "VisitorInfo": {
#                     "visitorGivenName": name,
#                     "phoneNo": phone
#                 }
#             }
#         ]
#     }

#     response = requests.post("http://127.0.0.1:8000/visitor", json=payload)
#     print("API Response:", response.json())

# def clear_screen():
#     for widget in root.winfo_children():
#         widget.destroy()

# root = tk.Tk()
# root.title("Visitor Management System")
# root.geometry("600x400")
# show_main_screen()
# root.mainloop()


import os
import sys
import runpy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
LOGIN_DIR = os.path.join(SRC_DIR, "Homepage")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if LOGIN_DIR not in sys.path:
    sys.path.insert(0, LOGIN_DIR)

def start_login():
    """Starts the login window"""
    print("Starting Visitor Management System login...")
    runpy.run_path(os.path.join(LOGIN_DIR, "ui.py"), run_name="__main__")

if __name__ == "__main__":
    start_login()











