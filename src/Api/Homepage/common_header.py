import tkinter as tk
from tkinter import ttk

HEADER_BG = "#003B73"     # Navy blue
HEADER_HOVER = "#0058A3"  # Hover blue
HEADER_TEXT = "white"
HEADER_FONT = ("Segoe UI", 11, "bold")

# ----------------------------------------------------------------------
# GLOBAL NAVIGATION HEADER — REUSABLE ON ALL SCREENS
# ----------------------------------------------------------------------
def render_global_header(root, home_fn, add_fn, list_fn, door_fn, access_fn):

    # Clear previous header if exists
    for w in root.grid_slaves(row=0):
        w.destroy()

    header = tk.Frame(root, bg=HEADER_BG, height=45)
    header.grid(row=0, column=0, sticky="ew")
    header.grid_columnconfigure(20, weight=1)

    # Logo / Brand text
    tk.Label(
        header, text="VisitorMS",
        font=("Segoe UI", 15, "bold"), fg="white", bg=HEADER_BG, padx=20
    ).grid(row=0, column=0, sticky="w")

    # Reusable button creator
    def nav_button(text, col, fn):
        lbl = tk.Label(
            header, text=text,
            font=HEADER_FONT,
            fg="white", bg=HEADER_BG,
            padx=18, cursor="hand2"
        )
        lbl.grid(row=0, column=col)

        lbl.bind("<Enter>", lambda e: lbl.config(bg=HEADER_HOVER))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=HEADER_BG))
        lbl.bind("<Button-1>", lambda e: fn())
        return lbl

    # Navigation Buttons
    nav_button("Home",          1, home_fn)
    nav_button("Add Visitor",   2, add_fn)
    nav_button("Visitor List",  3, list_fn)
    nav_button("Door ▼",        4, door_fn)
    nav_button("Access Control",5, access_fn)
