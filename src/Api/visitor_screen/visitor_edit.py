import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import Api.Common_signature.common_signature_api as api_handler

# ===== COLORS =====
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
CARD_BG = "white"

# API Endpoint for Updating
UPDATE_API_PATH = "/artemis/api/visitor/v2/appointment/update"

# Global references
entries = {}
date_fields = {}
gender_var = None
purpose_var = None
current_appoint_id = None


# ------------------------------------------------------
# HANDLE UPDATE SUBMISSION
# ------------------------------------------------------
def handle_update(root_instance, on_success_callback):
    global current_appoint_id
    
    if not current_appoint_id:
        messagebox.showerror("Error", "No Appointment ID found for update.")
        return

    # 1. Validate Dates
    start_date = date_fields["visitStart"].get_date()
    end_date = date_fields["visitEnd"].get_date()
    
    if not start_date or not end_date:
        messagebox.showerror("Error", "Start and End dates are required.")
        return

    # 2. Format Dates (Keeping 09:00 - 17:00 default time for now)
    visitStartTime = start_date.strftime("%Y-%m-%dT09:00:00+05:30")
    visitEndTime = end_date.strftime("%Y-%m-%dT17:00:00+05:30")

    # 3. Map Purpose String to Integer
    purpose_map = {"Business": 0, "Training": 1, "Visit": 2, "Meeting": 3, "Others": 4}
    visit_purpose_type = purpose_map.get(purpose_var.get(), 0)

    # 4. Construct Payload
    payload = {
        "appointRecordId": current_appoint_id,  # REQUIRED for update
        "visitStartTime": visitStartTime,
        "visitEndTime": visitEndTime,
        "visitPurposeType": visit_purpose_type,
        "visitPurpose": purpose_var.get(),
        "visitorInfoList": [
            {
                "VisitorInfo": {
                    "visitorFamilyName": entries["visitorFamilyName"].get(),
                    "visitorGivenName": entries["visitorGivenName"].get(),
                    "gender": gender_var.get(),
                    "phoneNo": entries["phoneNo"].get(),
                    "plateNo": entries["plateNo"].get(),
                    "companyName": entries["companyName"].get(),
                    "remark": entries["remark"].get(),
                },
                "cards": [
                    {
                        "cardNo": entries["cardNo"].get().strip() or "123456"
                    }
                ],
            }
        ],
    }

    # 5. Send to API
    def success_wrapper():
        messagebox.showinfo("Success", "Appointment Updated Successfully!")
        on_success_callback() # Return to list

    api_handler.send_to_api(payload, UPDATE_API_PATH, success_wrapper)


