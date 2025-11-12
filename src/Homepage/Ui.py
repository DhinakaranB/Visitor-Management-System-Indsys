import tkinter as tk
from tkinter import ttk, messagebox
import sys, os

# 🧭 Path Setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Api import visitor_registerment as visitor_form
from Api import visitor_list_Info as visitor_list
import Api.common_signature_api

# 🎨 COLORS
BG_COLOR = "#F4F6F7"
NAV_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#3498DB"
TEXT_COLOR = "#2C3E50"
SUCCESS_COLOR = "#2ECC71"
SECONDARY_COLOR = "#95A5A6"

root = None
content_frame = None
nav = None
login_frame = None


# 🔹 Utility Functions
def clear_content():
    """Remove all widgets from content area."""
    if content_frame:
        for widget in content_frame.winfo_children():
            widget.destroy()


def close_application():
    """Exit the app."""
    if root:
        root.quit()
        root.destroy()


# 🏠 Home Screen
def show_home():
    clear_content()
    home_center = tk.Frame(content_frame, bg=BG_COLOR)
    home_center.grid(row=0, column=0, sticky="nsew")

    tk.Label(
        home_center,
        text="Welcome to Visitor Management System 👋",
        font=("Segoe UI", 22, "bold"),
        bg=BG_COLOR,
        fg=PRIMARY_COLOR,
    ).pack(pady=(50, 10))

    tk.Label(
        home_center,
        text="Use the navigation bar above to manage visitor appointments and access control.",
        font=("Segoe UI", 12),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
    ).pack(pady=(0, 20))


def show_add_visitor():
    clear_content()
    visitor_form.show_create_form(content_frame, show_home, close_application)


def show_single_visitor_list_external():
    clear_content()
    visitor_list.show_single_visitor_list(content_frame)


def show_door_list():
    clear_content()
    import Api.door_list_Info as door_list
    door_list.show_door_list(content_frame)


def show_access_control():
    clear_content()
    lbl = tk.Label(
        content_frame,
        text="🛂 Access Control (Coming Soon)",
        font=("Segoe UI", 14),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
    )
    lbl.grid(row=0, column=0, padx=20, pady=40)


# 🔹 Navbar
def setup_navbar():
    global nav
    nav = tk.Frame(root, bg=NAV_COLOR, relief="raised", bd=1)
    nav.grid(row=1, column=0, sticky="ew")

    # --- Visitor Dropdown ---
    visitor_menu = tk.Menu(nav, tearoff=0, bg="white", fg=TEXT_COLOR, font=("Segoe UI", 10))
    visitor_menu.add_command(label="📋 All Visitor List", command=show_single_visitor_list_external)

    def show_visitor_dropdown(event):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        visitor_menu.tk_popup(x, y)

    # --- Door Dropdown ---
    door_menu = tk.Menu(nav, tearoff=0, bg="white", fg=TEXT_COLOR, font=("Segoe UI", 10))

    # Dropdown functions
    def open_door_list():
        show_door_list()

    def open_linked_doors():
        clear_content()
        import Api.linked_door_info as linked_doors  # 🧩 create your LinkedDoors UI here
        linked_doors.show_linked_doors(content_frame)

    def open_door_access():
        clear_content()
        lbl = tk.Label(
            content_frame,
            text="🚪 Door Access (Coming Soon)",
            font=("Segoe UI", 14),
            bg=BG_COLOR,
            fg=TEXT_COLOR,
        )
        lbl.grid(row=0, column=0, padx=20, pady=40)

    # Dropdown options
    door_menu.add_command(label="Door List", command=open_door_list)
    door_menu.add_command(label="Linked Doors", command=open_linked_doors)
    door_menu.add_command(label="Door Access", command=open_door_access)

    def show_door_dropdown(event):
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height()
        door_menu.tk_popup(x, y)

    # --- Navbar Buttons ---
    buttons = [
        ("🏠 Home", show_home),
        ("➕ Add Visitor", show_add_visitor),
        ("👥 Visitor List ▼", show_visitor_dropdown),
        ("🚪 Door ▼", show_door_dropdown),
        ("🛂 Access Control", show_access_control),
        ("❌ Exit", close_application),
    ]

    for text, cmd in buttons:
        btn = ttk.Button(nav, text=text, style="Nav.TButton")
        btn.pack(side="left", padx=10, pady=6)
        if text.endswith("▼"):
            btn.bind("<Button-1>", cmd)
        else:
            btn.config(command=cmd)

    return nav



