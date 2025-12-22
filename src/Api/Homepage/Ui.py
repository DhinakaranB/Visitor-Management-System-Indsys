import tkinter as tk
from tkinter import ttk, messagebox
import os, sys  
import common_header    

# --- DEBUG: Start ---
print("--- Ui.py: Starting initialization ---")

# -----------------------------------------
# SAFE IMPORT HANDLING
# -----------------------------------------
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
    from src.Api.Homepage import common_header
    from src.Api.visitor_screen import VisitorRegisterDetails as visitorRegisterDetails
    from src.Api.visitor_screen import VisitorQRconfig as visitorQRconfig


    # Import the FILE (module), not something inside it
    from src.Api.person_screen import person_form
    from src.Api.person_screen import person_list  
except Exception as e:
    print("Import Error:", e)

    # --- NEW MODULES ---
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

def show_add_person():
    print("Opening Add Person Screen...")   
    # Pass 'show_person_list' so after saving, it goes to the list automatically
    person_form.show_create_form(content_frame, on_success_callback=show_person_list)

def show_person_list():
    print("Opening Person List Screen...")
    person_list.show_list(content_frame)

# -----------------------------------------
# GLOBALS & COLORS
# -----------------------------------------
BG_COLOR = "#D6EAF8"
NAVBAR_BLUE = "#0A74FF"
WHITE = "#FFFFFF"

root = None
content_frame = None  # This will hold the changing screens
nav = None

# -----------------------------------------
# NAVIGATION FUNCTIONS
# -----------------------------------------
def clear_content():
    """Removes all widgets from the content frame"""
    if content_frame:
        for widget in content_frame.winfo_children():
            widget.destroy()

def show_home():
    clear_content()
    # Pass content_frame as the parent for the home screen
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

def open_person_dropdown(widget):
    # 1. Create the popup menu window
    menu = tk.Toplevel(root)
    menu.overrideredirect(True) # Removes window borders
    menu.config(bg="white")
    
    # 2. Calculate position (appears right under the button)
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"200x100+{x}+{y}") # Adjusted size for 2 items

    # 3. Helper to create menu items
    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI", 10), padx=14, pady=7, anchor="w")
        lbl.pack(fill="x")
        # Hover effects (Light Blue)
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        # Click action
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    # 4. Add the Menu Items
    item("Add Person", show_add_person)
    item("Person List (Edit/Delete)", show_person_list)

    # 5. Close menu if user clicks away
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()


def setup_navbar():
    print("--- Ui.py: Setting up Navbar via common_header ---")
    
    common_header.render_global_header(
        root,
        home_fn=show_home,
        visitor_fn=open_visitor_dropdown,
        
        # LINK THE NEW DROPDOWN HERE:
        person_fn=open_person_dropdown,  
        
        vehicle_fn=lambda w: print("Vehicle Clicked"), # We will do Vehicle next
        door_fn=open_door_dropdown,
        access_fn=lambda: messagebox.showinfo("Info", "Access Control Coming Soon")
    )
    
    global nav
    global content_frame
    
    content_frame = tk.Frame(root, bg=BG_COLOR) 
    content_frame.pack(fill="both", expand=True) 

    show_home()


# -----------------------------------------
# MAIN UI INIT
# -----------------------------------------
def init_ui():
    global root

    try:
        print("--- Ui.py: Applying Geometry ---")
        root.title("Visitor Management System")
        root.geometry("1100x750")
        root.configure(bg=BG_COLOR)

        # NOTE: We do NOT use grid_rowconfigure on root anymore 
        # because the Header uses pack(). Mixing them causes the crash.
        
        # 1. Setup Navbar & Content Area
        setup_navbar()

        # 2. Add Footer (Use pack to match the header)
        footer = tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.", font=("Segoe UI",9), bg=BG_COLOR, fg="#777")
        footer.pack(side="bottom", pady=8)

    except Exception as e:
        messagebox.showerror("Critical Error", f"Failed to load UI:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    init_ui()
    root.mainloop()