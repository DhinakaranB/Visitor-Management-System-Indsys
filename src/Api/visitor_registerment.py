# add_visitor.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import Api.common_signature_api as api_handler
import Homepage.Ui

# --- Constants ---
BG_COLOR = "#F4F6F7"
PRIMARY_COLOR = "#3498DB"
TEXT_COLOR = "#2C3E50"
VISITOR_API_PATH = "/artemis/api/visitor/v1/appointment"

entries = {}
date_fields = {}
gender_var = None
purpose_var = None  # ✅ added for dropdown tracking


def show_help_info():
    messagebox.showinfo(
        "Help & Info",
        "This form registers a new visitor appointment.\n\n"
        "Cert. Type Codes: 111=ID, 414=Passport, 113=DL, 335=Employee ID, 990=Other",
    )


def clear_form_entries(root_instance):
    """Clears all visitor input fields after a successful API submission."""
    global gender_var, purpose_var
    for key in entries:
        if entries[key].winfo_exists():
            entries[key].delete(0, tk.END)
    if gender_var is not None:
        gender_var.set(1)
    if purpose_var is not None:
        purpose_var.set("Business")  # reset dropdown


def handle_send(root_instance):
    """Collects form data, validates it, and sends to API."""
    global gender_var, purpose_var

    try:
        # --- Date Gathering ---
        try:
            start_date_str = date_fields["visitStart"].get()
            end_date_str = date_fields["visitEnd"].get()

            if not start_date_str or not end_date_str:
                messagebox.showerror("Validation Error", "Visit start and end dates are required.")
                return

            visitStartTime = f"{start_date_str}T09:00:00+08:00"
            visitEndTime = f"{end_date_str}T17:00:00+08:00"

        except Exception:
            messagebox.showerror("Validation Error", "Invalid date format. Please use the calendar picker.")
            return

        # --- Map Dropdown Text to Numeric Value ---
        purpose_map = {
            "Business": 0,
            "Training": 1,
            "Visit": 2,
            "Meeting": 3,
            "Others": 4
        }
        visit_purpose_type = purpose_map.get(purpose_var.get(), 0)

        # --- Construct API Body ---
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
                            "cardNo": entries["cardNo"].get().strip()
                            if entries["cardNo"].get().strip()
                            else "123456"
                        }
                    ],
                }
            ],
        }

        # --- Success Callback ---
        def safe_transition_to_home():
            clear_form_entries(root_instance)
            main_root = root_instance.winfo_toplevel()
            main_root.after(0, Homepage.Ui.show_home)

        api_handler.send_to_api(data_payload, VISITOR_API_PATH, safe_transition_to_home)

    except Exception as e:
        messagebox.showerror("Unhandled Form Error", f"A form error occurred: {str(e)}")


