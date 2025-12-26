import base64
import tkinter as tk
import os
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import Api.Common_signature.common_signature_api as api_handler
import Api.visitor_screen.visitor_appointment as visitor_appointment 
import json

# ==========================================
# 1. CONFIGURATION & STYLES
# ==========================================
BG_MAIN = "white"             
BG_SECTION = "#F3F4F6"        
BG_APP = "#F4F6F7"            
TEXT_HEADER = "#333333"       
TEXT_LABEL = "#555555"        
BORDER_COLOR = "#D1D5DB"      

BTN_PRIMARY = "#4F46E5"       
BTN_SUCCESS = "#27AE60"       
BTN_TEXT = "white"

FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 9)
FONT_ENTRY = ("Segoe UI", 10)

API_CREATE_PATH = "/artemis/api/visitor/v1/registerment"
API_UPDATE_PATH = "/artemis/api/visitor/v1/registerment/update"

ui_elements = {}
current_visitor_id = None 
is_edit_mode = False      

# ==========================================
# 2. LOGIC HANDLERS (UNCHANGED)
# ==========================================

def handle_submit(root_instance):
    global current_visitor_id
    rec_id = ui_elements["rec_id"].get()
    
    date_start = ui_elements["start_date"].get_date()
    date_end = ui_elements["end_date"].get_date()
    
    start_time = date_start.strftime("%Y-%m-%dT09:00:00+05:30")
    end_time = date_end.strftime("%Y-%m-%dT18:00:00+05:30")

    purpose_str = ui_elements["purpose_cb"].get()
    purpose_map = {"Business": 0, "Training": 1, "Visit": 2, "Meeting": 3, "Others": 4}
    visit_purpose_type = purpose_map.get(purpose_str, 4) 

    f_name = ui_elements["fname_entry"].get()
    l_name = ui_elements["lname_entry"].get()
    phone = ui_elements["phone_entry"].get()
    email = ui_elements["email_entry"].get()
    
    gender_str = ui_elements["gender_cb"].get()
    gender_map = {"Male": 1, "Female": 2, "Unknown": 0}
    gender_val = gender_map.get(gender_str, 1)

    group_name = ui_elements["group_entry"].get()
    company = ui_elements["company_entry"].get()
    plate = ui_elements["plate_entry"].get()
    remark = ui_elements["remark_entry"].get()

    if not f_name or not phone:
        messagebox.showwarning("Validation", "First Name and Phone Number are required (*).")
        return

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
                    "remark": remark,
                    "accessInfo": {"electrostaticDetectionType": 1, "qrCodeValidNum": 1}
                },
                "cards": [{"cardNo": "123456"}]
            }
        ]
    }

    if is_edit_mode and current_visitor_id:
        api_path = API_UPDATE_PATH
        payload["visitorInfoList"][0]["VisitorInfo"]["visitorId"] = current_visitor_id
        action_name = "Update"
    else:
        api_path = API_CREATE_PATH
        action_name = "Registration"

    response = api_handler.call_api(api_path, payload)

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
            ui_elements["btn_appt"].config(state="normal", bg=BTN_SUCCESS, text="NEXT: BOOK APPOINTMENT ➜")
    else:
        msg = response.get('msg') if response else "Unknown Error"
        messagebox.showerror("Error", f"{action_name} Failed: {msg}")

def open_appointment_screen(root_instance, show_main_menu):
    if not current_visitor_id:
        if not messagebox.askyesno("Confirm", "No Visitor ID detected. Proceed anyway?"):
            return
    visitor_appointment.show_appointment_screen(root_instance, show_main_menu, prefill_visitor_id=current_visitor_id)

# ==========================================
# 3. FULL WIDTH FLUID UI
# ==========================================

