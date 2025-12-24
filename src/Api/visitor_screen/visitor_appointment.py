import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import Api.Common_signature.common_signature_api as api_handler
import json

# ==========================================
# 1. CONFIGURATION & STYLES
# ==========================================
BG_COLOR = "#F4F6F7"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#3498DB"   # Blue
SUCCESS_COLOR = "#27AE60"   # Green
WARNING_COLOR = "#E67E22"   # Orange
TEXT_COLOR = "#2C3E50"      # Dark Text
LABEL_COLOR = "#7F8C8D"     # Grey Labels
ERROR_COLOR = "#E74C3C"     # Red for *

# API V2 Endpoint for Booking
API_APPOINTMENT_PATH = "/artemis/api/visitor/v2/appointment"
# API to fetch visitor details
API_GET_VISITOR = "/artemis/api/visitor/v1/visitor/single/visitorinfo"

ui_elements = {}
current_visitor_id = None

# ==========================================
# 2. LOGIC HANDLERS
# ==========================================

def fetch_visitor_details(vis_id=None):
    """ Fetches existing visitor info to pre-fill the form """
    if not vis_id:
        vis_id = ui_elements["id_entry"].get()
    
    if not vis_id:
        messagebox.showwarning("Input", "Please enter a Visitor ID first.")
        return

    payload = {"visitorId": vis_id}
    ui_elements["status_lbl"].config(text="Fetching details...", fg=PRIMARY_COLOR)
    
    response = api_handler.call_api(API_GET_VISITOR, payload)

    if response and response.get("code") == "0":
        data = response.get("data", {}).get("VisitorInfo", {})
        if data:
            # Auto-fill fields
            set_entry("fname_entry", data.get("visitorGivenName", ""))
            set_entry("lname_entry", data.get("visitorFamilyName", ""))
            set_entry("phone_entry", data.get("phoneNo", ""))
            set_entry("email_entry", data.get("email", ""))
            set_entry("comp_entry", data.get("companyName", ""))
            set_entry("plate_entry", data.get("plateNo", ""))
            set_entry("group_entry", data.get("visitorGroupName", "Visitors"))
            
            # Gender
            g_val = data.get("gender")
            gen_str = "Male" if str(g_val) == "1" else "Female"
            ui_elements["gender_cb"].set(gen_str)
            
            ui_elements["status_lbl"].config(text="Details Loaded Successfully", fg=SUCCESS_COLOR)
        else:
            ui_elements["status_lbl"].config(text="Visitor ID not found", fg=ERROR_COLOR)
    else:
        ui_elements["status_lbl"].config(text="Fetch Failed", fg=ERROR_COLOR)

def set_entry(key, value):
    if key in ui_elements and value:
        ui_elements[key].delete(0, tk.END)
        ui_elements[key].insert(0, str(value))

def handle_booking(root_instance):
    """ Collects all data and sends the V2 JSON Payload """
    
    # --- 1. Get Values ---
    vis_id = ui_elements["id_entry"].get()
    
    # Dates
    date_start = ui_elements["start_date"].get_date()
    date_end = ui_elements["end_date"].get_date()
    
    # ISO 8601 Strings with Timezone
    fmt_start = date_start.strftime("%Y-%m-%dT09:05:00+05:30")
    fmt_end = date_end.strftime("%Y-%m-%dT19:05:00+05:30")

    # Appointment Details
    rec_id = ui_elements["rec_id_entry"].get()
    purpose = ui_elements["purpose_entry"].get()
    reason_detail = ui_elements["reason_entry"].get()
    
    reason_map = {"Business": 0, "Training": 1, "Visit": 2, "Meeting": 3, "Others": 4}
    reason_type = reason_map.get(ui_elements["reason_type_cb"].get(), 0)

    # Visitor Details
    f_name = ui_elements["fname_entry"].get()
    l_name = ui_elements["lname_entry"].get()
    phone = ui_elements["phone_entry"].get()
    email = ui_elements["email_entry"].get()
    company = ui_elements["comp_entry"].get()
    plate = ui_elements["plate_entry"].get()
    group = ui_elements["group_entry"].get()
    
    gender_map = {"Male": 1, "Female": 2}
    gender_val = gender_map.get(ui_elements["gender_cb"].get(), 1)

    # --- Validation ---
    if not vis_id or not f_name:
        messagebox.showwarning("Required", "Visitor ID and Name are required.")
        return

    # --- 2. Construct Payload ---
    payload = {
        "receptionistId": rec_id,
        "appointStartTime": fmt_start,
        "appointEndTime": fmt_end,
        "visitReasonType": reason_type,
        "visitPurpose": purpose if purpose else "null",
        "visitReasonDetail": reason_detail,
        "visitorInfoList": [
            {
                "VisitorInfo": {
                    "visitorId": vis_id,
                    "visitorFamilyName": l_name if l_name else "Guest",
                    "visitorGivenName": f_name,
                    "visitorGroupName": group,
                    "gender": gender_val,
                    "email": email,
                    "phoneNo": phone,
                    "plateNo": plate,
                    "companyName": company,
                    "certificateType": 111,
                    "remark": "visitor",
                    "accessInfo": {
                        "electrostaticDetectionType": 1,
                        "qrCodeValidNum": 1
                    }
                },
                "cards": [
                    { "cardNo": "123456" }
                ]
            }
        ]
    }

    ui_elements["status_lbl"].config(text="BOOKING...", fg=PRIMARY_COLOR)
    root_instance.update()

    # --- 3. Call API ---
    response = api_handler.call_api(API_APPOINTMENT_PATH, payload)

    # --- 4. Handle Response ---
    if response and response.get("code") == "0":
        data = response.get("data", {})
        appoint_id = data.get("appointRecordId") or data.get("orderId")
        
        if appoint_id:
            messagebox.showinfo("✅ Success", f"Appointment Booked!\nRecord ID: {appoint_id}")
            ui_elements["status_lbl"].config(text=f"BOOKED! ID: {appoint_id}", fg=SUCCESS_COLOR)
        else:
            messagebox.showwarning("Warning", "Booking successful, but No Appointment ID returned.")
            ui_elements["status_lbl"].config(text="SUCCESS (NO ID)", fg=WARNING_COLOR)
    else:
        msg = response.get('msg') if response else "Unknown Error"
        messagebox.showerror("Booking Failed", f"Error: {msg}")
        ui_elements["status_lbl"].config(text="FAILED", fg=ERROR_COLOR)


