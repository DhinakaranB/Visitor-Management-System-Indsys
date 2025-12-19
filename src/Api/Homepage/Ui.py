import tkinter as tk
from tkinter import ttk, messagebox
import os, sys

# --- DEBUG: Start ---
print("--- Ui.py: Starting initialization ---")

# -----------------------------------------
# SAFE IMPORT HANDLING
# -----------------------------------------
# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

try:
    # --- CORE IMPORTS ---
    from src.Api.visitor_screen import visitor_registerment as visitor_form
    from src.Api.visitor_screen import visitor_list_Info as visitor_list
    from src.Api.Common_signature import common_signature_api
    from src.Api.Door_screen import door_list_Info as door_list
    from src.Api.Door_screen import linked_door_info as linked_doors
    from src.Api.Homepage.home_screen import load_home_screen
    from src.Api.visitor_screen.visitor_group import show_visitor_group_screen 

    # --- NEW MODULES (FIXED LOCATION) ---
    # These files are in 'src/Api/visitor_screen/', NOT 'Homepage'
    from src.Api.visitor_screen import VisitorRegisterDetails as visitorRegisterDetails
    from src.Api.visitor_screen import VisitorQRconfig as visitorQRconfig
    
    print("✅ Successfully imported VisitorRegisterDetails & VisitorQRconfig")

except Exception as e:
    print("IMPORT ERROR:", e)
    # Mock classes to prevent crash
    class MockAPI:
        def show_create_form(*a): print("Mock: show_create_form")
        def show_single_visitor_list(*a): print("Mock: show_single_visitor_list")
        def show_door_list(*a): print("Mock: show_door_list")
        def show_linked_doors(*a): print("Mock: show_linked_doors")

    visitor_form = MockAPI()
    visitor_list = MockAPI()
    door_list = MockAPI()
    linked_doors = MockAPI()
    
    # Fallback for new modules
    class FakeModule:
        @staticmethod
        def render_register_details(parent):
            tk.Label(parent, text=f"⚠️ Import Error:\n{e}", fg="red").pack(pady=20)
        @staticmethod
        def render_qr_config(parent):
            tk.Label(parent, text=f"⚠️ Import Error:\n{e}", fg="red").pack(pady=20)
            
    visitorRegisterDetails = FakeModule()
    visitorQRconfig = FakeModule()

    def load_home_screen(*args, **kwargs): print("Mock: load_home_screen")


# -----------------------------------------
# COLORS
# -----------------------------------------
BG_COLOR = "#D6EAF8"
NAVBAR_BLUE = "#0A74FF"
WHITE = "#FFFFFF"

root = None
content_frame = None
nav = None

# -----------------------------------------
# NAVIGATION FUNCTIONS
# -----------------------------------------
def clear_content():
    """Removes all widgets from the content frame"""
    for widget in content_frame.winfo_children():
        widget.destroy()

def show_home():
    clear_content()
    load_home_screen(content_frame)     

def show_add_visitor():
    visitor_form.show_create_form(content_frame, show_home, close_application)

def show_single_visitor_list_external():
    visitor_list.show_single_visitor_list(content_frame)

def show_visitor_groups():
    show_visitor_group_screen(content_frame)

def show_visitor_register():
    clear_content()
    visitorRegisterDetails.render_register_details(content_frame)

def show_visitor_QR():
    clear_content()
    visitorQRconfig.render_qr_config(content_frame)

def show_door_list():
    door_list.show_door_list(content_frame)

def show_linked_doors():
    linked_doors.show_linked_doors(content_frame)

def close_application():
    root.destroy()

# -----------------------------------------
# DROPDOWNS
# -----------------------------------------
def open_door_dropdown(widget):
    menu = tk.Toplevel(root)
    menu.overrideredirect(True)
    menu.config(bg="white")
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"180x120+{x}+{y}")

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI",10), padx=10, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("🚪 Door List", show_door_list)
    item("🔗 Linked Doors", show_linked_doors)
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

def open_visitor_dropdown(widget):
    menu = tk.Toplevel(root)
    menu.overrideredirect(True)
    menu.config(bg="white")
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"240x240+{x}+{y}") 

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI", 10), padx=14, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("Visitor Registration", show_add_visitor)
    item("Visitor List || Edit | Delete", show_single_visitor_list_external)
    item("Visitor Groups", show_visitor_groups)
    item("Visitor Register Details", show_visitor_register)
    item("Visitor QR Config", show_visitor_QR)

    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

# -----------------------------------------
# NAVBAR
# -----------------------------------------
def setup_navbar():
    global nav
    nav = tk.Frame(root, bg=NAVBAR_BLUE, height=55)
    nav.grid_propagate(False)

    left = tk.Frame(nav, bg=NAVBAR_BLUE)
    left.pack(side="left", fill="y")

    tk.Label(left, text="VisitorMS", bg=NAVBAR_BLUE, fg=WHITE, font=("Segoe UI",15,"bold"), padx=18).pack(side="left")

    def menu(text, cmd=None):
        lbl = tk.Label(left, text=text, bg=NAVBAR_BLUE, fg=WHITE, font=("Segoe UI",11), padx=15, cursor="hand2")
        lbl.pack(side="left")
        lbl.bind("<Enter>", lambda e: lbl.config(fg="#DCE6FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(fg=WHITE))
        if cmd: lbl.bind("<Button-1>", lambda e: cmd())
        return lbl

    menu("Home", show_home)
    v = menu("Visitor ▼")
    v.bind("<Button-1>", lambda e: open_visitor_dropdown(v))
    d = menu("Door ▼")
    d.bind("<Button-1>", lambda e: open_door_dropdown(d))
    menu("Access Control", lambda: None)

    return nav

# -----------------------------------------
# MAIN UI INIT
# -----------------------------------------
def init_ui():
    global root, content_frame, nav

    try:
        print("--- Ui.py: Applying Geometry ---")
        root.title("Visitor Management System")
        root.geometry("1100x750")
        root.configure(bg=BG_COLOR)

        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=1)
        root.grid_rowconfigure(2, weight=0)
        root.grid_columnconfigure(0, weight=1)

        nav = setup_navbar()
        nav.grid(row=0, column=0, sticky="ew")

        content_frame = tk.Frame(root, bg=BG_COLOR)
        content_frame.grid(row=1, column=0, sticky="nsew")

        tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.", font=("Segoe UI",9), bg=BG_COLOR, fg="#777").grid(row=2, column=0, pady=8)

        show_home()

    except Exception as e:
        messagebox.showerror("Critical Error", f"Failed to load UI:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    init_ui()
    root.mainloop()