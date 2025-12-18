import tkinter as tk
from tkinter import ttk, messagebox
import os, sys
from PIL import Image, ImageTk

# --- DEBUG: Start ---
print("--- Ui.py: Starting initialization ---")

# -----------------------------------------
# SAFE IMPORT HANDLING
# -----------------------------------------
# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

try:
    print("--- Ui.py: Attempting imports ---")
    from src.Api.visitor_screen import visitor_registerment as visitor_form
    from src.Api.visitor_screen import visitor_list_Info as visitor_list
    from src.Api.Common_signature import common_signature_api
    from src.Api.Door_screen import door_list_Info as door_list
    from src.Api.Door_screen import linked_door_info as linked_doors
    from src.Api.Homepage.home_screen import load_home_screen
    from src.Api.visitor_screen.visitor_edit import show_visitor_edit
    from src.Api.visitor_screen.visitor_delete import show_visitor_delete
    print("--- Ui.py: Imports successful ---")

except Exception as e:
    print(f"--- Ui.py: IMPORT ERROR: {e} ---")
    print("--- Ui.py: Loading MOCK API fallback ---")

    class MockAPI:
        def show_create_form(*a): print("Mock: show_create_form")
        def show_single_visitor_list(*a): print("Mock: show_single_visitor_list")
        def show_door_list(*a): print("Mock: show_door_list")
        def show_linked_doors(*a): print("Mock: show_linked_doors")

    visitor_form = MockAPI()
    visitor_list = MockAPI()
    door_list = MockAPI()
    linked_doors = MockAPI()

    def load_home_screen(*args, **kwargs):
        print("Mock: load_home_screen (Home screen import failed!)")


# -----------------------------------------
# COLORS
# -----------------------------------------
BG_COLOR = "#D6EAF8"
NAVBAR_BLUE = "#0A74FF"
WHITE = "#FFFFFF"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#2C3EFA"

root = None
content_frame = None
nav = None

# -----------------------------------------
# NAVIGATION FUNCTIONS
# -----------------------------------------
def show_home():
    print("--- Ui.py: Loading Home Screen ---")
    load_home_screen(content_frame)    

def show_add_visitor():
    # Pass 'show_home' as the callback so the form knows how to return
    visitor_form.show_create_form(content_frame, show_home, close_application)

def show_single_visitor_list_external():
    visitor_list.show_single_visitor_list(content_frame)

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

def open_visitor_dropdown(widget):
    menu = tk.Toplevel(root)
    menu.overrideredirect(True)
    menu.config(bg="white")
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"200x200+{x}+{y}")

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI", 10), padx=14, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("Add Visitor", show_add_visitor)
    item("Visitor List", show_single_visitor_list_external)
    item("Edit Visitor", lambda: show_visitor_edit(content_frame))
    separator = tk.Frame(menu, bg="#E5E7EB", height=1)
    separator.pack(fill="x", pady=4, padx=8)
    item("Create Appointment", lambda: messagebox.showinfo("Info", "Coming soon"))
    
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

# -----------------------------------------
# NAVBAR
# -----------------------------------------
def setup_navbar():
    global nav
    print("--- Ui.py: Setting up Navbar ---")
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

        # 1. Setup and Show Navbar
        nav = setup_navbar()
        nav.grid(row=0, column=0, sticky="ew")

        # 2. Setup Content Frame
        print("--- Ui.py: Creating Content Frame ---")
        content_frame = tk.Frame(root, bg=BG_COLOR)
        content_frame.grid(row=1, column=0, sticky="nsew")

        # 3. Footer
        footer = tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.", font=("Segoe UI",9), bg=BG_COLOR, fg="#777")
        footer.grid(row=2, column=0, pady=8)

        # 4. Show Home immediately (Login skipped)
        show_home()
        print("--- Ui.py: Initialization Complete ---")

    except Exception as e:
        print(f"!!! CRITICAL ERROR IN INIT_UI: {e} !!!")
        messagebox.showerror("Critical Error", f"Failed to load UI:\n{e}")

# -----------------------------------------
# BOOT
# -----------------------------------------
if __name__ == "__main__":
    print("--- Ui.py: __main__ started ---")
    root = tk.Tk()
    init_ui()
    print("--- Ui.py: Entering Mainloop ---")
    root.mainloop()