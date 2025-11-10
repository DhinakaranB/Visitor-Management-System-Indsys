# ui.py

import tkinter as tk
from tkinter import ttk
import add_visitor as visitor_form
import common_api
import sys
import os
import visitor_list_single as single_list
# import pdb; pdb.set_trace()


# Colors
BG_COLOR = "#F4F6F7"
NAV_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#3498DB"
TEXT_COLOR = "#2C3E50"
SUCCESS_COLOR = "#2ECC71"
DANGER_COLOR = "#E74C3C"
SECONDARY_COLOR = "#95A5A6"

root = None
content_frame = None  # Dynamic area


# -----------------------------------
# Core Utility Functions
# -----------------------------------

def clear_content():
    """Clears all widgets from the central content frame."""
    if content_frame:
        for widget in content_frame.winfo_children():
            widget.destroy()


def close_application():
    """Closes the main Tkinter application."""
    if root:
        root.quit()
        root.destroy()


# -----------------------------------
# Navigation Screen Functions
# -----------------------------------

def show_home():
    """Displays the default home welcome screen."""
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        home_center = tk.Frame(content_frame, bg=BG_COLOR)
        home_center.grid(row=0, column=0, sticky="nsew")

        home_center.grid_rowconfigure(0, weight=1)
        home_center.grid_rowconfigure(2, weight=1)
        home_center.grid_columnconfigure(0, weight=1)

        text_frame = tk.Frame(home_center, bg=BG_COLOR)
        text_frame.grid(row=1, column=0, padx=20, pady=20)

        tk.Label(
            text_frame,
            text="Welcome to Visitor Management System",
            font=("Segoe UI", 22, "bold"),
            bg=BG_COLOR,
            fg=PRIMARY_COLOR,
        ).pack(pady=(20, 10))

        tk.Label(
            text_frame,
            text="Use the navigation bar above to manage visitor appointments and access control.",
            font=("Segoe UI", 12),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        ).pack(pady=(0, 20))


def show_add_visitor():
    """Clears the screen and loads the responsive visitor registration form."""
    clear_content()
    visitor_form.show_create_form(content_frame, show_home, close_application)

def show_single_visitor_list_external():
    clear_content()
    single_list.show_single_visitor_list(content_frame)



def show_door_list():
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        lbl = tk.Label(
            content_frame,
            text="🚪 Door List (Coming Soon)",
            font=("Segoe UI", 14),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        lbl.grid(row=0, column=0, padx=20, pady=40)


def show_access_control():
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        lbl = tk.Label(
            content_frame,
            text="🛂 Access Control (Coming Soon)",
            font=("Segoe UI", 14),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        lbl.grid(row=0, column=0, padx=20, pady=40)


# -----------------------------------
# Visitor List Screens
# -----------------------------------

def show_single_visitor_list_external():
    """Opens the Single Visitor List screen."""
    clear_content()
    import visitor_list_single as single_list  # Avoid circular import
    single_list.show_single_visitor_list(content_frame)


def show_bulk_visitor_list():
    """Displays Bulk Visitor List placeholder."""
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        lbl = tk.Label(
            content_frame,
            text="📦 Bulk Visitor List (Coming Soon)",
            font=("Segoe UI", 14),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        lbl.grid(row=0, column=0, padx=20, pady=40)


# -----------------------------------
# Navigation Bar Setup
# -----------------------------------

def setup_navbar():
    """Creates and returns the navigation bar frame."""
    nav = tk.Frame(root, bg=NAV_COLOR, relief="raised", bd=1)

    # Create dropdown for Visitor List
    visitor_menu = tk.Menu(nav, tearoff=0, bg="white", fg=TEXT_COLOR, font=("Segoe UI", 10))
    visitor_menu.add_command(label="📋 Single Visitor List", command=show_single_visitor_list_external)
    visitor_menu.add_command(label="📦 Bulk Visitor List", command=show_bulk_visitor_list)

    # Function to open dropdown on click
    def show_visitor_dropdown(event):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        visitor_menu.tk_popup(x, y)

    # Define navbar buttons
    buttons = [
        ("➕ Visitor Registration", show_add_visitor),
        ("👥 Visitor List ▼", show_visitor_dropdown),
        ("🚪 Door List", show_door_list),
        ("🛂 Access Control", show_access_control),
        ("❌ Exit", close_application),
    ]

    for text, cmd in buttons:
        btn = ttk.Button(nav, text=text, style="Nav.TButton")
        btn.pack(side="left", padx=8, pady=5)
        if text.startswith("👥"):
            btn.bind("<Button-1>", cmd)
        else:
            btn.config(command=cmd)

    return nav


# -----------------------------------
# Styles and Initialization
# -----------------------------------

def setup_styles(style):
    """Configures the custom ttk styles used application-wide."""
    style.theme_use("clam")

    # Navigation
    style.configure(
        "Nav.TButton",
        font=("Segoe UI", 10, "bold"),
        foreground="white",
        background=PRIMARY_COLOR,
        padding=6,
        borderwidth=0,
    )
    style.map("Nav.TButton", background=[("active", "#2E86C1")])

    # Inputs
    style.configure("TEntry", fieldbackground="white", foreground=TEXT_COLOR, bordercolor=SECONDARY_COLOR, borderwidth=1)
    style.configure("TRadiobutton", background=BG_COLOR, foreground=TEXT_COLOR)

    # Buttons
    style.configure(
        "TSuccess.TButton",
        foreground="white",
        background=SUCCESS_COLOR,
        font=("Segoe UI", 11, "bold"),
        padding=(10, 5),
        relief="flat",
    )
    style.map("TSuccess.TButton", background=[("active", "#27AE60")])

    style.configure(
        "TSecondary.TButton",
        foreground="white",
        background=SECONDARY_COLOR,
        font=("Segoe UI", 10),
        padding=(10, 5),
        relief="flat",
    )
    style.map("TSecondary.TButton", background=[("active", "#7F8C8D")])

    style.configure(
        "TInfo.TButton",
        font=("Segoe UI", 10, "bold"),
        background=PRIMARY_COLOR,
        foreground="white",
        relief="flat",
        padding=(5, 5),
    )
    style.map("TInfo.TButton", background=[("active", "#2980B9")])


def init_ui():
    """Initializes the main window and layout using grid for responsiveness."""
    global root, content_frame
    root.title("Visitor Management System")
    root.geometry("1000x650")
    root.configure(bg=BG_COLOR)

    # Main layout grid
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=0)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=0)
    root.grid_columnconfigure(0, weight=1)

    # Header
    header = tk.Label(
        root,
        text="Visitor Management System",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
    )
    header.grid(row=0, column=0, sticky="ew", pady=(15, 5))

    # Navbar
    nav = setup_navbar()
    nav.grid(row=1, column=0, sticky="ew")

    # Content area
    content_frame = tk.Frame(root, bg=BG_COLOR)
    content_frame.grid(row=2, column=0, sticky="nsew")

    # Footer
    footer = tk.Frame(root, bg=BG_COLOR)
    footer.grid(row=3, column=0, sticky="ew", pady=10)
    tk.Label(
        footer,
        text="© 2025 Copyright by Indsys Holdings - All rights reserved.",
        font=("Segoe UI", 9),
        bg=BG_COLOR,
        fg="#7F8C8D",
    ).pack(side="left", padx=15)

    # Show home screen
    show_home()


# -----------------------------------
# Main Entry Point
# -----------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    setup_styles(ttk.Style(root))
    init_ui()
    root.mainloop()
