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

# 1. CORE IMPORTS (Visitor, Door, Person, Vehicle)
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

    # Visitor Extras
    from src.Api.visitor_screen import VisitorRegisterDetails as visitorRegisterDetails
    from src.Api.visitor_screen import VisitorQRconfig as visitorQRconfig

    import src.Api.visitor_screen.visitor_appointment as visitor_appointment
    
    print("✅ Core modules imported successfully")

except Exception as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    # Define mocks so the app doesn't crash completely
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


# 2. NEW DOOR IMPORTS (Isolated - won't crash the app if missing)
region_list = None
org_creation = None
area_creation = None

try:
    from src.Api.Door_screen import region_list
except ImportError:
    print("⚠️ region_list.py not found in Door_screen")

try:
    from src.Api.Door_screen import org_creation
except ImportError:
    print("⚠️ org_creation.py not found in Door_screen")

try:
    # Keep support for your old file if it exists
    from src.Api.Door_screen import area_creation
except ImportError:
    pass

# -----------------------------------------
# WRAPPER FUNCTIONS
# -----------------------------------------
def show_add_person():
    person_form.show_create_form(content_frame, on_success_callback=show_person_list)

def show_person_list():
    person_list.show_list(content_frame)

# -----------------------------------------
# GLOBALS & COLORS
# -----------------------------------------
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
    # Pass the show_home callback correctly
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
    visitorQRconfig.render_qr_config(content_frame)

def show_visitor_checkstatus():
    clear_content()
    # ✅ FIX: Passing content_frame instead of root
    visitor_checkin.show_checkin_screen(content_frame, show_home)

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
    
    # Dynamic height calculation
    menu_height = 80
    if region_list: menu_height += 35
    if org_creation: menu_height += 35
    elif area_creation: menu_height += 35
    
    menu.geometry(f"220x{menu_height}+{x}+{y}")

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI",10), padx=10, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("🚪 Door List", show_door_list)
    item("🔗 Linked Doors", show_linked_doors)
    
    if region_list:
        item("📋 Region/Area List", lambda: region_list.show_region_list(content_frame))
    
    if org_creation:
        item("➕ Create Org (Logical)", lambda: org_creation.show_org_creation(content_frame))
    elif area_creation:
        item("➕ Create Area", lambda: area_creation.show_area_creation(content_frame))

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
    item("Visitor Check-In / Check-Out", show_visitor_checkstatus)

    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

def open_person_dropdown(widget):
    menu = tk.Toplevel(root)
    menu.overrideredirect(True) 
    menu.config(bg="white")
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"200x100+{x}+{y}") 

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI", 10), padx=14, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("Add Person", show_add_person)
    item("Person List (Edit/Delete)", show_person_list)

    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

def open_vehicle_dropdown(widget):
    menu = tk.Toplevel(root)
    menu.overrideredirect(True) 
    menu.config(bg="white")
    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"250x320+{x}+{y}") 

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D", font=("Segoe UI", 10), padx=14, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("Add Vehicle", lambda: vehicle_form.show_vehicle_form(content_frame, lambda: vehicle_list.show_list(content_frame)))
    item("Vehicle List", lambda: vehicle_list.show_list(content_frame))
    item("Vehicle Parking List", lambda: vehicle_screen.show_parking_list(content_frame))
    item("Floor List", lambda: vehicle_screen.show_floor_list(content_frame))
    item("Floor Overview", lambda: vehicle_screen.show_floor_overview(content_frame))
    item("Parkinglot Passageway Record", lambda: vehicle_screen.show_passageway_record(content_frame))
    item("Parking Fee Calculation", lambda: vehicle_screen.show_fee_calc(content_frame))
    item("Parking Fees Confirm", lambda: vehicle_screen.show_fee_confirm(content_frame))

    menu.bind("<FocusOut>", lambda e: menu.destroy())
    menu.focus_force()

# -----------------------------------------
# SETUP NAVBAR
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

        setup_navbar()

        footer = tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.", font=("Segoe UI",9), bg=BG_COLOR, fg="#777")
        footer.pack(side="bottom", pady=8)

    except Exception as e:
        messagebox.showerror("Critical Error", f"Failed to load UI:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    init_ui()
    root.mainloop()