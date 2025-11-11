import tkinter as tk
from tkinter import ttk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Api import visitor_registerment as visitor_form
from Api import visitor_list_Info as visitor_list
import Api.common_signature_api


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

def show_home():
    """Displays the default home screen."""
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        home_center = tk.Frame(content_frame, bg=BG_COLOR)
        home_center.grid(row=0, column=0, sticky="nsew")

        tk.Label(home_center, text="Welcome to Visitor Management System",
                 font=("Segoe UI", 22, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR).pack(pady=(10, 5))
        tk.Label(home_center,
                 text="Use the navigation bar above to manage visitor appointments and access control.",
                 font=("Segoe UI", 12), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 10))


def show_add_visitor():
    clear_content()
    visitor_form.show_create_form(content_frame, show_home, close_application)

def show_single_visitor_list_external():
    """Display the single visitor list"""
    clear_content()
    visitor_list.show_single_visitor_list(content_frame)



def show_bulk_visitor_list():
    clear_content()
    lbl = tk.Label(content_frame, text="📦 Bulk Visitor List (Coming Soon)",
                   font=("Segoe UI", 14), bg=BG_COLOR, fg=TEXT_COLOR)
    lbl.grid(row=0, column=0, padx=20, pady=40)


def show_door_list():
    """Loads the real Door List UI."""
    clear_content()
    import Api.door_list_Info as door_list
    door_list.show_door_list(content_frame)


def show_access_control():
    clear_content()
    lbl = tk.Label(content_frame, text="🛂 Access Control (Coming Soon)",
                   font=("Segoe UI", 14), bg=BG_COLOR, fg=TEXT_COLOR)
    lbl.grid(row=0, column=0, padx=20, pady=40)


def setup_navbar():
    """Creates and returns the navigation bar frame."""
    nav = tk.Frame(root, bg=NAV_COLOR, relief="raised", bd=1)

    visitor_menu = tk.Menu(nav, tearoff=0, bg="white", fg=TEXT_COLOR, font=("Segoe UI", 10))
    visitor_menu.add_command(label="📋 All Visitor List", command=show_single_visitor_list_external)
    visitor_menu.add_command(label="📦 Visitor List Update", command=show_bulk_visitor_list)

    def show_visitor_dropdown(event):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        visitor_menu.tk_popup(x, y)

    buttons = [
        ("➕ Add Visitor", show_add_visitor),
        ("👥 Visitor List ▼", show_visitor_dropdown),
        ("🚪 Door List", show_door_list),
        ("🛂 Access Control", show_access_control),
        ("❌ Exit", close_application)
    ]

    for text, cmd in buttons:
        btn = ttk.Button(nav, text=text, style="Nav.TButton")
        btn.pack(side="left", padx=8, pady=5)
        if text.startswith("👥"):
            btn.bind("<Button-1>", cmd)
        else:
            btn.config(command=cmd)

    return nav


def setup_styles(style):
    """Configures custom ttk styles."""
    style.theme_use("clam")

    style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"),
                    foreground="white", background=PRIMARY_COLOR, padding=6, borderwidth=0)
    style.map("Nav.TButton", background=[("active", "#2E86C1")])

    style.configure("TEntry", fieldbackground="white", foreground=TEXT_COLOR)
    style.configure("TRadiobutton", background=BG_COLOR, foreground=TEXT_COLOR)

    style.configure("TSuccess.TButton", foreground='white', background=SUCCESS_COLOR,
                    font=("Segoe UI", 11, "bold"), padding=(10, 5))
    style.map("TSuccess.TButton", background=[('active', '#27AE60')])

    style.configure("TSecondary.TButton", foreground='white', background=SECONDARY_COLOR,
                    font=("Segoe UI", 10), padding=(10, 5))
    style.map("TSecondary.TButton", background=[('active', '#7F8C8D')])


def init_ui():
    """Initializes the main window."""
    global root, content_frame
    root.title("Visitor Management System")
    root.geometry("1000x650")
    root.configure(bg=BG_COLOR)

    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)

    tk.Label(root, text="Visitor Management System", font=("Segoe UI", 20, "bold"),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="ew", pady=(10, 5))

    nav = setup_navbar()
    nav.grid(row=1, column=0, sticky="ew")

    content_frame = tk.Frame(root, bg=BG_COLOR)
    content_frame.grid(row=2, column=0, sticky="nsew")

    tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.",
             font=("Segoe UI", 9), bg=BG_COLOR, fg="#7F8C8D").grid(row=3, column=0, pady=5)

    show_home()


if __name__ == "__main__":
    root = tk.Tk()
    setup_styles(ttk.Style(root))
    init_ui()
    root.mainloop()
