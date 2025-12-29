import tkinter as tk
from tkinter import ttk, messagebox
import os, sys  
from Api.vehicle_screen import vehicle_group_form, vehicle_group_list
import common_header    

# --- THEME CONFIGURATION (Dark Blue + Gold) ---
MENU_BG_COLOR   = "#164077"  # Deep Dark Blue
MENU_TEXT_COLOR = "#FFFFFF"  # White Text
HOVER_BG_COLOR  = "#0A2A54"  # Slightly Lighter Blue
HOVER_TEXT_COLOR= "#FFD700"  # Bright Gold/Yellow
MENU_FONT       = ("Segoe UI", 11)

# --- DEBUG: Start ---
print("--- Ui.py: Starting initialization ---")

# -----------------------------------------
# SAFE IMPORT HANDLING
# -----------------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

try:
    from src.Api.visitor_screen import visitor_registerment as visitor_form
    from src.Api.visitor_screen import visitor_list_Info as visitor_list
    from src.Api.Common_signature import common_signature_api
    from src.Api.Door_screen import door_list_Info as door_list
    from src.Api.Door_screen import linked_door_info as linked_doors
    from src.Api.Homepage.home_screen import load_home_screen
    from src.Api.visitor_screen.visitor_group import show_visitor_group_screen 
    from src.Api.Homepage import common_header
    import src.Api.visitor_screen.visitor_checkin as visitor_checkin  
    
    # Vehicle
    from src.Api.vehicle_screen import vehicle_form
    from src.Api.vehicle_screen import vehicle_list
    from src.Api.vehicle_screen import vehicle_screen

    # Person
    from src.Api.person_screen import person_form
    from src.Api.person_screen import person_list  

    from src.Api.vehicle_screen import vehicle_group_list
    from src.Api.vehicle_screen import vehicle_group_form

    # Visitor Extras
    from src.Api.visitor_screen import VisitorRegisterDetails as visitorRegisterDetails
    from src.Api.visitor_screen import VisitorQRconfig as visitorQRconfig
    import src.Api.visitor_screen.visitor_appointment as visitor_appointment
    
    print("✅ Core modules imported successfully")

except Exception as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    # Mocks to prevent crash
    class MockAPI:
        def show_create_form(*a): print("Mock: show_create_form")
        def show_single_visitor_list(*a): print("Mock: show_single_visitor_list")
        def show_list(*a): print("Mock: show_list")
        def show_door_list(*a): print("Mock: show_door_list")
        def show_linked_doors(*a): print("Mock: show_linked_doors")

    visitor_form = MockAPI()
    visitor_list = MockAPI()
    door_list = MockAPI()
    linked_doors = MockAPI()
    vehicle_form = MockAPI()
    vehicle_list = MockAPI()
    vehicle_screen = MockAPI()
    person_form = MockAPI()
    person_list = MockAPI()
    
    class FakeModule:
        @staticmethod
        def render_register_details(parent): pass
        @staticmethod
        def render_qr_config(parent): pass
            
    visitorRegisterDetails = FakeModule()
    visitorQRconfig = FakeModule()
    def load_home_screen(*args, **kwargs): print("Mock: load_home_screen")


# DOOR IMPORTS
region_list = None
org_creation = None
area_creation = None
try: from src.Api.Door_screen import region_list
except ImportError: pass
try: from src.Api.Door_screen import org_creation
except ImportError: pass
try: from src.Api.Door_screen import area_creation
except ImportError: pass


# -----------------------------------------
# WRAPPER FUNCTIONS
# -----------------------------------------
def show_add_person():
    person_form.show_create_form(content_frame, on_success_callback=show_person_list)

def show_person_list():
    person_list.show_list(content_frame)

BG_COLOR = "#D6EAF8"
root = None
content_frame = None  
nav = None

# -----------------------------------------
# NAVIGATION FUNCTIONS
# -----------------------------------------
def clear_content():
    if content_frame:
        for widget in content_frame.winfo_children():
            widget.destroy()

def show_home():
    clear_content()
    load_home_screen(content_frame)     

def show_add_visitor():
    visitor_form.show_register_screen(content_frame, show_home)

def show_single_visitor_list_external():
    visitor_list.show_single_visitor_list(content_frame)

def show_visitor_groups():
    show_visitor_group_screen(content_frame)

def show_visitor_register():
    clear_content()
    visitorRegisterDetails.render_register_details(content_frame)

def show_visitor_QR():
    clear_content()
    visitorQRconfig.render_qr_config(content_frame, back_callback=content_frame)

def show_visitor_checkstatus():
    clear_content()
    visitor_checkin.show_checkin_screen(content_frame, show_home)

def show_door_list():
    door_list.show_door_list(content_frame)

def show_linked_doors():
    linked_doors.show_linked_doors(content_frame)

def close_application():
    root.destroy()

# ==========================================================
# STYLED DROPDOWN HELPERS (Dark Blue Design)
# ==========================================================

def create_styled_menu(widget, width, height_factor=1):
    """ Helper to create the themed dropdown window """
    menu = tk.Toplevel(root)
    menu.overrideredirect(True)
    menu.config(bg=MENU_BG_COLOR, highlightbackground=HOVER_TEXT_COLOR, highlightthickness=1)
    
    # Position: Under Mouse pointer
    x = root.winfo_pointerx() - 20
    # Fallback Y calculation
    y = widget.winfo_rooty() + widget.winfo_height()
    
    # Approx height calculation (45px per item)
    h = 45 * height_factor 
    menu.geometry(f"{width}x{h}+{x}+{y}")
    return menu

