# add_visitor.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
# Import the API handler and Ui for context/utilities
import common_api as api_handler 
import Ui 

# --- Constants ---
BG_COLOR = "#F4F6F7"
PRIMARY_COLOR = "#3498DB"  
TEXT_COLOR = "#2C3E50"
VISITOR_API_PATH = "/artemis/api/visitor/v1/appointment" 

# --- Global Form Variables ---
entries = {}
date_fields = {}
gender_var = None

# --- Helper Functions (Defined before show_create_form) ---

def show_help_info():
    messagebox.showinfo("Help & Info", 
                         "This form registers a new visitor appointment.\n\n"
                         "Cert. Type Codes: 111=ID, 414=Passport, 113=DL, 335=Employee ID, 990=Other")

def clear_form_entries(root_instance):
    """Clears all visitor input fields after a successful API submission."""
    global gender_var
    for key in entries:
        if entries[key].winfo_exists():
            entries[key].delete(0, tk.END)
    
    for key in date_fields:
        pass # DateEntry values often reset automatically or require specific method
        
    if gender_var is not None:
        gender_var.set(1) 

def handle_send(root_instance):
    """
    Gathers form data, validates it, and calls the API handler.
    Uses root.after() for thread-safe UI transition after API call (Fixes 'NoneType' error).
    """
    global gender_var

    try:
        # --- Date Gathering and Validation ---
        try:
            start_date_str = date_fields["visitStart"].get()
            end_date_str = date_fields["visitEnd"].get()
            
            if not start_date_str or not end_date_str:
                 messagebox.showerror("Validation Error", "Visit start and end dates are required.")
                 return
                 
            visitStartTime = f"{start_date_str}T09:00:00+08:00"
            visitEndTime   = f"{end_date_str}T17:00:00+08:00"

        except Exception:
            messagebox.showerror("Validation Error", "Invalid date format. Please use the calendar picker.")
            return

        # Certificate Type Validation
        valid_certificate_types = {111: "ID", 414: "Passport", 113: "DL", 335: "Employee ID", 990: "Other"}
        cert_type_input = entries["certificateType"].get().strip()
        if not cert_type_input:
            messagebox.showerror("Validation Error", "Certificate Type (Code) is required.")
            return

        try:
            cert_type = int(cert_type_input)
            if cert_type not in valid_certificate_types:
                allowed = ", ".join([str(k) for k in valid_certificate_types.keys()])
                raise ValueError(f"Invalid certificateType! Allowed codes: {allowed}")
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return
            
        # Visit Purpose Type Validation
        try:
            purpose_type_val = entries["visitPurposeType"].get().strip()
            visit_purpose_type = int(purpose_type_val) if purpose_type_val else 0
        except ValueError:
            messagebox.showerror("Validation Error", "Visit Purpose Type must be an integer (0 or above).")
            return

        # --- Construct API Body ---
        data_payload = {
            "visitStartTime": visitStartTime, "visitEndTime": visitEndTime,
            "visitPurposeType": visit_purpose_type, "visitPurpose": entries["visitPurpose"].get(),
            "visitorInfoList": [{ "VisitorInfo": {
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
            }}]
        }
        
        # --- Define the safe, post-API success callback ---
        def safe_transition_to_home():
            """Ensures UI cleanup and navigation runs in the main thread."""
            clear_form_entries(root_instance)
            main_root = root_instance.winfo_toplevel()
            main_root.after(0, Ui.show_home) 

        api_handler.send_to_api(data_payload, VISITOR_API_PATH, safe_transition_to_home) 

    except Exception as e:
        messagebox.showerror("Unhandled Form Error", f"A form error occurred: {str(e)}")