# 🔹 Styles
def setup_styles(style):
    style.theme_use("clam")

    style.configure(
        "Nav.TButton",
        font=("Segoe UI", 10, "bold"),
        foreground="white",
        background=PRIMARY_COLOR,
        padding=(8, 5),
        relief="flat",
        borderwidth=0,
        focusthickness=3,
        focuscolor="none",
    )
    style.map(
        "Nav.TButton",
        background=[("active", "#2E86C1")],
        relief=[("pressed", "flat")],
    )

    style.configure("TEntry", fieldbackground="white", foreground=TEXT_COLOR)
    style.configure("TRadiobutton", background=BG_COLOR, foreground=TEXT_COLOR)
    style.configure(
        "TSuccess.TButton",
        foreground="white",
        background=SUCCESS_COLOR,
        font=("Segoe UI", 11, "bold"),
        padding=(10, 5),
    )
    style.map("TSuccess.TButton", background=[("active", "#27AE60")])
    style.configure(
        "TSecondary.TButton",
        foreground="white",
        background=SECONDARY_COLOR,
        font=("Segoe UI", 10),
        padding=(10, 5),
    )
    style.map("TSecondary.TButton", background=[("active", "#7F8C8D")])


# 🔐 LOGIN SCREEN
def show_login_screen():
    """Displays login form before showing main UI."""
    global login_frame
    login_frame = tk.Frame(root, bg="white", width=400, height=320)
    login_frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        login_frame,
        text="Welcome Back 👋",
        font=("Segoe UI", 18, "bold"),
        bg="white",
        fg="#222",
    ).pack(pady=(20, 5))
    tk.Label(
        login_frame,
        text="Sign in to continue",
        font=("Segoe UI", 10),
        bg="white",
        fg="#777",
    ).pack(pady=(0, 20))

    tk.Label(login_frame, text="Username", font=("Segoe UI", 10), bg="white").pack(
        anchor="w", padx=40
    )
    username_entry = tk.Entry(login_frame, width=28, font=("Segoe UI", 11))
    username_entry.pack(pady=(3, 10))

    tk.Label(login_frame, text="Password", font=("Segoe UI", 10), bg="white").pack(
        anchor="w", padx=40
    )
    password_entry = tk.Entry(login_frame, show="*", width=28, font=("Segoe UI", 11))
    password_entry.pack(pady=(3, 15))

    def validate_login():
        user = username_entry.get().strip()
        pwd = password_entry.get().strip()

        if user == "admin" and pwd == "1234":
            # messagebox.showinfo("Login Success", f"Welcome {user} 😎")
            login_frame.destroy()  # hide login
            setup_navbar()  # show navbar
            content_frame.grid(row=2, column=0, sticky="nsew")
            show_home()
        else:
            messagebox.showerror("Error", "Invalid login credentials!")

    tk.Button(
        login_frame,
        text="🔓 Secure Sign In",
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        width=20,
        command=validate_login,
    ).pack(pady=10)

    password_entry.bind("<Return>", lambda e: validate_login())


# 🔹 Initialize Full UI
def init_ui():
    global root, content_frame, nav
    root.title("Visitor Management System")
    root.geometry("1000x650")
    root.configure(bg=BG_COLOR)

    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Title
    tk.Label(
        root,
        text="Visitor Management System",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
    ).grid(row=0, column=0, sticky="ew", pady=(10, 5))

    # Prepare navbar but hide until login
    nav = setup_navbar()
    nav.grid_remove()

    # Prepare main content frame (hidden initially)
    content_frame = tk.Frame(root, bg=BG_COLOR)

    # Footer
    tk.Label(
        root,
        text="© 2025 Indsys Holdings - All rights reserved.",
        font=("Segoe UI", 9),
        bg=BG_COLOR,
        fg="#7F8C8D",
    ).grid(row=3, column=0, pady=5)

    # Start with login screen
    show_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    setup_styles(ttk.Style(root))
    init_ui()
    root.mainloop()
