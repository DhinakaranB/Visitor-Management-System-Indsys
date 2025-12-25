import base64
import tkinter as tk
import os
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry  # Requires: pip install tkcalendar
import Api.Common_signature.common_signature_api as api_handler
import Api.visitor_screen.visitor_appointment as visitor_appointment 
import json

# ==========================================
# 1. CONFIGURATION & STYLES
# ==========================================
BG_COLOR = "#F4F6F7"        
CARD_BG = "#FFFFFF"         
PRIMARY_COLOR = "#3498DB"   
SUCCESS_COLOR = "#27AE60"   
WARNING_COLOR = "#E67E22"   
TEXT_COLOR = "#2C3E50"      
LABEL_COLOR = "#7F8C8D"     
BORDER_COLOR = "#D5DBDB"
ERROR_COLOR = "#E74C3C"     # Red for validation *

# API Endpoints
API_CREATE_PATH = "/artemis/api/visitor/v1/registerment"
API_UPDATE_PATH = "/artemis/api/visitor/v1/registerment/update"

ui_elements = {}
current_visitor_id = None 
is_edit_mode = False      

# ==========================================
# 2. LOGIC HANDLERS
# ==========================================

def handle_submit(root_instance):
    """ Handles Register using the EXACT JSON structure provided """
    global current_visitor_id
    
    # --- 1. GET DATA FROM UI ---
    rec_id = ui_elements["rec_id"].get()
    
    # Date Handling: Get Date Objects + Add Time & Timezone
    date_start = ui_elements["start_date"].get_date()
    date_end = ui_elements["end_date"].get_date()
    
    # Construct ISO 8601 Strings (Hardcoded 09:00 to 18:00 for simplicity, adjust as needed)
    start_time = date_start.strftime("%Y-%m-%dT09:00:00+05:30")
    end_time = date_end.strftime("%Y-%m-%dT18:00:00+05:30")

    # Purpose Mapping
    purpose_str = ui_elements["purpose_cb"].get()
    purpose_map = {"Business": 0, "Training": 1, "Visit": 2, "Meeting": 3, "Others": 4}
    visit_purpose_type = purpose_map.get(purpose_str, 4) # Default to Others

    f_name = ui_elements["fname_entry"].get()
    l_name = ui_elements["lname_entry"].get()
    phone = ui_elements["phone_entry"].get()
    email = ui_elements["email_entry"].get()
    
    # Gender Mapping
    gender_str = ui_elements["gender_cb"].get()
    gender_map = {"Male": 1, "Female": 2, "Unknown": 0}
    gender_val = gender_map.get(gender_str, 1)

    group_name = ui_elements["group_entry"].get()
    company = ui_elements["company_entry"].get()
    plate = ui_elements["plate_entry"].get()
    cert_type = ui_elements["cert_entry"].get()
    remark = ui_elements["remark_entry"].get()

    # --- Validation ---
    if not f_name or not phone:
        messagebox.showwarning("Validation", "First Name and Phone Number are required.")
        return

    # --- 2. PREPARE EXACT PAYLOAD ---
    payload = {
        "receptionistId": rec_id,
        "visitStartTime": start_time,
        "visitEndTime": end_time,
        "visitPurposeType": visit_purpose_type,
        "visitPurpose": purpose_str,
        "visitorInfoList": [
            {
                "VisitorInfo": {
                    "visitorFamilyName": l_name if l_name else "Guest", 
                    "visitorGivenName": f_name,
                    "visitorGroupName": group_name,
                    "gender": gender_val,
                    "email": email,
                    "phoneNo": phone,
                    "plateNo": plate,
                    "companyName": company,
                    "certificateType": int(cert_type) if cert_type.isdigit() else 111,
                    "remark": remark,
                    "accessInfo": {
                        "electrostaticDetectionType": 1,
                        "qrCodeValidNum": 1
                    }
                },
                "cards": [
                    {
                        "cardNo": "123456" 
                    }
                ]
            }
        ]
    }

    # --- 3. DETERMINE API PATH ---
    if is_edit_mode and current_visitor_id:
        api_path = API_UPDATE_PATH
        payload["visitorInfoList"][0]["VisitorInfo"]["visitorId"] = current_visitor_id
        action_name = "Update"
    else:
        api_path = API_CREATE_PATH
        action_name = "Registration"

    # --- 4. CALL API ---
    response = api_handler.call_api(api_path, payload)

    # --- 5. HANDLE RESPONSE ---
    if response and response.get("code") == "0":
        data = response.get("data", {})
        
        new_id = None
        if isinstance(data, dict):
            new_id = data.get("visitorId")
            if not new_id and "list" in data:
                 try: new_id = data["list"][0].get("visitorId")
                 except: pass
        
        if new_id: current_visitor_id = new_id
        
        messagebox.showinfo("Success", f"{action_name} Successful!")
        
        if current_visitor_id:
            ui_elements["btn_appt"].config(state="normal", bg=SUCCESS_COLOR, text="NEXT: BOOK APPOINTMENT ➜")
            ui_elements["status_bar"].config(bg="#D4EFDF", fg=SUCCESS_COLOR, text=f"✅ SAVED ID: {current_visitor_id}")
    else:
        msg = response.get('msg') if response else "Unknown Error"
        messagebox.showerror("Error", f"{action_name} Failed: {msg}")