# --- Main Form Function ---
def show_create_form(root_instance, show_main_screen_callback, close_app_callback):
    """
    Displays the two-column responsive visitor registration form.
    """
    global gender_var
    global entries
    
    # Configure root_instance grid (outer frame)
    root_instance.grid_rowconfigure(0, weight=0) 
    root_instance.grid_rowconfigure(1, weight=0) 
    root_instance.grid_rowconfigure(2, weight=1) # Form Container expands
    root_instance.grid_rowconfigure(3, weight=0) # Save Button
    root_instance.grid_rowconfigure(4, weight=0) # Nav Frame
    root_instance.grid_columnconfigure(0, weight=1) 
    
    row_index = 0
    
    # --- 1. HEADER (Row 0) ---
    header_frame = tk.Frame(root_instance, bg=BG_COLOR)
    header_frame.grid(row=row_index, column=0, pady=(10, 5), padx=30, sticky='ew') 
    row_index += 1
    
    header_frame.grid_columnconfigure(0, weight=1) 
    header_frame.grid_columnconfigure(1, weight=0)
    
    tk.Label(header_frame, text="Visitor Registration", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w")
    
    ttk.Button(header_frame, text=" ℹ ", command=show_help_info, style="TInfo.TButton", width=4).grid(row=0, column=1, sticky="e", padx=(10, 0))

    # --- 1.5. INFO LABEL (Row 1) ---
    info_label = tk.Label(root_instance, text="Please enter the visitor's appointment and personal details.", font=("Segoe UI", 10), bg=BG_COLOR, fg="gray")
    info_label.grid(row=row_index, column=0, pady=(0, 10), sticky='n')
    row_index += 1
    
    # --- 2. RESPONSIVE FORM CONTAINER (Row 2) ---
    form_container = tk.Frame(root_instance, bg=BG_COLOR)
    form_container.grid(row=row_index, column=0, padx=20, pady=10, sticky='nsew') 
    row_index += 1
    
    # Form Frame: The actual grid layout for fields (anchored left)
    form_frame = tk.Frame(form_container, bg=BG_COLOR)
    form_frame.grid(row=0, column=0, sticky='w')
    form_container.grid_columnconfigure(0, weight=1)
    
    # --- 3. RESPONSIVE FORM GRID CONFIGURATION (5 Columns: Label, Input, Spacer, Label, Input) ---
    form_frame.grid_columnconfigure(0, weight=0) # Label 1
    form_frame.grid_columnconfigure(1, weight=1) # Input 1 
    form_frame.grid_columnconfigure(2, weight=0, minsize=50) # Spacer/Separator
    form_frame.grid_columnconfigure(3, weight=0) # Label 2
    form_frame.grid_columnconfigure(4, weight=1) # Input 2 
    
    # Fields List (must contain all required keys for handle_send)
    fields = [
        ("visitStartTime (Date)", "visitStartTime"), ("visitEndTime (Date)", "visitEndTime"),
        ("visitorGivenName", "visitorGivenName"), ("visitorFamilyName", "visitorFamilyName"), 
        ("email", "email"), ("phoneNo", "phoneNo"), 
        ("companyName", "companyName"), ("plateNo", "plateNo"), 
        ("visitPurpose", "visitPurpose"), ("visitPurposeType", "visitPurposeType"), 
        ("certificateType", "certificateType"), ("certificateNo", "certificateNo"), 
        ("remark", "remark") 
    ]
    
    entries.clear()
    date_fields.clear()
    
    total_fields = len(fields)
    fields_per_column = (total_fields + 1) // 2 
    
    # --- Populate the Two Columns ---
    for i in range(total_fields):
        label_text, key = fields[i]
        
        if i < fields_per_column:
            # First Column (Cols 0, 1)
            col_label, col_input = 0, 1
            row_num = i
        else:
            # Second Column (Cols 3, 4)
            col_label, col_input = 3, 4
            row_num = i - fields_per_column
        
        # 1. Label
        tk.Label(form_frame, text=label_text, font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(
            row=row_num, column=col_label, sticky="e", pady=5, padx=(0, 10))
        
        # 2. Input/Date Picker
        if "Date" in label_text:
            date_field = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=20, background=PRIMARY_COLOR, foreground='white', borderwidth=2, relief="flat") 
            date_field.grid(row=row_num, column=col_input, sticky="ew", pady=5, padx=10) 
            date_fields[key.split("Time")[0]] = date_field
        else:
            e = ttk.Entry(form_frame, style="TEntry") 
            e.grid(row=row_num, column=col_input, sticky="ew", pady=5, padx=10) 
            entries[key] = e
    
    # Determine the next available row after the two columns end for gender radio buttons
    row_num = fields_per_column 

    # --- Explicitly Place Gender Radio Buttons ---
    tk.Label(form_frame, text="gender", font=("Segoe UI", 10), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row_num, column=0, sticky="e", pady=5, padx=(0, 10)) 
    gender_frame = tk.Frame(form_frame, bg=BG_COLOR)
    # Span the input columns (1, 2, 3, 4) for gender buttons for better placement
    gender_frame.grid(row=row_num, column=1, columnspan=4, sticky="w", pady=5, padx=10)

    if gender_var is None: gender_var = tk.IntVar()
    gender_var.set(1)
    
    ttk.Radiobutton(gender_frame, text="Male", value=1, variable=gender_var, style="TRadiobutton").pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Female", value=2, variable=gender_var, style="TRadiobutton").pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Undefined", value=0, variable=gender_var, style="TRadiobutton").pack(side="left", padx=5)
    
    row_num += 1 # Advance row_num for safety

    # Action Button (Row 3 in root_instance grid)
    send_button = ttk.Button(root_instance, text="💾 Save & Send to API", 
                             command=lambda: handle_send(root_instance), 
                             style="TSuccess.TButton")
    # Button moved to the right
    send_button.grid(row=row_index, column=0, pady=(20, 10), ipadx=10, ipady=5, sticky='e', padx=30) 
    row_index += 1
    
    # Navigation Buttons (Footer) (Row 4 in root_instance grid)
    nav_frame = tk.Frame(root_instance, bg=BG_COLOR)
    nav_frame.grid(row=row_index, column=0, pady=5, sticky='ew')
    
    ttk.Button(nav_frame, text="⬅ Back to Main Menu", command=show_main_screen_callback, style="TSecondary.TButton").pack(side=tk.LEFT, padx=10, anchor=tk.W)