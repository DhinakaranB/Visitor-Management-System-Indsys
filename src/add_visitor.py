# add_visitor.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import common_api as api_handler 
import Ui as main_app              

# --- API Path for this specific form ---
VISITOR_API_PATH = "/artemis/api/visitor/v1/appointment" 

# --- Global Variables for this Form ---
entries = {}
date_fields = {}
gender_var = None

# --- Custom Color Palette (Must match Ui.py) ---
BG_COLOR = "#F7F8FA"       
TEXT_COLOR = "#333333"
PRIMARY_COLOR = "#3498DB"  

def clear_form_entries(root_instance):
    """Clears all visitor input fields in the given root window."""
    global gender_var
    for key in entries:
        if entries[key].winfo_exists():
            entries[key].delete(0, tk.END)
    
    if gender_var is not None:
        gender_var.set(1) 

def handle_send(root_instance):
    """Gathers form data, validates it, and prepares the payload for the API handler."""
    global gender_var

    try:
        # --- Date/Time Formatting ---
        start_date_str = date_fields["visitStart"].get()
        end_date_str = date_fields["visitEnd"].get()
        
        visitStartTime = f"{start_date_str}T09:00:00+08:00"
        visitEndTime   = f"{end_date_str}T17:00:00+08:00"

        # --- Data Validation ---
        valid_certificate_types = {
            111: "ID", 414: "Passport", 113: "DL", 335: "Employee ID", 990: "Other"
        }
        cert_type_input = entries["certificateType"].get().strip()
        
        if not cert_type_input:
            messagebox.showerror("Validation Error", "certificateType cannot be empty.")
            return

        try:
            cert_type = int(cert_type_input)
            if cert_type not in valid_certificate_types:
                allowed = ", ".join([f"{k} ({v})" for k, v in valid_certificate_types.items()])
                raise ValueError(f"Invalid certificateType! Allowed values: {allowed}")

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return
            
        try:
            visit_purpose_type = int(entries["visitPurposeType"].get() or 0)
        except ValueError:
            messagebox.showerror("Validation Error", "visitPurposeType must be an integer.")
            return

        # --- Construct API Body ---
        data_payload = {
            "visitStartTime": visitStartTime,
            "visitEndTime": visitEndTime,
            "visitPurposeType": visit_purpose_type,
            "visitPurpose": entries["visitPurpose"].get(),
            "visitorInfoList": [
                { "VisitorInfo": {
                    "visitorFamilyName": entries["visitorFamilyName"].get(),
                    "visitorGivenName": entries["visitorGivenName"].get(),
                    "gender": gender_var.get(),
                    "email": entries["email"].get(),
                    "phoneNo": entries["phoneNo"].get(),
                    "plateNo": entries["plateNo"].get(),
                    "companyName": entries["companyName"].get(),
                    "certificateType": cert_type,
                    "certificateNo": entries["certificateNo"].get(),
                    "remark": entries["remark"].get()
                }}
            ]
        }
        
        # Call the API handler, passing the data payload, the API path, and the clear callback
        api_handler.send_to_api(data_payload, VISITOR_API_PATH, lambda: clear_form_entries(root_instance))

    except Exception as e:
        messagebox.showerror("Unhandled Error", str(e))


def show_create_form(root_instance, show_main_screen_callback, close_app_callback):
    """
    Displays the visitor registration form.
    """
    main_app.clear_screen(root_instance) 
    global gender_var
    global entries
    
    # 1. Main Header
    tk.Label(root_instance, text="Visitor Registration", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(10, 5))

    # 2. Sub-Header/Instruction
    tk.Label(root_instance, text="Please enter the visitor's appointment and personal details.", font=("Segoe UI", 10), bg=BG_COLOR, fg="gray").pack(pady=(0, 10))
    
    # Main frame for the form content
    form_frame = tk.Frame(root_instance, bg=BG_COLOR)
    form_frame.pack(padx=30, pady=10, anchor='n') 

    # Define the fields
    fields = [
        "visitStartTime (Date)", "visitEndTime (Date)",
        "visitorGivenName", "visitorFamilyName", "email", "phoneNo",
        "companyName", "plateNo", "visitPurpose", "visitPurposeType",
        "certificateType", "certificateNo", "remark"
    ]
    api_keys = [
        "visitStartTime", "visitEndTime",
        "visitorGivenName", "visitorFamilyName", "email", "phoneNo",
        "companyName", "plateNo", "visitPurpose", "visitPurposeType",
        "certificateType", "certificateNo", "remark"
    ]
    
    entries.clear()
    row_num = 0
    
    for i, label_text in enumerate(fields):
        key = api_keys[i]
        
        tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row_num, column=0, sticky="w", pady=5)
        
        # Handle Date Pickers
        if "Date" in label_text:
            date_field = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=20, background=PRIMARY_COLOR, foreground='white', borderwidth=2, relief="flat")
            date_field.grid(row=row_num, column=1, sticky="w", pady=5, padx=10)
            date_fields[key.split("Time")[0]] = date_field
            
        # Handle standard text Entry fields
        else:
            e = ttk.Entry(form_frame, width=25, style="TEntry") 
            e.grid(row=row_num, column=1, sticky="w", pady=5, padx=10)
            entries[key] = e
            
        row_num += 1

    # Gender Radio Buttons
    tk.Label(form_frame, text="gender", font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row_num, column=0, sticky="w", pady=5)
    gender_frame = tk.Frame(form_frame, bg=BG_COLOR)
    gender_frame.grid(row=row_num, column=1, sticky="w", pady=5, padx=10)

    if gender_var is None:
        gender_var = tk.IntVar()
    
    gender_var.set(1)
    
    ttk.Radiobutton(gender_frame, text="Male", value=1, variable=gender_var, style="TRadiobutton").pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Female", value=2, variable=gender_var, style="TRadiobutton").pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Undefined", value=0, variable=gender_var, style="TRadiobutton").pack(side="left", padx=5)
    
    # Action Buttons
    ttk.Button(root_instance, text="💾 Save & Send to API", 
               command=lambda: handle_send(root_instance), 
               style="TSuccess.TButton").pack(pady=(20, 10), ipadx=15, ipady=8)
    
    nav_frame = tk.Frame(root_instance, bg=BG_COLOR)
    nav_frame.pack(pady=5)
    
    ttk.Button(nav_frame, text="⬅ Back to Main Menu", command=show_main_screen_callback, style="TSecondary.TButton").pack(side=tk.LEFT, padx=10)
    ttk.Button(nav_frame, text="❌ Close Form", command=close_app_callback, style="TDanger.TButton").pack(side=tk.LEFT, padx=10)