def show_register_screen(root_instance, show_main_screen_callback, edit_data=None):
    global ui_elements, current_visitor_id, is_edit_mode
    
    ui_elements = {}
    current_visitor_id = None
    is_edit_mode = False
    
    # --- RESET ---
    for widget in root_instance.winfo_children(): widget.destroy()
    root_instance.config(bg=BG_APP)
    try: root_instance.state('zoomed') 
    except: pass

    if edit_data and ("visitorId" in edit_data or "visitorID" in edit_data):
        is_edit_mode = True
        current_visitor_id = edit_data.get("visitorId") or edit_data.get("visitorID")
        header_text = "Update Visitor Registration"
        btn_text = "Save Changes"
    else:
        header_text = "New Visitor Registration"
        btn_text = "Register Visitor"

    # --- TOP BAR ---
    top_bar = tk.Frame(root_instance, bg="white", pady=10, padx=20)
    top_bar.pack(fill="x")
    tk.Button(top_bar, text="← Back", command=show_main_screen_callback, 
              bg="white", fg="#777", bd=0, font=("Segoe UI", 10), cursor="hand2").pack(side="left")
    tk.Label(top_bar, text=f"  |  {header_text}", font=("Segoe UI", 16, "bold"), bg="white", fg=TEXT_HEADER).pack(side="left")

    # --- SCROLLABLE CANVAS SETUP ---
    container = tk.Frame(root_instance, bg=BG_APP)
    container.pack(fill="both", expand=True, padx=20, pady=20)

    canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    
    scrollable_frame = tk.Frame(canvas, bg=BG_MAIN, padx=40, pady=30)
    
    # ---------------------------------------------------------
    # CRITICAL FIX: Make inner frame fill the canvas width
    # ---------------------------------------------------------
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def configure_frame_width(event):
        # Force the scrollable_frame width to match the canvas width
        canvas.itemconfig(frame_id, width=event.width)

    scrollable_frame.bind("<Configure>", configure_scroll_region)
    canvas.bind("<Configure>", configure_frame_width)
    # ---------------------------------------------------------

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ==========================
    # HELPERS
    # ==========================
    def create_section_header(text):
        f = tk.Frame(scrollable_frame, bg=BG_SECTION, pady=8, padx=15)
        f.pack(fill="x", pady=(25, 15))
        tk.Label(f, text=text, font=FONT_HEADER, bg=BG_SECTION, fg=TEXT_HEADER).pack(anchor="w")

    def create_grid_frame(columns=4):
        f = tk.Frame(scrollable_frame, bg=BG_MAIN)
        f.pack(fill="x")
        # Give every column equal weight so they stretch
        for i in range(columns):
            f.columnconfigure(i, weight=1) 
        return f

    def add_field(parent, label_text, key, row, col, default="", required=False, colspan=1):
        # Frame wrapper to add padding around the field
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew", columnspan=colspan)
        
        lbl_frame = tk.Frame(f, bg=BG_MAIN)
        lbl_frame.pack(anchor="w", pady=(0, 5))
        tk.Label(lbl_frame, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(side="left")
        if required:
            tk.Label(lbl_frame, text=" *", font=FONT_LABEL, bg=BG_MAIN, fg="red").pack(side="left")

        entry = ttk.Entry(f, font=FONT_ENTRY)
        entry.pack(fill="x", ipady=5) # ipady makes it taller
        entry.insert(0, str(default))
        ui_elements[key] = entry

    def add_combo(parent, label_text, key, row, col, values, default_val):
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew")

        tk.Label(f, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(anchor="w", pady=(0, 5))
        
        combo = ttk.Combobox(f, values=values, font=FONT_ENTRY, state="readonly")
        combo.pack(fill="x", ipady=5)
        combo.set(default_val)
        ui_elements[key] = combo

    def add_date(parent, label_text, key, row, col, default_iso=None, required=False):
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew")

        lbl_frame = tk.Frame(f, bg=BG_MAIN)
        lbl_frame.pack(anchor="w", pady=(0, 5))
        tk.Label(lbl_frame, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(side="left")
        if required:
            tk.Label(lbl_frame, text=" *", font=FONT_LABEL, bg=BG_MAIN, fg="red").pack(side="left")

        dt = DateEntry(f, width=12, background='#34495E', foreground='white', borderwidth=2, font=FONT_ENTRY, date_pattern='yyyy-mm-dd')
        dt.pack(fill="x", ipady=5)
        
        if default_iso:
            try: dt.set_date(datetime.strptime(default_iso[:10], "%Y-%m-%d"))
            except: pass
        
        ui_elements[key] = dt

    # --- DATA ---
    d = edit_data if edit_data else {}

    # ==========================
    # FORM CONTENT
    # ==========================

    # --- 1. VISIT DETAILS ---
    create_section_header("Visit Details")
    grid1 = create_grid_frame(columns=4) 
    
    add_field(grid1, "Receptionist ID", "rec_id", 0, 0, d.get("receptionistId", "1"))
    
    def_purpose = d.get("visitPurpose", "Business")
    if def_purpose == "null": def_purpose = "Business"
    add_combo(grid1, "Visit Purpose", "purpose_cb", 0, 1, ["Business", "Training", "Visit", "Meeting", "Others"], def_purpose)
    
    def_start = d.get("visitStartTime", datetime.now().strftime("%Y-%m-%dT..."))
    def_end = d.get("visitEndTime", datetime.now().strftime("%Y-%m-%dT..."))
    
    add_date(grid1, "Visit Start Date", "start_date", 0, 2, def_start, required=True)
    add_date(grid1, "Visit End Date", "end_date", 0, 3, def_end, required=True)

    # --- 2. PERSONAL INFORMATION ---
    create_section_header("Personal Information")
    grid2 = create_grid_frame(columns=4)

    add_field(grid2, "Given Name (First Name)", "fname_entry", 0, 0, d.get("visitorGivenName", ""), required=True)
    add_field(grid2, "Family Name (Last Name)", "lname_entry", 0, 1, d.get("visitorFamilyName", "Guest"))
    add_field(grid2, "Phone Number", "phone_entry", 0, 2, d.get("phoneNo", ""), required=True)
    add_field(grid2, "Email Address", "email_entry", 0, 3, d.get("email", ""))
    
    gender_map_rev = {"1": "Male", "2": "Female", "0": "Unknown"}
    raw_gen = str(d.get("gender", "1"))
    def_gen = gender_map_rev.get(raw_gen, "Male")
    add_combo(grid2, "Gender", "gender_cb", 1, 0, ["Male", "Female", "Unknown"], def_gen)

    # --- 3. COMPANY ---
    create_section_header("Company & Additional Info")
    grid3 = create_grid_frame(columns=4)

    add_field(grid3, "Company Name", "company_entry", 0, 0, d.get("companyName", ""))
    add_field(grid3, "Vehicle Plate", "plate_entry", 0, 1, d.get("plateNo", ""))
    add_field(grid3, "Group Name", "group_entry", 0, 2, d.get("visitorGroupName", "Visitors"))
    add_field(grid3, "Remark", "remark_entry", 0, 3, d.get("remark", "Visitor"))

    # --- FOOTER ---
    btn_frame = tk.Frame(scrollable_frame, bg=BG_MAIN, pady=30)
    btn_frame.pack(fill="x")

    tk.Button(btn_frame, text=btn_text, bg=BTN_PRIMARY, fg=BTN_TEXT, font=("Segoe UI", 10, "bold"),
              padx=25, pady=10, relief="flat", cursor="hand2",
              command=lambda: handle_submit(root_instance)).pack(side="left")

    state = "normal" if is_edit_mode else "disabled"
    bg_next = BTN_SUCCESS if is_edit_mode else "#BDC3C7"

    ui_elements["btn_appt"] = tk.Button(btn_frame, text="NEXT STEP →", bg=bg_next, fg=BTN_TEXT, 
                                        font=("Segoe UI", 10, "bold"), padx=25, pady=10, 
                                        relief="flat", cursor="hand2", state=state,
                                        command=lambda: open_appointment_screen(root_instance, show_main_screen_callback))
    ui_elements["btn_appt"].pack(side="right")
    
    tk.Label(scrollable_frame, text="* Required Fields", fg="red", bg=BG_MAIN, font=("Segoe UI", 8)).pack(anchor="w")