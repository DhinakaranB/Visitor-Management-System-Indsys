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
WARNING_COLOR = "#E67E22"   # Orange (Check Out Button)
SUCCESS_COLOR = "#27AE60"   # Green (Status Text) <--- ADDED BACK
LABEL_COLOR = "#7F8C8D"     

# === API ENDPOINTS ===
API_SEARCH_PATH = "/artemis/api/visitor/v1/visitor/queryVisitorList"
API_CHECKOUT_PATH = "/artemis/api/visitor/v1/visitor/checkOut" 
# Fallback if needed: "/artemis/api/visitor/v1/visitor/out"

# Global references
current_visitor_data = None
ui_elements = {}

# ==========================================
# 2. LOGIC HANDLERS
# ==========================================

def handle_search(search_term, root_instance):
    """ Searches for the visitor to get their record ID """
    global current_visitor_data
    
    if not search_term:
        messagebox.showwarning("Input Required", "Please enter a Visitor ID.")
        return

    # Clear UI
    current_visitor_data = None
    reset_ui_fields()
    ui_elements["status_lbl"].config(text="SEARCHING...", fg=PRIMARY_COLOR)

    # Payload: Map input to 'visitorName' (standard Artemis search)
    search_payload = {
        "pageNo": 1,
        "pageSize": 10,
        "visitorName": search_term 
    }

    def on_search_success(response):
        if not response or "data" not in response:
            ui_elements["status_lbl"].config(text="API ERROR", fg="red")
            return
            
        if not response["data"] or not response["data"].get("list"):
            # Optional: Add logic here to search by 'certNo' if name fails
            messagebox.showinfo("Not Found", f"No visitor found with ID/Name: {search_term}")
            ui_elements["status_lbl"].config(text="NOT FOUND", fg="red")
            return

        # Bind the first result
        visitor_record = response["data"]["list"][0]
        populate_ui(visitor_record)

    api_handler.send_to_api(search_payload, API_SEARCH_PATH, on_search_success)


def populate_ui(data):
    """ Binds data to UI and enables Checkout """
    global current_visitor_data
    current_visitor_data = data
    
    # 1. Bind Texts
    ui_elements["name_lbl"].config(text=data.get("visitorName", "--"))
    ui_elements["comp_lbl"].config(text=data.get("companyName", "--"))
    ui_elements["phone_lbl"].config(text=data.get("phoneNo", "--"))
    ui_elements["plate_lbl"].config(text=data.get("plateNo", "--"))
    
    gender_map = {1: "Male", 2: "Female", 0: "Unknown"}
    gender = gender_map.get(data.get("gender", 0), "Unknown")
    ui_elements["purpose_lbl"].config(text=gender)

    # 2. Update Status (Now SUCCESS_COLOR is defined!)
    ui_elements["status_lbl"].config(text="READY TO CHECK OUT", fg=SUCCESS_COLOR)
    
    # 3. Enable Checkout Button
    ui_elements["btn_out"].config(state="normal", bg=WARNING_COLOR, text="CONFIRM CHECK OUT ➜")


def perform_checkout():
    """ Execute Checkout """
    if not current_visitor_data:
        return

    # 1. Get Appointment Record ID
    record_id = current_visitor_data.get("appointRecordId") or current_visitor_data.get("orderId")

    if not record_id:
        messagebox.showerror("Data Error", "Record ID (appointRecordId) missing. Cannot check out.")
        return

    # 2. Payload
    payload = {
        "appointRecordId": record_id
    }

    # 3. API Call
    def on_success(response):
        if response.get("code") == "0":
            messagebox.showinfo("Success", "Visitor Checked Out Successfully!")
            ui_elements["status_lbl"].config(text="CHECKED OUT", fg="red")
            ui_elements["btn_out"].config(state="disabled", bg="#bdc3c7", text="CHECKED OUT")
        else:
            messagebox.showerror("Checkout Failed", f"Error: {response.get('msg')}")

    api_handler.send_to_api(payload, API_CHECKOUT_PATH, on_success)


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

    tk.Label(search_card, text="ENTER VISITOR ID / NAME", font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=LABEL_COLOR).pack(anchor="w")
    
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

    # Action Button (Checkout Only)
    btn_area = tk.Frame(details_card, bg=CARD_BG)
    btn_area.pack(fill="x", pady=(30, 0))

    ui_elements["btn_out"] = tk.Button(
        btn_area, text="CHECK OUT ➜", bg="#bdc3c7", fg="white",
        font=("Segoe UI", 14, "bold"), bd=0, padx=30, pady=12, cursor="hand2", state="disabled",
        command=perform_checkout
    )
    ui_elements["btn_out"].pack(fill="x")