# ==========================================
# 3. SCROLLABLE UI LAYOUT
# ==========================================

def show_appointment_screen(root_instance, show_main_menu, prefill_visitor_id=None):
    global ui_elements, current_visitor_id
    current_visitor_id = prefill_visitor_id
    ui_elements = {}
    
    # Reset UI
    for widget in root_instance.winfo_children(): widget.destroy()
    root_instance.config(bg=BG_COLOR)
    
    try: root_instance.winfo_toplevel().state('zoomed')
    except: pass

    # --- SCROLLABLE SETUP ---
    main_canvas = tk.Canvas(root_instance, bg=BG_COLOR, highlightthickness=0)
    scrollbar = ttk.Scrollbar(root_instance, orient="vertical", command=main_canvas.yview)
    
    # Inner Frame
    scrollable_frame = tk.Frame(main_canvas, bg=BG_COLOR)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    )

    window_id = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Force Full Width
    def on_canvas_configure(event):
        main_canvas.itemconfig(window_id, width=event.width)
    
    main_canvas.bind("<Configure>", on_canvas_configure)
    main_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    main_canvas.pack(side="left", fill="both", expand=True)

    # --- CONTENT ---
    container = tk.Frame(scrollable_frame, bg=BG_COLOR, padx=60, pady=20)
    container.pack(fill="both", expand=True)

    # --- Header ---
    header_frame = tk.Frame(container, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(0, 10))
    tk.Button(header_frame, text="← Back", command=show_main_menu, bg=BG_COLOR, fg=LABEL_COLOR, bd=0, cursor="hand2").pack(side="left")
    tk.Label(header_frame, text="  |  Book Appointment (Step 2)", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(side="left")

    # --- Card ---
    card = tk.Frame(container, bg=CARD_BG, padx=40, pady=30)
    card.pack(fill="both", expand=True)
    card.columnconfigure(1, weight=1)
    card.columnconfigure(3, weight=1)

    # Styles
    style = ttk.Style()
    style.configure("Modern.TEntry", padding=6)
    style.configure("Modern.TCombobox", padding=6)

    # --- Helper Functions ---
    def add_header(row, text):
        lbl = tk.Label(card, text=text.upper(), font=("Segoe UI", 9, "bold"), bg=CARD_BG, fg="#95A5A6")
        lbl.grid(row=row, column=0, columnspan=4, sticky="w", pady=(20, 5))
        ttk.Separator(card, orient="horizontal").grid(row=row+1, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        return row + 2

    def add_field_label(row, col, label, required=False):
        f = tk.Frame(card, bg=CARD_BG)
        f.grid(row=row, column=col, sticky="w")
        tk.Label(f, text=label, bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 9, "bold")).pack(side="left")
        if required:
            tk.Label(f, text=" *", bg=CARD_BG, fg=ERROR_COLOR, font=("Segoe UI", 10, "bold")).pack(side="left")

    def add_entry(row, col, label, var_name, value="", required=False):
        add_field_label(row, col, label, required)
        e = ttk.Entry(card, font=("Segoe UI", 11), style="Modern.TEntry")
        e.grid(row=row+1, column=col, sticky="ew", padx=(0, 30), pady=(5, 15), ipady=6)
        if value: e.insert(0, str(value))
        ui_elements[var_name] = e
        return e

    def add_combo(row, col, label, var_name, options, default, required=False):
        add_field_label(row, col, label, required)
        c = ttk.Combobox(card, values=options, font=("Segoe UI", 11), state="readonly", style="Modern.TCombobox")
        c.set(default)
        c.grid(row=row+1, column=col, sticky="ew", padx=(0, 30), pady=(5, 15), ipady=6)
        ui_elements[var_name] = c

    def add_date(row, col, label, var_name, required=False):
        add_field_label(row, col, label, required)
        d = DateEntry(card, width=12, background=PRIMARY_COLOR, foreground='white', borderwidth=1, font=("Segoe UI", 11), date_pattern='yyyy-mm-dd')
        d.grid(row=row+1, column=col, sticky="ew", padx=(0, 30), pady=(5, 15), ipady=6)
        ui_elements[var_name] = d

    # ================= FIELDS =================

    # --- SECTION 1: APPOINTMENT ---
    r = add_header(0, "Appointment Details")
    
    # Row 1: ID with Search Button & Receptionist
    add_field_label(r, 0, "Visitor ID", True)
    
    # ID Frame to hold Entry + Button
    id_frame = tk.Frame(card, bg=CARD_BG)
    id_frame.grid(row=r+1, column=0, sticky="ew", padx=(0, 30), pady=(5, 15))
    
    id_entry = ttk.Entry(id_frame, font=("Segoe UI", 11), style="Modern.TEntry")
    id_entry.pack(side="left", fill="x", expand=True, ipady=6)
    ui_elements["id_entry"] = id_entry
    
    search_btn = tk.Button(id_frame, text="🔍", command=lambda: fetch_visitor_details(), 
                           bg="#EAEDED", bd=0, cursor="hand2", padx=10)
    search_btn.pack(side="right", fill="y", padx=(5,0))

    add_entry(r, 2, "Receptionist ID", "rec_id_entry", "1")

    r += 2
    add_date(r, 0, "Start Date", "start_date", True)
    add_date(r, 2, "End Date", "end_date", True)
    
    r += 2
    add_combo(r, 0, "Visit Reason Type", "reason_type_cb", ["Business", "Training", "Visit", "Meeting", "Others"], "Business")
    add_entry(r, 2, "Visit Purpose (Description)", "purpose_entry", "Business Meeting")

    # --- SECTION 2: VISITOR DATA ---
    r += 2
    r = add_header(r, "Visitor Information (Auto-Filled)")

    add_entry(r, 0, "Given Name *", "fname_entry", required=True)
    add_entry(r, 2, "Family Name", "lname_entry")
    
    r += 2
    add_entry(r, 0, "Phone No *", "phone_entry", required=True)
    add_entry(r, 2, "Email", "email_entry")
    
    r += 2
    add_entry(r, 0, "Company", "comp_entry")
    add_entry(r, 2, "Vehicle Plate", "plate_entry")
    
    r += 2
    add_entry(r, 0, "Group Name", "group_entry", "Visitors")
    add_combo(r, 2, "Gender", "gender_cb", ["Male", "Female"], "Male")
    
    # Reason Detail (Optional, put at end)
    r += 2
    add_entry(r, 0, "Reason Detail", "reason_entry")

    # --- Auto-Fill Logic ---
    if prefill_visitor_id:
        ui_elements["id_entry"].insert(0, str(prefill_visitor_id))
        root_instance.after(500, lambda: fetch_visitor_details(prefill_visitor_id))

    # --- Footer ---
    footer = tk.Frame(container, bg=BG_COLOR)
    footer.pack(fill="x", pady=20, side="bottom")
    
    status_frame = tk.Frame(footer, bg="#EAEDED")
    status_frame.pack(side="left", fill="x", expand=True)
    tk.Label(status_frame, text="* Required Fields", bg="#EAEDED", fg=ERROR_COLOR, padx=15, pady=8, font=("Segoe UI", 9, "bold")).pack(side="left")
    ui_elements["status_lbl"] = tk.Label(status_frame, text="Ready", bg="#EAEDED", fg=LABEL_COLOR, font=("Segoe UI", 9))
    ui_elements["status_lbl"].pack(side="left")

    # Action Buttons
    tk.Button(footer, text="CONFIRM BOOKING", bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 11, "bold"), 
              padx=30, pady=10, borderwidth=0, cursor="hand2",
              command=lambda: handle_booking(root_instance)).pack(side="right", padx=15)
              
    tk.Button(footer, text="BACK TO REGISTRATION", bg="#BDC3C7", fg="white", font=("Segoe UI", 11, "bold"), 
              padx=20, pady=10, borderwidth=0, cursor="hand2",
              command=show_main_menu).pack(side="right")