def add_menu_item(menu, text, command):
    """ Helper to add a clean text row to the menu (No Emoji) """
    item_frame = tk.Frame(menu, bg=MENU_BG_COLOR)
    item_frame.pack(fill="x", pady=1)

    lbl = tk.Label(item_frame, text=text, 
                   bg=MENU_BG_COLOR, fg=MENU_TEXT_COLOR, 
                   font=MENU_FONT, anchor="w", padx=20, pady=10)
    lbl.pack(fill="both", expand=True)

    # Hover Effects
    def on_enter(e):
        item_frame.config(bg=HOVER_BG_COLOR)
        lbl.config(bg=HOVER_BG_COLOR, fg=HOVER_TEXT_COLOR, cursor="hand2")

    def on_leave(e):
        item_frame.config(bg=MENU_BG_COLOR)
        lbl.config(bg=MENU_BG_COLOR, fg=MENU_TEXT_COLOR)

    def on_click(e):
        menu.destroy()
        command()

    for w in (item_frame, lbl):
        w.bind("<Enter>", on_enter)
        w.bind("<Leave>", on_leave)
        w.bind("<Button-1>", on_click)

# ==========================================================
# DROPDOWN MENUS
# ==========================================================

def open_visitor_dropdown(widget):
    menu = create_styled_menu(widget, width=260, height_factor=5)
    add_menu_item(menu, "New Registration", show_add_visitor)
    add_menu_item(menu, "Visitor List / Edit", show_single_visitor_list_external)
    add_menu_item(menu, "Visitor Groups", show_visitor_groups)
    add_menu_item(menu, "Register Details", show_visitor_register)
    add_menu_item(menu, "QR Configuration", show_visitor_QR)
    # add_menu_item(menu, "Check-In / Out", show_visitor_checkstatus)
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

def open_person_dropdown(widget):
    menu = create_styled_menu(widget, width=220, height_factor=2)
    add_menu_item(menu, "Add Person", show_add_person)
    add_menu_item(menu, "Person List", show_person_list)
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

def open_vehicle_dropdown(widget):
    menu = create_styled_menu(widget, width=280, height_factor=6)
    add_menu_item(menu, "Add Vehicle Group", lambda: vehicle_group_form.show_group_form(content_frame, lambda: vehicle_group_list.show_group_list(content_frame)))
    add_menu_item(menu, "Vehicle Group List", lambda: vehicle_group_list.show_group_list(content_frame))
    add_menu_item(menu, "Add Vehicle", lambda: vehicle_form.show_vehicle_form(content_frame, lambda: vehicle_list.show_list(content_frame)))
    # add_menu_item(menu, "Vehicle List", lambda: vehicle_list.show_list(content_frame))
    # Match the function name defined in vehicle_list.py
    # add_menu_item(menu, "Vehicle List", lambda: vehicle_list.show_vehicle_list(content_frame))
    # Use .show_list()
    add_menu_item(menu, "Vehicle List", lambda: vehicle_list.show_list(content_frame))
    add_menu_item(menu, "Parking List", lambda: vehicle_screen.show_parking_list(content_frame))
    add_menu_item(menu, "Floor List", lambda: vehicle_screen.show_floor_list(content_frame))
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

def open_door_dropdown(widget):
    count = 2
    if region_list: count += 1
    if org_creation or area_creation: count += 1
    
    menu = create_styled_menu(widget, width=240, height_factor=count)
    add_menu_item(menu, "Door List", show_door_list)
    add_menu_item(menu, "Linked Doors", show_linked_doors)
    if region_list:
        add_menu_item(menu, "Region/Area List", lambda: region_list.show_region_list(content_frame))
    if org_creation:
        add_menu_item(menu, "Create Org", lambda: org_creation.show_org_creation(content_frame))
    elif area_creation:
        add_menu_item(menu, "Create Area", lambda: area_creation.show_area_creation(content_frame))
    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

# -----------------------------------------
# SETUP NAVBAR & INIT
# -----------------------------------------
def setup_navbar():
    print("--- Ui.py: Setting up Navbar via common_header ---")
    common_header.render_global_header(
        root,
        home_fn=show_home,
        visitor_fn=open_visitor_dropdown,
        person_fn=open_person_dropdown,
        vehicle_fn=open_vehicle_dropdown, 
        door_fn=open_door_dropdown,       
        access_fn=lambda: messagebox.showinfo("Info", "Access Control Coming Soon")
    )
    global content_frame
    content_frame = tk.Frame(root, bg=BG_COLOR) 
    content_frame.pack(fill="both", expand=True) 
    show_home()

def init_ui():
    global root
    try:
        print("--- Ui.py: Applying Geometry ---")
        root.title("Visitor Management System")
        root.geometry("1100x750")
        root.configure(bg=BG_COLOR)
        setup_navbar()
        footer = tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.", font=("Segoe UI",9), bg=BG_COLOR, fg="#777")
        footer.pack(side="bottom", pady=8)
    except Exception as e:
        messagebox.showerror("Critical Error", f"Failed to load UI:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    init_ui()
    root.mainloop()