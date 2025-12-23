import tkinter as tk
from tkinter import ttk, messagebox
import Api.Common_signature.common_signature_api as api_handler
import json

# ==========================================
# 1. CONFIGURATION & STYLES
# ==========================================
BG_COLOR = "#F4F6F7"        
CARD_BG = "#FFFFFF"         
TEXT_COLOR = "#2C3E50"      
PRIMARY_COLOR = "#3498DB"   
WARNING_COLOR = "#E67E22"   # Orange (Check Out)
SUCCESS_COLOR = "#27AE60"   # Green (Status)
LABEL_COLOR = "#7F8C8D"     

# === API ENDPOINTS ===
# 1. To display the photo & details immediately
API_SINGLE_INFO = "/artemis/api/visitor/v1/visitor/single/visitorinfo"

# 2. To find the 'appointRecordId' needed for checkout
API_LIST_SEARCH = "/artemis/api/visitor/v1/visitor/queryVisitorList"

# 3. The CORRECT Checkout API for your version
# Use '/out' instead of '/checkOut' to fix the "Product version" error
API_CHECKOUT_PATH = "/artemis/api/visitor/v1/visitor/out" 

# Global references
current_visitor_data = {}
ui_elements = {}

# ==========================================
# 2. LOGIC HANDLERS
# ==========================================

def handle_search(search_term, root_instance):
    """ 
    Two-Step Search:
    1. Get Details (Visuals) -> Sync
    2. Get AppointRecordID (Background) -> Sync
    """
    global current_visitor_data
    
    if not search_term:
        messagebox.showwarning("Input Required", "Please enter a Visitor ID.")
        return

    # Clear UI
    current_visitor_data = {} 
    reset_ui_fields()
    ui_elements["status_lbl"].config(text="SEARCHING...", fg=PRIMARY_COLOR)
    
    # Force UI update
    root_instance.update()

    # --- STEP 1: Get Details (Visuals) ---
    search_payload = { "visitorId": search_term }
    
    # Call API
    response = api_handler.call_api(API_SINGLE_INFO, search_payload)

    # Validate Response
    if not response or "data" not in response:
        ui_elements["status_lbl"].config(text="NOT FOUND", fg="red")
        return

    data_block = response.get("data", {})
    if not data_block or "VisitorInfo" not in data_block:
        messagebox.showinfo("Not Found", f"No details found for ID: {search_term}")
        ui_elements["status_lbl"].config(text="NOT FOUND", fg="red")
        return

    # Success! Bind Visuals
    visitor_record = data_block["VisitorInfo"]
    populate_ui_visuals(visitor_record)
    current_visitor_data.update(visitor_record)
    
    # --- STEP 2: Fetch Appointment ID (Crucial for Checkout) ---
    # We use the name to find the 'appointRecordId'
    visitor_name = visitor_record.get("visitorFullName") or visitor_record.get("visitorGivenName")
    
    if visitor_name:
        fetch_appointment_id(visitor_name, search_term)
    else:
        print("Warning: No visitor name found, cannot fetch Appointment ID.")

def fetch_appointment_id(visitor_name, original_visitor_id):
    """ Calls list API to find 'appointRecordId' corresponding to the Visitor ID """
    payload = { "pageNo": 1, "pageSize": 50, "visitorName": visitor_name }
    
    response = api_handler.call_api(API_LIST_SEARCH, payload)
    
    if response and "data" in response and response["data"] and response["data"].get("list"):
        for record in response["data"]["list"]:
            # Match IDs
            if str(record.get("visitorId")) == str(original_visitor_id):
                # Found the record! Get the ID needed for checkout
                appoint_id = record.get("appointRecordId") or record.get("orderId")
                if appoint_id:
                    current_visitor_data["appointRecordId"] = appoint_id
                    print(f"DEBUG: Found Appointment ID: {appoint_id}")
                    enable_checkout_button()
                return
    
    print("DEBUG: Could not resolve Appointment ID from list.")

def populate_ui_visuals(data):
    """ Updates UI Labels """
    name = data.get("visitorFullName") or data.get("visitorGivenName") or "--"
    company = data.get("companyName", "--")
    phone = data.get("phoneNo", "--")
    plate = data.get("plateNo", "--")
    
    gender_map = {1: "Male", 2: "Female", 0: "Unknown"}
    gender = gender_map.get(data.get("gender", 0), "Unknown")
    
    ui_elements["name_lbl"].config(text=name)
    ui_elements["comp_lbl"].config(text=company)
    ui_elements["phone_lbl"].config(text=phone)
    ui_elements["plate_lbl"].config(text=plate)
    ui_elements["purpose_lbl"].config(text=gender)

    ui_elements["status_lbl"].config(text="VISITOR FOUND", fg=PRIMARY_COLOR)

def enable_checkout_button():
    ui_elements["status_lbl"].config(text="READY TO CHECK OUT", fg=SUCCESS_COLOR)
    ui_elements["btn_out"].config(state="normal", bg=WARNING_COLOR, text="CONFIRM CHECK OUT ➜")

def perform_checkout():
    """ Execute Checkout using appointRecordId """
    # 1. Get the ID we found in Step 2
    record_id = current_visitor_data.get("appointRecordId")
    
    if not record_id:
        messagebox.showerror("Error", "Could not find 'appointRecordId'.\nCheckout cannot proceed without it.")
        return

    # 2. Prepare Payload
    payload = { "appointRecordId": record_id }

    # 3. Call API
    response = api_handler.call_api(API_CHECKOUT_PATH, payload)

    if response and response.get("code") == "0":
        messagebox.showinfo("Success", "Visitor Checked Out Successfully!")
        ui_elements["status_lbl"].config(text="CHECKED OUT", fg="red")
        ui_elements["btn_out"].config(state="disabled", bg="#bdc3c7", text="CHECKED OUT")
    else:
        msg = response.get('msg') if response else "Unknown Error"
        messagebox.showerror("Checkout Failed", f"Error: {msg}")

