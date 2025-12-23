import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import Api.Common_signature.common_signature_api as api_handler

# ==========================================
# 1. CONFIGURATION & STYLES
# ==========================================
BG_COLOR = "#F4F6F7"        # Light Grey (App Background)
CARD_BG = "#FFFFFF"         # White (Form Card Background)
TEXT_COLOR = "#2C3E50"      # Dark Blue/Grey (Text)
PRIMARY_COLOR = "#3498DB"   # Blue (Primary Button/Highlight)
LABEL_COLOR = "#7F8C8D"     # Grey (Field Labels)

VISITOR_API_PATH = "/artemis/api/visitor/v1/appointment"

# Global dictionary to store widget references
entries = {}
date_fields = {}
gender_var = None
purpose_var = None

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def show_help_info():
    messagebox.showinfo(
        "Help & Info",
        "This form registers a new visitor appointment.\n\n"
        "Cert. Type Codes:\n111=ID, 414=Passport, 113=DL, 335=Employee ID, 990=Other"
    )

def clear_form_entries(root_instance):
    global gender_var, purpose_var
    for key in entries:
        if entries[key].winfo_exists():
            entries[key].delete(0, tk.END)
    
    # Reset Defaults
    if gender_var: gender_var.set(1)
    if purpose_var: purpose_var.set("Business")

# ==========================================
# 3. API LOGIC (SAVE & SEND)
# ==========================================
def handle_send(root_instance, on_success_callback):
    global gender_var, purpose_var

    try:
        # --- Validation ---
        start_date_str = date_fields["visitStart"].get()
        end_date_str = date_fields["visitEnd"].get()

        if not start_date_str or not end_date_str:
            messagebox.showerror("Validation Error", "Visit start and end dates are required.")
            return

        # --- Prepare Data ---
        visitStartTime = f"{start_date_str}T09:00:00+08:00"
        visitEndTime = f"{end_date_str}T17:00:00+08:00"

        purpose_map = {"Business": 0, "Training": 1, "Visit": 2, "Meeting": 3, "Others": 4}
        visit_purpose_type = purpose_map.get(purpose_var.get(), 0)

        # --- Construct Payload ---
        data_payload = {
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
                            "cardNo": entries["cardNo"].get().strip() if entries["cardNo"].get().strip() else "123456"
                        }
                    ],
                }
            ],
        }

        # --- Success Callback ---
        def safe_transition_to_home():
            clear_form_entries(root_instance)
            root_instance.after(0, on_success_callback)

        # --- Execute API Call ---
        api_handler.send_to_api(data_payload, VISITOR_API_PATH, safe_transition_to_home)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ==========================================