def open_appointment_screen(root_instance, show_main_menu):
    if not current_visitor_id:
        if not messagebox.askyesno("Confirm", "No Visitor ID detected. Proceed anyway?"):
            return
    visitor_appointment.show_appointment_screen(root_instance, show_main_menu, prefill_visitor_id=current_visitor_id)


def show_qr_success_popup(parent, appoint_id, visitor_id, b64_image_data, name):
    """ Displays a modal with the QR Code and ID, and saves it to disk """
    popup = tk.Toplevel(parent)
    popup.title("Registration Successful")
    popup.geometry("450x550")
    popup.configure(bg="white")
    popup.transient(parent) # Keep on top
    popup.grab_set()        # Modal behavior

    # 1. Clean the Base64 String (Critical for proper rendering)
    # Remove newlines/spaces that might corrupt the image
    b64_image_data = b64_image_data.replace("\n", "").replace("\r", "").strip()

    # Title
    tk.Label(popup, text="✅ Visitor Registered!", font=("Segoe UI", 16, "bold"), bg="white", fg=SUCCESS_COLOR).pack(pady=(20, 5))
    tk.Label(popup, text=f"Welcome, {name}", font=("Segoe UI", 12), bg="white", fg=TEXT_COLOR).pack()

    # QR Code Image
    try:
        # Render Image
        qr_image = tk.PhotoImage(data=b64_image_data)
        
        # Display Image
        img_lbl = tk.Label(popup, image=qr_image, bg="white", bd=1, relief="solid")
        img_lbl.image = qr_image # Keep reference!
        img_lbl.pack(pady=20, padx=20)
        
        # SAVE TO FILE (Debugging)
        # This helps you check if the QR code is valid by opening it manually
        with open("last_visitor_qr.png", "wb") as fh:
            fh.write(base64.b64decode(b64_image_data))
        print("DEBUG: QR Code saved to 'last_visitor_qr.png'")
        
    except Exception as e:
        tk.Label(popup, text=f"(QR Render Error: {e})", bg="white", fg="red").pack(pady=20)
        print(f"QR Error: {e}")

    # Warning Label about Scanning
    warn_text = "Note: If scanning with phone fails, it's because\nthe server is on Localhost (127.0.0.1).\nScan this at the Entry Terminal instead."
    tk.Label(popup, text=warn_text, font=("Segoe UI", 9), bg="#FEF9E7", fg="#D35400", justify="center").pack(pady=(0, 15))

    # IDs
    info_frame = tk.Frame(popup, bg="#F4F6F7", pady=10, padx=10)
    info_frame.pack(fill="x", padx=40, pady=(0, 20))
    
    tk.Label(info_frame, text=f"Visitor ID: {visitor_id}", font=("Segoe UI", 10, "bold"), bg="#F4F6F7", fg=TEXT_COLOR).pack()
    tk.Label(info_frame, text=f"Appoint ID: {appoint_id}", font=("Segoe UI", 9), bg="#F4F6F7", fg=LABEL_COLOR).pack()

    # Close Button
    tk.Button(popup, text="Close", bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=5, bd=0, cursor="hand2", command=popup.destroy).pack(side="bottom", pady=20)

