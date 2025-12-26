import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import Api.Common_signature.common_signature_api as api_handler
import json

# ==========================================
# 1. CONFIGURATION & STYLES (LMS THEME)
# ==========================================
BG_MAIN = "white"             
BG_SECTION = "#F3F4F6"        
BG_APP = "#F4F6F7"            
TEXT_HEADER = "#333333"       
TEXT_LABEL = "#555555"        
BORDER_COLOR = "#D1D5DB"      

BTN_PRIMARY = "#4F46E5"       # Indigo
BTN_SUCCESS = "#27AE60"       # Green
BTN_TEXT = "white"

FONT_HEADER = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 9)
FONT_ENTRY = ("Segoe UI", 10)

# API Endpoints
API_APPOINTMENT_PATH = "/artemis/api/visitor/v2/appointment"
API_GET_VISITOR = "/artemis/api/visitor/v1/visitor/single/visitorinfo"

ui_elements = {}
current_visitor_id = None

# ==========================================
# 2. LOGIC HANDLERS (UNCHANGED)
# ==========================================

def fetch_visitor_details(vis_id=None):
    if not vis_id:
        vis_id = ui_elements["id_entry"].get()
    
    if not vis_id:
        messagebox.showwarning("Input", "Please enter a Visitor ID first.")
        return

    payload = {"visitorId": vis_id}
    # ui_elements["status_lbl"].config(text="Fetching details...", fg=BTN_PRIMARY) # Optional status update
    
    response = api_handler.call_api(API_GET_VISITOR, payload)

    if response and response.get("code") == "0":
        data = response.get("data", {}).get("VisitorInfo", {})
        if data:
            set_entry("fname_entry", data.get("visitorGivenName", ""))
            set_entry("lname_entry", data.get("visitorFamilyName", ""))
            set_entry("phone_entry", data.get("phoneNo", ""))
            set_entry("email_entry", data.get("email", ""))
            set_entry("comp_entry", data.get("companyName", ""))
            set_entry("plate_entry", data.get("plateNo", ""))
            set_entry("group_entry", data.get("visitorGroupName", "Visitors"))
            
            g_val = data.get("gender")
            gen_str = "Male" if str(g_val) == "1" else "Female"
            ui_elements["gender_cb"].set(gen_str)
            
            messagebox.showinfo("Found", "Visitor details loaded successfully.")
        else:
            messagebox.showerror("Not Found", "Visitor ID not found.")
    else:
        messagebox.showerror("Error", "Fetch Failed.")

def set_entry(key, value):
    if key in ui_elements:
        ui_elements[key].delete(0, tk.END)
        ui_elements[key].insert(0, str(value))

def handle_booking(root_instance):
    vis_id = ui_elements["id_entry"].get()
    date_start = ui_elements["start_date"].get_date()
    date_end = ui_elements["end_date"].get_date()
    
    fmt_start = date_start.strftime("%Y-%m-%dT09:05:00+05:30")
    fmt_end = date_end.strftime("%Y-%m-%dT19:05:00+05:30")

    rec_id = ui_elements["rec_id_entry"].get()
    purpose = ui_elements["purpose_entry"].get()
    reason_detail = ui_elements["reason_entry"].get()
    
    reason_map = {"Business": 0, "Training": 1, "Visit": 2, "Meeting": 3, "Others": 4}
    reason_type = reason_map.get(ui_elements["reason_type_cb"].get(), 0)

    f_name = ui_elements["fname_entry"].get()
    l_name = ui_elements["lname_entry"].get()
    phone = ui_elements["phone_entry"].get()
    email = ui_elements["email_entry"].get()
    company = ui_elements["comp_entry"].get()
    plate = ui_elements["plate_entry"].get()
    group = ui_elements["group_entry"].get()
    gender_map = {"Male": 1, "Female": 2}
    gender_val = gender_map.get(ui_elements["gender_cb"].get(), 1)

    if not vis_id or not f_name:
        messagebox.showwarning("Required", "Visitor ID and Name are required.")
        return

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
                    "accessInfo": {"electrostaticDetectionType": 1, "qrCodeValidNum": 1}
                },
                "cards": [{ "cardNo": "123456" }]
            }
        ]
    }

    response = api_handler.call_api(API_APPOINTMENT_PATH, payload)

    if response and response.get("code") == "0":
        data = response.get("data", {})
        appoint_id = data.get("appointRecordId") or data.get("orderId")
        messagebox.showinfo("✅ Success", f"Appointment Booked!\nRecord ID: {appoint_id}")
    else:
        msg = response.get('msg') if response else "Unknown Error"
        messagebox.showerror("Booking Failed", f"Error: {msg}")


