import tkinter as tk
from tkinter import messagebox

def show_visitor_edit(content_frame):
    """Simple Visitor Edit UI – backend can be added later."""

    for widget in content_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(content_frame, bg="white", padx=20, pady=20)
    frame.pack(pady=20)

    tk.Label(frame, text="Visitor Edit", font=("Segoe UI", 18, "bold"), bg="white").grid(row=0, column=0, columnspan=2, pady=10)

    tk.Label(frame, text="Enter Visitor ID:", font=("Segoe UI", 11), bg="white").grid(row=1, column=0, sticky="w")
    visitor_id_entry = tk.Entry(frame, font=("Segoe UI", 11))
    visitor_id_entry.grid(row=1, column=1, pady=5)

    tk.Button(frame, text="Load Visitor", font=("Segoe UI", 10, "bold"),
              command=lambda: messagebox.showinfo("Info", "Edit function coming soon...")).grid(row=2, column=0, columnspan=2, pady=15)