# ==========================================
# 3. PROFESSIONAL COMPACT UI
# ==========================================
def show_register_screen(root_instance, show_main_screen_callback, edit_data=None):
    global ui_elements, current_visitor_id, is_edit_mode
    
    ui_elements = {}
    current_visitor_id = None
    is_edit_mode = False
    
    # Maximize Window
    try:
        root_instance.winfo_toplevel().state('zoomed')
    except:
        pass

    # Check Mode
    if edit_data and ("visitorId" in edit_data or "visitorID" in edit_data):
        is_edit_mode = True
        current_visitor_id = edit_data.get("visitorId") or edit_data.get("visitorID")
        title_text = "Update Visitor"
        btn_text = "SAVE CHANGES"
        btn_bg = WARNING_COLOR 
    else:
        title_text = "New Visitor Registration"
        btn_text = "REGISTER VISITOR"
        btn_bg = PRIMARY_COLOR 

    # --- RESET WINDOW ---
    for widget in root_instance.winfo_children(): widget.destroy()
    root_instance.config(bg=BG_COLOR)

    # --- MAIN CONTAINER ---
    container = tk.Frame(root_instance, bg=BG_COLOR, padx=40, pady=10)
    container.pack(fill="both", expand=True)
    
    # --- HEADER ---
    header_frame = tk.Frame(container, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(0, 5))
    
    tk.Button(header_frame, text="← Back", command=show_main_screen_callback, bg=BG_COLOR, fg=LABEL_COLOR, bd=0, cursor="hand2").pack(side="left")
    tk.Label(header_frame, text=f"  |  {title_text}", font=("Segoe UI", 18, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")

    # --- CARD (WHITE BOX) ---
    card = tk.Frame(container, bg=CARD_BG, padx=30, pady=15)
    card.pack(fill="both", expand=True)
    
    card.columnconfigure(1, weight=1)
    card.columnconfigure(3, weight=1)
    
    style = ttk.Style()
    style.configure("Modern.TEntry", padding=5)

    def add_header(row, text):
        lbl = tk.Label(card, text=text.upper(), font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#95A5A6")
        lbl.grid(row=row, column=0, columnspan=4, sticky="w", pady=(10, 2))
        ttk.Separator(card, orient="horizontal").grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=(0, 5))
        return row + 2

    def add_field_label(row, col, label, required=False):
        # Frame to hold label and star
        lbl_frame = tk.Frame(card, bg=CARD_BG)
        lbl_frame.grid(row=row, column=col, sticky="w", pady=(0,0))
        
        tk.Label(lbl_frame, text=label, bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 9)).pack(side="left")
        if required:
            tk.Label(lbl_frame, text=" *", bg=CARD_BG, fg=ERROR_COLOR, font=("Segoe UI", 10, "bold")).pack(side="left")

    def add_text_field(row, col, label, var_name, value="", width=None, required=False):
        add_field_label(row, col, label, required)
        
        entry = ttk.Entry(card, font=("Segoe UI", 10), style="Modern.TEntry")
        if width: entry.config(width=width)
        entry.grid(row=row+1, column=col, sticky="ew", padx=(0, 20), pady=(0, 8))
        if value: entry.insert(0, str(value))
        ui_elements[var_name] = entry

    def add_dropdown_field(row, col, label, var_name, options, default_val, required=False):
        add_field_label(row, col, label, required)
        
        combo = ttk.Combobox(card, values=options, font=("Segoe UI", 10), state="readonly")
        combo.set(default_val)
        combo.grid(row=row+1, column=col, sticky="ew", padx=(0, 20), pady=(0, 8))
        ui_elements[var_name] = combo

    def add_date_field(row, col, label, var_name, default_date_iso=None, required=False):
        add_field_label(row, col, label, required)
        
        date_picker = DateEntry(card, width=12, background=PRIMARY_COLOR, foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        date_picker.grid(row=row+1, column=col, sticky="ew", padx=(0, 20), pady=(0, 8))
        
        # Pre-select date if updating
        if default_date_iso:
            try:
                # Expecting ISO like 2025-12-24T...
                dt = datetime.strptime(default_date_iso[:10], "%Y-%m-%d")
                date_picker.set_date(dt)
            except:
                pass
        
        ui_elements[var_name] = date_picker

    # Data Extract
    d = edit_data if edit_data else {}

    # === 1. VISIT DETAILS ===
    r = add_header(0, "Visit Details")
    
    # Row 1: ID & Purpose
    add_text_field(r, 0, "Receptionist ID", "rec_id", d.get("receptionistId", "1"))
    
    # Visit Purpose Dropdown (0-4 mapping)
    purposes = ["Business", "Training", "Visit", "Meeting", "Others"]
    default_purpose = d.get("visitPurpose", "Business")
    if default_purpose == "null": default_purpose = "Business"
    add_dropdown_field(r, 2, "Visit Purpose", "purpose_cb", purposes, default_purpose)
    
    r += 2
    # Row 2: Date Pickers
    def_start = d.get("visitStartTime", datetime.now().strftime("%Y-%m-%dT..."))
    def_end = d.get("visitEndTime", datetime.now().strftime("%Y-%m-%dT..."))
    
    add_date_field(r, 0, "Visit Start Date", "start_date", def_start, required=True)
    add_date_field(r, 2, "Visit End Date", "end_date", def_end, required=True)

    # === 2. PERSONAL INFO ===
    r += 2
    r = add_header(r, "Personal Information")
    
    add_text_field(r, 0, "Given Name (First Name)", "fname_entry", d.get("visitorGivenName", ""), required=True)
    add_text_field(r, 2, "Family Name (Last Name)", "lname_entry", d.get("visitorFamilyName", "Guest"))
    
    r += 2
    add_text_field(r, 0, "Phone Number", "phone_entry", d.get("phoneNo", ""), required=True)
    add_text_field(r, 2, "Email Address", "email_entry", d.get("email", ""))
    
    r += 2
    # Gender Dropdown
    gender_map_rev = {"1": "Male", "2": "Female", "0": "Unknown"}
    raw_gen = str(d.get("gender", "1"))
    def_gen = gender_map_rev.get(raw_gen, "Male")
    add_dropdown_field(r, 0, "Gender", "gender_cb", ["Male", "Female", "Unknown"], def_gen)

    # === 3. COMPANY & OTHER ===
    r += 2
    r = add_header(r, "Company & Additional Info")
    
    add_text_field(r, 0, "Company Name", "company_entry", d.get("companyName", ""))
    add_text_field(r, 2, "Vehicle Plate", "plate_entry", d.get("plateNo", ""))
    
    r += 2
    add_text_field(r, 0, "Group Name", "group_entry", d.get("visitorGroupName", "Visitors"))
    add_text_field(r, 2, "Cert Type (111=ID)", "cert_entry", d.get("certificateType", "111"))
    
    r += 2
    # Remark spans full width
    tk.Label(card, text="Remark", bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 9)).grid(row=r, column=0, sticky="w")
    remark_entry = ttk.Entry(card, font=("Segoe UI", 10), style="Modern.TEntry")
    remark_entry.grid(row=r+1, column=0, columnspan=4, sticky="ew", padx=(0, 20), pady=(0, 8))
    remark_entry.insert(0, str(d.get("remark", "Visitor")))
    ui_elements["remark_entry"] = remark_entry

    # --- FOOTER ---
    footer = tk.Frame(container, bg=BG_COLOR)
    footer.pack(fill="x", pady=10, side="bottom")
    
    # Status bar with Red legend
    status_frame = tk.Frame(footer, bg="#EAEDED")
    status_frame.pack(side="left", fill="x", expand=True)
    tk.Label(status_frame, text="* Required Fields", bg="#EAEDED", fg=ERROR_COLOR, padx=15, pady=8, font=("Segoe UI", 9, "bold")).pack(side="left")
    ui_elements["status_bar"] = tk.Label(status_frame, text="", bg="#EAEDED", fg=LABEL_COLOR, font=("Segoe UI", 9))
    ui_elements["status_bar"].pack(side="left")

    tk.Button(footer, text=btn_text, bg=btn_bg, fg="white", font=("Segoe UI", 10, "bold"), padx=25, pady=8, borderwidth=0, cursor="hand2",
              command=lambda: handle_submit(root_instance)).pack(side="left", padx=15)
    
    state = "normal" if is_edit_mode else "disabled"
    bg_next = SUCCESS_COLOR if is_edit_mode else "#BDC3C7"
    
    ui_elements["btn_appt"] = tk.Button(footer, text="NEXT STEP ➜", bg=bg_next, fg="white", font=("Segoe UI", 10, "bold"), 
                                        padx=25, pady=8, state=state, borderwidth=0, cursor="hand2",
                                        command=lambda: open_appointment_screen(root_instance, show_main_screen_callback))
    ui_elements["btn_appt"].pack(side="left")