def reset_ui_fields():
    for key in ["name_lbl", "comp_lbl", "phone_lbl", "plate_lbl", "purpose_lbl"]:
        if key in ui_elements:
            ui_elements[key].config(text="--")
    ui_elements["btn_out"].config(state="disabled", bg="#bdc3c7", text="CHECK OUT ➜")

# ==========================================
# 3. UI LAYOUT
# ==========================================
def show_checkin_screen(root_instance, show_main_screen_callback):
    global ui_elements
    
    try:
        root_instance.winfo_toplevel().state("zoomed")
    except:
        pass

    root_instance.config(bg=BG_COLOR)
    for widget in root_instance.winfo_children():
        widget.destroy()

    root_instance.grid_columnconfigure(0, weight=1)
    root_instance.grid_columnconfigure(1, weight=0)
    root_instance.grid_columnconfigure(2, weight=1)
    root_instance.grid_rowconfigure(0, weight=1)

    main_container = tk.Frame(root_instance, bg=BG_COLOR)
    main_container.grid(row=0, column=1, sticky="n", pady=30)

    # Header
    header_frame = tk.Frame(main_container, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(0, 20))

    btn_back = tk.Button(
        header_frame, text="← Back to Main Menu", command=show_main_screen_callback,
        bg=BG_COLOR, fg=LABEL_COLOR, bd=0, font=("Segoe UI", 9), cursor="hand2"
    )
    btn_back.pack(side="top", anchor="w")

    tk.Label(
        header_frame, text="Visitor Check-Out", font=("Segoe UI", 24, "bold"), 
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(side="left", pady=(5,0))

    # Search Card
    search_card = tk.Frame(main_container, bg=CARD_BG, padx=30, pady=20)
    search_card.pack(fill="x", pady=(0, 20))

    tk.Label(search_card, text="ENTER VISITOR ID", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=LABEL_COLOR).pack(anchor="w")
    
    search_row = tk.Frame(search_card, bg=CARD_BG)
    search_row.pack(fill="x", pady=(5, 0))

    search_entry = ttk.Entry(search_row, font=("Segoe UI", 12))
    search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
    search_entry.focus()
    search_entry.bind('<Return>', lambda event: handle_search(search_entry.get(), root_instance))

    btn_search = tk.Button(
        search_row, text="Find Visitor", bg=PRIMARY_COLOR, fg="white", 
        font=("Segoe UI", 10, "bold"), bd=0, padx=25, pady=6, cursor="hand2",
        command=lambda: handle_search(search_entry.get(), root_instance)
    )
    btn_search.pack(side="right")

    # Details Card
    details_card = tk.Frame(main_container, bg=CARD_BG, padx=40, pady=40)
    details_card.pack(fill="both", expand=True)

    status_frame = tk.Frame(details_card, bg=CARD_BG)
    status_frame.pack(fill="x", pady=(0, 20))
    tk.Label(status_frame, text="STATUS:", font=("Segoe UI", 10, "bold"), bg=CARD_BG, fg=LABEL_COLOR).pack(side="left")
    ui_elements["status_lbl"] = tk.Label(status_frame, text="WAITING FOR INPUT...", font=("Segoe UI", 12, "bold"), bg=CARD_BG, fg="#95A5A6")
    ui_elements["status_lbl"].pack(side="left", padx=10)

    grid_frame = tk.Frame(details_card, bg=CARD_BG)
    grid_frame.pack(fill="x")
    grid_frame.columnconfigure(1, weight=1)
    grid_frame.columnconfigure(3, weight=1)

    def add_detail_row(row, label1, key1, label2, key2):
        tk.Label(grid_frame, text=label1, font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=LABEL_COLOR).grid(row=row, column=0, sticky="w", pady=10)
        lbl1 = tk.Label(grid_frame, text="--", font=("Segoe UI", 11), bg=CARD_BG, fg=TEXT_COLOR)
        lbl1.grid(row=row, column=1, sticky="w", padx=(0, 20))
        ui_elements[key1] = lbl1
        
        tk.Label(grid_frame, text=label2, font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=LABEL_COLOR).grid(row=row, column=2, sticky="w", pady=10, padx=(20,0))
        lbl2 = tk.Label(grid_frame, text="--", font=("Segoe UI", 11), bg=CARD_BG, fg=TEXT_COLOR)
        lbl2.grid(row=row, column=3, sticky="w")
        ui_elements[key2] = lbl2
        
        ttk.Separator(grid_frame, orient="horizontal").grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=5)

    add_detail_row(0, "VISITOR NAME", "name_lbl", "COMPANY", "comp_lbl")
    add_detail_row(2, "PHONE NO", "phone_lbl", "VEHICLE PLATE", "plate_lbl")
    add_detail_row(4, "GENDER", "purpose_lbl", "", "dummy") 

    # Action Button
    btn_area = tk.Frame(details_card, bg=CARD_BG)
    btn_area.pack(fill="x", pady=(30, 0))

    ui_elements["btn_out"] = tk.Button(
        btn_area, text="CHECK OUT ➜", bg="#bdc3c7", fg="white",
        font=("Segoe UI", 14, "bold"), bd=0, padx=30, pady=12, cursor="hand2", state="disabled",
        command=perform_checkout
    )
    ui_elements["btn_out"].pack(fill="x")