# ------------------------------------------------------
# SHOW EDIT UI
# ------------------------------------------------------
def show_visitor_edit(root_instance, show_main_screen_callback, existing_data=None):
    """
    Renders the Edit Form and pre-fills it with existing_data.
    """
    global gender_var, entries, purpose_var, current_appoint_id
    
    current_appoint_id = existing_data.get("appointID") if existing_data else None

    # Clear screen
    root_instance.config(bg=BG_COLOR)
    for widget in root_instance.winfo_children():
        widget.destroy()

    # Grid Config
    root_instance.grid_rowconfigure(3, weight=1)
    root_instance.grid_columnconfigure(0, weight=1)

    # --- Header ---
    header = tk.Frame(root_instance, bg=BG_COLOR)
    header.grid(row=0, column=0, pady=(15, 5), sticky="ew")
    tk.Label(
        header, 
        text=f"Edit Appointment ({current_appoint_id})", 
        font=("Segoe UI", 18, "bold"), 
        bg=BG_COLOR, 
        fg=TEXT_COLOR
    ).pack(side="left", padx=20)

    # --- Form Container ---
    form_card = tk.Frame(root_instance, bg=CARD_BG, padx=30, pady=25)
    form_card.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")

    entries = {}
    date_fields = {}

    # Helper to build fields
    def add_field(row, col, label, key, is_date=False):
        tk.Label(form_card, text=label, bg=CARD_BG, font=("Segoe UI", 10)).grid(row=row, column=col, sticky="e", padx=10, pady=8)
        if is_date:
            widget = DateEntry(form_card, width=26, date_pattern="yyyy-mm-dd")
            date_fields[key] = widget
        else:
            widget = ttk.Entry(form_card, width=26)
            entries[key] = widget
        widget.grid(row=row, column=col+1, sticky="w", padx=10, pady=8)

    # Left Column
    add_field(0, 0, "Visit Start:", "visitStart", is_date=True)
    add_field(1, 0, "Given Name:", "visitorGivenName")
    add_field(2, 0, "Phone No:", "phoneNo")
    add_field(3, 0, "Remark:", "remark")
    add_field(4, 0, "Plate No:", "plateNo")

    # Right Column
    add_field(0, 3, "Visit End:", "visitEnd", is_date=True)
    add_field(1, 3, "Family Name:", "visitorFamilyName")
    add_field(2, 3, "Company:", "companyName")
    add_field(3, 3, "Card No:", "cardNo")

    # Purpose Dropdown
    tk.Label(form_card, text="Purpose:", bg=CARD_BG).grid(row=5, column=0, sticky="e", padx=10)
    purpose_var = tk.StringVar(value="Business")
    ttk.Combobox(form_card, textvariable=purpose_var, 
                 values=["Business", "Meeting", "Visit", "Training", "Others"]).grid(row=5, column=1, sticky="w", padx=10)

    # Gender Radio
    tk.Label(form_card, text="Gender:", bg=CARD_BG).grid(row=6, column=0, sticky="e", padx=10)
    gender_var = tk.IntVar(value=1)
    gf = tk.Frame(form_card, bg=CARD_BG)
    gf.grid(row=6, column=1, sticky="w")
    for txt, val in [("Male", 1), ("Female", 2)]:
        ttk.Radiobutton(gf, text=txt, variable=gender_var, value=val).pack(side="left", padx=5)


    # --- PRE-FILL DATA ---
    if existing_data:
        try:
            v_info = existing_data.get("visitorInfo", {}) or {}
            
            # Fill Text Fields
            entries["visitorGivenName"].insert(0, v_info.get("visitorGivenName", ""))
            entries["visitorFamilyName"].insert(0, v_info.get("visitorFamilyName", ""))
            entries["phoneNo"].insert(0, v_info.get("phoneNo", ""))
            entries["companyName"].insert(0, v_info.get("companyName", ""))
            entries["plateNo"].insert(0, v_info.get("plateNo", ""))
            entries["remark"].insert(0, v_info.get("remark", ""))

            # Fill Dates
            s_time = existing_data.get("appointStartTime", "")
            e_time = existing_data.get("appointEndTime", "")
            if s_time: 
                date_fields["visitStart"].set_date(datetime.strptime(s_time[:10], "%Y-%m-%d"))
            if e_time: 
                date_fields["visitEnd"].set_date(datetime.strptime(e_time[:10], "%Y-%m-%d"))

            # Fill Dropdowns
            gender_val = v_info.get("gender")
            if gender_val: gender_var.set(int(gender_val))

            reason = existing_data.get("visitorReasonName")
            if reason: purpose_var.set(reason)

        except Exception as e:
            print(f"Error pre-filling form: {e}")

    # --- Buttons ---
    btn_frame = tk.Frame(root_instance, bg=BG_COLOR)
    btn_frame.grid(row=2, column=0, pady=20)

    ttk.Button(btn_frame, text="🔄 Update Appointment", 
               command=lambda: handle_update(root_instance, show_main_screen_callback)).pack(side="left", padx=10)
    
    ttk.Button(btn_frame, text="❌ Cancel", 
               command=show_main_screen_callback).pack(side="left", padx=10)