# 4. FULL UI LAYOUT
# ==========================================
def show_create_form(root_instance, show_main_screen_callback, close_app_callback, visitor_id=None):
    global gender_var, entries, purpose_var, date_fields

    # --- Reset Root ---
    root_instance.config(bg=BG_COLOR)
    for widget in root_instance.winfo_children():
        widget.destroy()

    # --- Grid Configuration for Centering ---
    # Column 0 & 2 are spacers. Column 1 is the content.
    root_instance.grid_columnconfigure(0, weight=1)
    root_instance.grid_columnconfigure(1, weight=0) 
    root_instance.grid_columnconfigure(2, weight=1)
    root_instance.grid_rowconfigure(0, weight=1)

    # --- Main Container ---
    main_container = tk.Frame(root_instance, bg=BG_COLOR)
    main_container.grid(row=0, column=1, sticky="n", pady=30)

    # ================= HEADER SECTION =================
    header_frame = tk.Frame(main_container, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(0, 20))

    # Breadcrumb Link (Cancel)
    btn_back = tk.Button(
        header_frame, 
        text="← Cancel", 
        command=show_main_screen_callback,
        bg=BG_COLOR, fg="#7F8C8D", bd=0, font=("Segoe UI", 9), cursor="hand2", activebackground=BG_COLOR
    )
    btn_back.pack(side="top", anchor="w", pady=(0, 5))

    # Title Row
    title_row = tk.Frame(header_frame, bg=BG_COLOR)
    title_row.pack(fill="x")
    
    tk.Label(
        title_row, 
        text="New Appointment", 
        font=("Segoe UI", 24, "bold"), 
        bg=BG_COLOR, fg=TEXT_COLOR
    ).pack(side="left")

    tk.Button(
        title_row, text="ℹ Help", bg="white", relief="flat", fg=PRIMARY_COLOR, command=show_help_info
    ).pack(side="right")

    # ================= FORM CARD (White Box) =================
    form_card = tk.Frame(main_container, bg=CARD_BG, padx=40, pady=40)
    form_card.pack(fill="both", expand=True)

    # Configure Internal Grid: [Label] [Input] [Gap] [Label] [Input]
    form_card.columnconfigure(1, weight=1)
    form_card.columnconfigure(3, weight=1)

    entries.clear()
    date_fields.clear()

    # --- Helper to create standard rows ---
    def add_row(row_idx, label1, widget1, label2=None, widget2=None):
        # Upper Case Labels
        l1_text = label1.upper()
        
        tk.Label(
            form_card, text=l1_text, font=("Segoe UI", 8, "bold"), 
            bg=CARD_BG, fg=LABEL_COLOR
        ).grid(row=row_idx, column=0, sticky="w", pady=(15, 5))
        
        widget1.grid(row=row_idx, column=1, sticky="ew", padx=(0, 20))

        if label2 and widget2:
            l2_text = label2.upper()
            tk.Label(
                form_card, text=l2_text, font=("Segoe UI", 8, "bold"), 
                bg=CARD_BG, fg=LABEL_COLOR
            ).grid(row=row_idx, column=2, sticky="w", pady=(15, 5), padx=(20, 0))
            
            widget2.grid(row=row_idx, column=3, sticky="ew")

    # === ROW 1: DATES ===
    d_start = DateEntry(form_card, width=20, date_pattern="yyyy-mm-dd", background=PRIMARY_COLOR, foreground="white")
    d_end = DateEntry(form_card, width=20, date_pattern="yyyy-mm-dd", background=PRIMARY_COLOR, foreground="white")
    
    add_row(0, "Visit Start Time", d_start, "Visit End Time", d_end)
    date_fields["visitStart"] = d_start
    date_fields["visitEnd"] = d_end

    # === ROW 2: NAMES ===
    e_given = ttk.Entry(form_card)
    e_family = ttk.Entry(form_card)
    
    add_row(1, "Visitor Given Name", e_given, "Visitor Family Name", e_family)
    entries["visitorGivenName"] = e_given
    entries["visitorFamilyName"] = e_family

    # === ROW 3: CONTACT ===
    e_phone = ttk.Entry(form_card)
    e_comp = ttk.Entry(form_card)
    
    add_row(2, "Phone No", e_phone, "Company Name", e_comp)
    entries["phoneNo"] = e_phone
    entries["companyName"] = e_comp

    # === ROW 4: ID & PLATE ===
    e_card = ttk.Entry(form_card)
    e_plate = ttk.Entry(form_card)
    
    add_row(3, "Card No", e_card, "Vehicle Plate No", e_plate)
    entries["cardNo"] = e_card
    entries["plateNo"] = e_plate

    # === ROW 5: PURPOSE & GENDER ===
    purpose_var = tk.StringVar(value="Business")
    cb_purpose = ttk.Combobox(
        form_card, textvariable=purpose_var, state="readonly",
        values=["Business", "Training", "Visit", "Meeting", "Others"]
    )

    gender_frame = tk.Frame(form_card, bg=CARD_BG)
    gender_var = tk.IntVar(value=1)
    
    ttk.Radiobutton(gender_frame, text="Male", value=1, variable=gender_var).pack(side="left", padx=(0,15))
    ttk.Radiobutton(gender_frame, text="Female", value=2, variable=gender_var).pack(side="left", padx=(0,15))
    ttk.Radiobutton(gender_frame, text="Unknown", value=0, variable=gender_var).pack(side="left")

    add_row(4, "Visit Purpose", cb_purpose, "Gender", gender_frame)

    # === ROW 6: REMARKS (Full Width) ===
    tk.Label(
        form_card, text="REMARKS", font=("Segoe UI", 8, "bold"), 
        bg=CARD_BG, fg=LABEL_COLOR
    ).grid(row=5, column=0, sticky="w", pady=(20, 5))
    
    e_remark = ttk.Entry(form_card)
    e_remark.grid(row=5, column=1, columnspan=3, sticky="ew", pady=(0, 10))
    entries["remark"] = e_remark

    # ================= FOOTER BUTTONS =================
    # Horizontal Line
    ttk.Separator(form_card, orient='horizontal').grid(row=6, column=0, columnspan=4, sticky="ew", pady=(20, 20))

    btn_frame = tk.Frame(form_card, bg=CARD_BG)
    btn_frame.grid(row=7, column=0, columnspan=4, sticky="e")

    # Cancel Button
    btn_cancel = tk.Button(
        btn_frame, 
        text="Cancel", 
        command=show_main_screen_callback,
        bg="white", fg="#555", font=("Segoe UI", 9), bd=1, relief="solid", padx=15, pady=6, cursor="hand2"
    )
    btn_cancel.pack(side="left", padx=(0, 10))

    # Confirm Button
    btn_save = tk.Button(
        btn_frame, 
        text="Confirm Registration", 
        command=lambda: handle_send(root_instance, show_main_screen_callback),
        bg=PRIMARY_COLOR, fg="white", font=("Segoe UI", 9, "bold"), bd=0, padx=20, pady=7, cursor="hand2"
    )
    btn_save.pack(side="left")