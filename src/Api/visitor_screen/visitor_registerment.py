# add_visitor.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import Api.Common_signature.common_signature_api as api_handler
import Api.Homepage.Ui

# ===== COLORS =====
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
CARD_BG = "white"

VISITOR_API_PATH = "/artemis/api/visitor/v1/appointment"

entries = {}
date_fields = {}
gender_var = None
purpose_var = None


# ------------------------------------------------------
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

    gender_var.set(1)
    purpose_var.set("Business")


# ------------------------------------------------------
def handle_send(root_instance):
    global gender_var, purpose_var

    try:
        start_date_str = date_fields["visitStart"].get()
        end_date_str = date_fields["visitEnd"].get()

        if not start_date_str or not end_date_str:
            messagebox.showerror("Validation Error", "Visit start and end dates are required.")
            return

        visitStartTime = f"{start_date_str}T09:00:00+08:00"
        visitEndTime = f"{end_date_str}T17:00:00+08:00"

        purpose_map = {
            "Business": 0,
            "Training": 1,
            "Visit": 2,
            "Meeting": 3,
            "Others": 4
        }

        visit_purpose_type = purpose_map.get(purpose_var.get(), 0)

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

        def safe_transition_to_home():
            clear_form_entries(root_instance)
            root_instance.after(0, Api.Homepage.Ui.show_home)

        api_handler.send_to_api(data_payload, VISITOR_API_PATH, safe_transition_to_home)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# ------------------------------------------------------
def show_create_form(root_instance, show_main_screen_callback, close_app_callback):
    global gender_var, entries, purpose_var
    root_instance.config(bg=BG_COLOR)

    for widget in root_instance.winfo_children():
        widget.destroy()

    root_instance.grid_rowconfigure(3, weight=1)
    root_instance.grid_columnconfigure(0, weight=1)

    row_index = 0

    # ===== HEADER =====
    header = tk.Frame(root_instance, bg=BG_COLOR)
    header.grid(row=row_index, column=0, pady=(15, 5), sticky="ew")
    header.grid_columnconfigure(0, weight=1)

    tk.Label(
        header,
        text="Visitor Registration",
        font=("Segoe UI", 20, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).grid(row=0, column=0, sticky="w", padx=20)

    ttk.Button(header, text="ℹ", width=3, command=show_help_info).grid(row=0, column=1, padx=20)
    row_index += 1

    tk.Label(
        root_instance,
        text="Please enter the visitor's details.",
        font=("Segoe UI", 10),
        bg=BG_COLOR,
        fg="gray"
    ).grid(row=row_index, column=0, sticky="w", padx=30)
    row_index += 1

    # ===== PROFESSIONAL FORM CARD =====
    ENTRY_WIDTH = 26
    PADX = 15
    PADY = 8

    form_card = tk.Frame(root_instance, bg=CARD_BG, padx=30, pady=25)
    form_card.grid(row=row_index, column=0, padx=40, pady=20, sticky="nsew")
    row_index += 1

    for col in range(5):
        form_card.grid_columnconfigure(col, weight=1)

    entries.clear()
    date_fields.clear()

    # ===== FORM FIELD BUILDER =====
    def add_field(row, label, widget, side="left"):
        if side == "left":
            c1, c2 = 0, 1
        else:
            c1, c2 = 3, 4

        tk.Label(
            form_card,
            text=label,
            bg=CARD_BG,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10)
        ).grid(row=row, column=c1, sticky="e", padx=PADX, pady=PADY)

        widget.grid(row=row, column=c2, sticky="w", padx=PADX, pady=PADY)

    # ===== LEFT SIDE FIELDS =====
    add_field(0, "visit Start Time (Date)",
              DateEntry(form_card, width=ENTRY_WIDTH, date_pattern="yyyy-mm-dd"), "left")
    date_fields["visitStart"] = form_card.grid_slaves(row=0, column=1)[0]

    add_field(1, "visitor Given Name", ttk.Entry(form_card, width=ENTRY_WIDTH), "left")
    entries["visitorGivenName"] = form_card.grid_slaves(row=1, column=1)[0]

    add_field(2, "Phone No", ttk.Entry(form_card, width=ENTRY_WIDTH), "left")
    entries["phoneNo"] = form_card.grid_slaves(row=2, column=1)[0]

    add_field(3, "Remark", ttk.Entry(form_card, width=ENTRY_WIDTH), "left")
    entries["remark"] = form_card.grid_slaves(row=3, column=1)[0]

    # ===== RIGHT SIDE FIELDS =====
    add_field(0, "visit End Time(Date)",
              DateEntry(form_card, width=ENTRY_WIDTH, date_pattern="yyyy-mm-dd"), "right")
    date_fields["visitEnd"] = form_card.grid_slaves(row=0, column=4)[0]

    add_field(1, "visitor Family Name", ttk.Entry(form_card, width=ENTRY_WIDTH), "right")
    entries["visitorFamilyName"] = form_card.grid_slaves(row=1, column=4)[0]

    add_field(2, "Company Name", ttk.Entry(form_card, width=ENTRY_WIDTH), "right")
    entries["companyName"] = form_card.grid_slaves(row=2, column=4)[0]

    add_field(3, "Card No", ttk.Entry(form_card, width=ENTRY_WIDTH), "right")
    entries["cardNo"] = form_card.grid_slaves(row=3, column=4)[0]

    # PlateNo (extra field right side)
    add_field(4, "Plate No", ttk.Entry(form_card, width=ENTRY_WIDTH), "left")
    entries["plateNo"] = form_card.grid_slaves(row=4, column=1)[0]

    # ===== Visiting Purpose Type =====
    tk.Label(form_card, text="Visiting Purpose Type", bg=CARD_BG, fg=TEXT_COLOR).grid(
        row=5, column=0, sticky="e", padx=PADX, pady=PADY
    )
    purpose_var = tk.StringVar(value="Business")
    purpose_dropdown = ttk.Combobox(
        form_card,
        textvariable=purpose_var,
        values=["Business", "Training", "Visit", "Meeting", "Others"],
        state="readonly",
        width=24
    )
    purpose_dropdown.grid(row=5, column=1, sticky="w", padx=PADX, pady=PADY)

    # ===== Gender =====
    tk.Label(form_card, text="Gender", bg=CARD_BG, fg=TEXT_COLOR).grid(
        row=6, column=0, sticky="e", padx=PADX
    )

    gender_frame = tk.Frame(form_card, bg=CARD_BG)
    gender_frame.grid(row=6, column=1, sticky="w")

    gender_var = tk.IntVar(value=1)
    ttk.Radiobutton(gender_frame, text="Male", value=1, variable=gender_var).pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Female", value=2, variable=gender_var).pack(side="left", padx=5)
    ttk.Radiobutton(gender_frame, text="Unknown", value=0, variable=gender_var).pack(side="left", padx=5)

    # ===== SAVE BUTTON =====
    save_btn = ttk.Button(
        root_instance,
        text="💾 Save & Send to API",
        command=lambda: handle_send(root_instance)
    )
    save_btn.grid(row=row_index, column=0, sticky="e", padx=40, pady=(10, 20))
    row_index += 1

    # ===== FOOTER NAV =====
    footer = tk.Frame(root_instance, bg=BG_COLOR)
    footer.grid(row=row_index, column=0, pady=10, sticky="w")

    ttk.Button(
        footer,
        text="⬅ Back to Main Menu",
        command=show_main_screen_callback
    ).pack(side="left", padx=20)