def show_create_form(root_instance, show_main_screen_callback, close_app_callback):
    """Displays the visitor registration form."""
    global gender_var, entries, purpose_var
    root_instance.grid_rowconfigure(2, weight=1)
    root_instance.grid_columnconfigure(0, weight=1)
    row_index = 0

    # Header
    header_frame = tk.Frame(root_instance, bg=BG_COLOR)
    header_frame.grid(row=row_index, column=0, pady=(10, 5), padx=30, sticky="ew")
    row_index += 1

    header_frame.grid_columnconfigure(0, weight=1)
    tk.Label(header_frame, text="Visitor Registration",
             font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w")
    ttk.Button(header_frame, text=" ℹ ", command=show_help_info,
               style="TInfo.TButton", width=4).grid(row=0, column=1, sticky="e", padx=(10, 0))

    info_label = tk.Label(root_instance, text="Please enter the visitor's details.",
                          font=("Segoe UI", 10), bg=BG_COLOR, fg="gray")
    info_label.grid(row=row_index, column=0, pady=(0, 10))
    row_index += 1

    # Form
    form_container = tk.Frame(root_instance, bg=BG_COLOR)
    form_container.grid(row=row_index, column=0, padx=20, pady=10, sticky="nsew")
    row_index += 1
    form_frame = tk.Frame(form_container, bg=BG_COLOR)
    form_frame.grid(row=0, column=0, sticky="w")

    form_frame.grid_columnconfigure(1, weight=1)
    form_frame.grid_columnconfigure(4, weight=1)

    # --- Fields ---
    fields = [
        ("visitStartTime (Date)", "visitStartTime"), ("visitEndTime (Date)", "visitEndTime"),
        ("visitorGivenName", "visitorGivenName"), ("visitorFamilyName", "visitorFamilyName"),
        ("phoneNo", "phoneNo"), ("companyName", "companyName"),
        ("plateNo", "plateNo"), ("visitPurpose", "visitPurpose"),
        ("remark", "remark"), ("cardNo", "cardNo")
    ]

    entries.clear()
    date_fields.clear()
    total_fields = len(fields)
    fields_per_column = (total_fields + 1) // 2

    for i in range(total_fields):
        label_text, key = fields[i]
        if i < fields_per_column:
            col_label, col_input = 0, 1
            row_num = i
        else:
            col_label, col_input = 3, 4
            row_num = i - fields_per_column

        tk.Label(form_frame, text=label_text, font=("Segoe UI", 10),
                 bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row_num, column=col_label,
                                                  sticky="e", pady=5, padx=(0, 10))

        if "Date" in label_text:
            date_field = DateEntry(form_frame, date_pattern='yyyy-mm-dd',
                                   width=20, background=PRIMARY_COLOR, foreground='white')
            date_field.grid(row=row_num, column=col_input,
                            sticky="ew", pady=5, padx=10)
            date_fields[key.split("Time")[0]] = date_field
        else:
            e = ttk.Entry(form_frame, style="TEntry")
            e.grid(row=row_num, column=col_input,
                   sticky="ew", pady=5, padx=10)
            entries[key] = e

    # --- Dropdown for visitPurposeType ---
    row_num += 1
    tk.Label(form_frame, text="Visiting Purpose Type", font=("Segoe UI", 10),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row_num, column=0,
                                              sticky="e", pady=5, padx=(0, 10))

    purpose_var = tk.StringVar(value="Business")
    purpose_dropdown = ttk.Combobox(form_frame, textvariable=purpose_var,
                                    values=["Business", "Training", "Visit", "Meeting", "Others"],
                                    state="readonly", width=18)
    purpose_dropdown.grid(row=row_num, column=1, sticky="w", pady=5, padx=10)

    # --- Gender Row ---
    row_num += 1
    tk.Label(form_frame, text="Gender", font=("Segoe UI", 10),
             bg=BG_COLOR, fg=TEXT_COLOR).grid(row=row_num, column=0,
                                              sticky="e", pady=5, padx=(0, 10))
    gender_frame = tk.Frame(form_frame, bg=BG_COLOR)
    gender_frame.grid(row=row_num, column=1, columnspan=4,
                      sticky="w", pady=5, padx=10)

    if gender_var is None:
        gender_var = tk.IntVar()
    gender_var.set(1)
    ttk.Radiobutton(gender_frame, text="Male", value=1,
                    variable=gender_var).pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Female", value=2,
                    variable=gender_var).pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Unknown", value=0,
                    variable=gender_var).pack(side="left", padx=5)

    # Save Button
    ttk.Button(root_instance, text="💾 Save & Send to API",
               command=lambda: handle_send(root_instance),
               style="TSuccess.TButton").grid(row=row_index, column=0,
                                              pady=(20, 10), ipadx=10, ipady=5, sticky="e", padx=30)
    row_index += 1

    # Footer Navigation
    nav_frame = tk.Frame(root_instance, bg=BG_COLOR)
    nav_frame.grid(row=row_index, column=0, pady=5, sticky="ew")
    ttk.Button(nav_frame, text="⬅ Back to Main Menu",
               command=show_main_screen_callback,
               style="TSecondary.TButton").pack(side=tk.LEFT, padx=10, anchor=tk.W)