# ==========================================
# 3. WIDE HORIZONTAL UI (MATCHING REGISTRATION)
# ==========================================

def show_appointment_screen(root_instance, show_main_menu, prefill_visitor_id=None):
    global ui_elements, current_visitor_id
    current_visitor_id = prefill_visitor_id
    ui_elements = {}
    
    # --- RESET ---
    for widget in root_instance.winfo_children(): widget.destroy()
    root_instance.config(bg=BG_APP)
    try: root_instance.state('zoomed')
    except: pass

    # --- TOP BAR ---
    top_bar = tk.Frame(root_instance, bg="white", pady=10, padx=20)
    top_bar.pack(fill="x")
    tk.Button(top_bar, text="← Back", command=show_main_menu, 
              bg="white", fg="#777", bd=0, font=("Segoe UI", 10), cursor="hand2").pack(side="left")
    tk.Label(top_bar, text="  |  Book Appointment", font=("Segoe UI", 16, "bold"), bg="white", fg=TEXT_HEADER).pack(side="left")

    # --- SCROLLABLE CANVAS SETUP ---
    container = tk.Frame(root_instance, bg=BG_APP)
    container.pack(fill="both", expand=True, padx=20, pady=20)

    canvas = tk.Canvas(container, bg=BG_MAIN, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    
    scrollable_frame = tk.Frame(canvas, bg=BG_MAIN, padx=40, pady=30)
    
    # --- CRITICAL FIX: Make inner frame fill the canvas width ---
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def configure_frame_width(event):
        canvas.itemconfig(frame_id, width=event.width)

    scrollable_frame.bind("<Configure>", configure_scroll_region)
    canvas.bind("<Configure>", configure_frame_width)

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
        for i in range(columns):
            f.columnconfigure(i, weight=1)
        return f

    def add_field(parent, label_text, key, row, col, default="", required=False, colspan=1):
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew", columnspan=colspan)
        
        lbl_frame = tk.Frame(f, bg=BG_MAIN)
        lbl_frame.pack(anchor="w", pady=(0, 5))
        tk.Label(lbl_frame, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(side="left")
        if required:
            tk.Label(lbl_frame, text=" *", font=FONT_LABEL, bg=BG_MAIN, fg="red").pack(side="left")

        entry = ttk.Entry(f, font=FONT_ENTRY)
        entry.pack(fill="x", ipady=5)
        if default: entry.insert(0, str(default))
        ui_elements[key] = entry
        return entry

    def add_field_with_btn(parent, label_text, key, row, col, btn_cmd):
        """Special field for Visitor ID with Search Button"""
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew")

        lbl_frame = tk.Frame(f, bg=BG_MAIN)
        lbl_frame.pack(anchor="w", pady=(0, 5))
        tk.Label(lbl_frame, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(side="left")
        tk.Label(lbl_frame, text=" *", font=FONT_LABEL, bg=BG_MAIN, fg="red").pack(side="left")

        # Container for Entry + Button
        box = tk.Frame(f, bg=BG_MAIN)
        box.pack(fill="x")
        
        entry = ttk.Entry(box, font=FONT_ENTRY)
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        btn = tk.Button(box, text="🔍", bg="#E0E0E0", bd=0, padx=10, cursor="hand2", command=btn_cmd)
        btn.pack(side="left", padx=(5,0), fill="y")

        ui_elements[key] = entry

    def add_combo(parent, label_text, key, row, col, values, default_val):
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew")

        tk.Label(f, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(anchor="w", pady=(0, 5))
        combo = ttk.Combobox(f, values=values, font=FONT_ENTRY, state="readonly")
        combo.pack(fill="x", ipady=5)
        combo.set(default_val)
        ui_elements[key] = combo

    def add_date(parent, label_text, key, row, col, required=False):
        f = tk.Frame(parent, bg=BG_MAIN, pady=5, padx=10)
        f.grid(row=row, column=col, sticky="ew")

        lbl_frame = tk.Frame(f, bg=BG_MAIN)
        lbl_frame.pack(anchor="w", pady=(0, 5))
        tk.Label(lbl_frame, text=label_text, font=FONT_LABEL, bg=BG_MAIN, fg=TEXT_LABEL).pack(side="left")
        if required:
            tk.Label(lbl_frame, text=" *", font=FONT_LABEL, bg=BG_MAIN, fg="red").pack(side="left")

        dt = DateEntry(f, width=12, background='#34495E', foreground='white', borderwidth=2, font=FONT_ENTRY, date_pattern='yyyy-mm-dd')
        dt.pack(fill="x", ipady=5)
        ui_elements[key] = dt

    # ==========================
    # FORM CONTENT (4 Columns)
    # ==========================

    # --- 1. APPOINTMENT DETAILS ---
    create_section_header("Appointment Details")
    grid1 = create_grid_frame(columns=4)
    
    # Row 0
    add_field_with_btn(grid1, "Visitor ID", "id_entry", 0, 0, btn_cmd=lambda: fetch_visitor_details())
    add_field(grid1, "Receptionist ID", "rec_id_entry", 0, 1, "1")
    add_date(grid1, "Start Date", "start_date", 0, 2, required=True)
    add_date(grid1, "End Date", "end_date", 0, 3, required=True)

    # Row 1
    add_combo(grid1, "Visit Reason Type", "reason_type_cb", 1, 0, ["Business", "Training", "Visit", "Meeting", "Others"], "Business")
    add_field(grid1, "Visit Purpose (Description)", "purpose_entry", 1, 1, "Business Meeting")
    add_field(grid1, "Reason Detail", "reason_entry", 1, 2, "", colspan=2)

    # --- 2. VISITOR INFORMATION ---
    create_section_header("Visitor Information (Auto-Filled)")
    grid2 = create_grid_frame(columns=4)

    # Row 0
    add_field(grid2, "Given Name", "fname_entry", 0, 0, required=True)
    add_field(grid2, "Family Name", "lname_entry", 0, 1)
    add_field(grid2, "Phone Number", "phone_entry", 0, 2, required=True)
    add_field(grid2, "Email Address", "email_entry", 0, 3)

    # Row 1
    add_field(grid2, "Company", "comp_entry", 1, 0)
    add_field(grid2, "Vehicle Plate", "plate_entry", 1, 1)
    add_field(grid2, "Group Name", "group_entry", 1, 2, "Visitors")
    add_combo(grid2, "Gender", "gender_cb", 1, 3, ["Male", "Female"], "Male")

    # --- FOOTER ---
    btn_frame = tk.Frame(scrollable_frame, bg=BG_MAIN, pady=30)
    btn_frame.pack(fill="x")

    tk.Button(btn_frame, text="CONFIRM BOOKING", bg=BTN_PRIMARY, fg="white", font=("Segoe UI", 10, "bold"),
              padx=25, pady=10, relief="flat", cursor="hand2",
              command=lambda: handle_booking(root_instance)).pack(side="left")

    tk.Button(btn_frame, text="BACK TO REGISTRATION", bg="#95A5A6", fg="white", font=("Segoe UI", 10, "bold"),
              padx=25, pady=10, relief="flat", cursor="hand2",
              command=show_main_menu).pack(side="right")
    
    # Auto-fill if ID provided
    if prefill_visitor_id:
        ui_elements["id_entry"].insert(0, str(prefill_visitor_id))
        root_instance.after(500, lambda: fetch_visitor_details(prefill_visitor_id))