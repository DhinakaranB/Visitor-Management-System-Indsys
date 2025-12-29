import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
import json
import urllib3
from tkcalendar import DateEntry 

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None
    
# Import our new Edit module
from src.Api.person_screen import person_edit

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ADD_API_PATH = "/artemis/api/resource/v1/person/single/add"

def generate_unique_id():
    timestamp = datetime.now().strftime("%Y%m%d")
    rand_num = random.randint(1000, 9999)
    return f"{timestamp}{rand_num}"

def show_create_form(parent_frame, on_success_callback=None, edit_data=None):
    """
    edit_data: Dict of person details. If NOT None, form opens in 'Edit Mode'.
    """
    for widget in parent_frame.winfo_children():
        widget.destroy()

    is_edit = edit_data is not None
    title_txt = f"Edit Person ({edit_data['personCode']})" if is_edit else "Add Person (Secure API)"
    btn_txt = "Update Person" if is_edit else "Submit"
    btn_color = "#ffc107" if is_edit else "#28a745"

    # Header
    header_frame = tk.Frame(parent_frame, bg="white", pady=10)
    header_frame.pack(fill="x")
    tk.Button(header_frame, text="← Back", bg="white", bd=0, font=("Segoe UI", 10), 
              command=on_success_callback).pack(side="left", padx=10)
    tk.Label(header_frame, text=title_txt, font=("Segoe UI", 18, "bold"), bg="white").pack(side="left", padx=10)

    form_frame = tk.Frame(parent_frame, bg="white", padx=30, pady=20)
    form_frame.pack(fill="both", expand=True)

    # --- VARIABLES (Pre-fill if editing) ---
    vars = {
        "id": tk.StringVar(value=edit_data.get("personCode") if is_edit else generate_unique_id()),
        "first_name": tk.StringVar(value=edit_data.get("personGivenName", "") if is_edit else ""),
        "last_name": tk.StringVar(value=edit_data.get("personFamilyName", "") if is_edit else ""),
        "phone": tk.StringVar(value=edit_data.get("phoneNo", "") if is_edit else ""),
        "email": tk.StringVar(value=edit_data.get("email", "") if is_edit else ""),
        # Safely get card No
        "card": tk.StringVar(value=edit_data.get("cards", [{}])[0].get("cardNo", "") if is_edit and edit_data.get("cards") else ""),
        "gender": tk.StringVar(value="1 - Male"), 
        "remark": tk.StringVar(value=edit_data.get("remark", "") if is_edit else "")
    }
    
    # Set Gender Logic
    if is_edit:
        g_val = str(edit_data.get("gender", "1"))
        vars["gender"].set("1 - Male" if g_val == "1" else "2 - Female")

    # --- FIELDS ---
    row_idx = 0
    def add_row(label, var, readonly=False):
        nonlocal row_idx
        tk.Label(form_frame, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
        ent = tk.Entry(form_frame, textvariable=var, font=("Segoe UI", 10), width=40, bg="#eee" if readonly else "white")
        if readonly: ent.config(state="readonly")
        ent.grid(row=row_idx, column=1, pady=(5, 10), padx=20, sticky="w")
        row_idx += 1

    # ID is Read-Only in Edit Mode (Primary Key)
    add_row("Person Code (ID):", vars["id"], readonly=is_edit)
    add_row("First Name:", vars["first_name"])
    add_row("Last Name:", vars["last_name"])
    
    tk.Label(form_frame, text="Gender:", bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
    ttk.Combobox(form_frame, textvariable=vars["gender"], values=["1 - Male", "2 - Female"], width=38).grid(row=row_idx, column=1, pady=5, padx=20, sticky="w")
    row_idx += 1

    add_row("Phone No:", vars["phone"])
    add_row("Email:", vars["email"])
    add_row("Card No:", vars["card"])
    
    # --- DATES ---
    tk.Label(form_frame, text="--- Effective Period ---", bg="white", fg="#007bff", font=("Segoe UI", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=(15, 5))
    row_idx += 1
    
    def create_date(label, date_str=None):
        nonlocal row_idx
        tk.Label(form_frame, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
        d_ent = DateEntry(form_frame, width=37, background='#007bff', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        # If Editing, try to parse existing date
        if is_edit and date_str:
            try: d_ent.set_date(datetime.strptime(date_str[:10], "%Y-%m-%d"))
            except: pass
        d_ent.grid(row=row_idx, column=1, pady=5, padx=20, sticky="w")
        row_idx += 1
        return d_ent

    b_ent = create_date("Begin Date:", edit_data.get("beginTime") if is_edit else None)
    e_ent = create_date("End Date:", edit_data.get("endTime") if is_edit else None)
    
    add_row("Remark:", vars["remark"])

    # --- SAVE ACTION ---
    def on_save():
        if not vars["first_name"].get():
            messagebox.showwarning("Required", "First Name is required!")
            return

        fmt_begin = f"{b_ent.get_date().strftime('%Y-%m-%d')}T15:00:00+08:00"
        fmt_end = f"{e_ent.get_date().strftime('%Y-%m-%d')}T15:00:00+08:00"
        
        try: gender_val = int(vars["gender"].get().split(" ")[0])
        except: gender_val = 1 

        payload = {
            "personCode": vars["id"].get(),
            "personFamilyName": vars["last_name"].get(),
            "personGivenName": vars["first_name"].get(),
            "gender": gender_val,
            "orgIndexCode": "1",
            "remark": vars["remark"].get(),
            "phoneNo": vars["phone"].get(),
            "email": vars["email"].get(),
            "cards": [{"cardNo": vars["card"].get()}] if vars["card"].get() else [],
            "beginTime": fmt_begin,
            "endTime": fmt_end
        }

        # --- ROUTING LOGIC (ADD vs EDIT) ---
        if is_edit:
            # Call the new Edit File
            success = person_edit.update_person_api(payload)
            if success:
                messagebox.showinfo("Success", "Person Updated Successfully!")
                if on_success_callback: on_success_callback()
        else:
            # Call Add API directly (Existing Logic)
            if hasattr(common_signature_api, 'call_api'):
                 response = common_signature_api.call_api(ADD_API_PATH, payload)
            elif hasattr(common_signature_api, 'send_to_api'):
                 response = common_signature_api.send_to_api(ADD_API_PATH, payload)
            else:
                 response = None
            
            # Simple Success Check for Add
            if response and "code" in str(response) and "'0'" in str(response):
                 messagebox.showinfo("Success", "Person Added Successfully!")
                 if on_success_callback: on_success_callback()
            else:
                 # Better to parse JSON properly in production, keeping it simple here
                 messagebox.showinfo("Result", f"API Response: {response}")
                 if on_success_callback: on_success_callback()

    tk.Button(form_frame, text=btn_txt, bg=btn_color, fg="black" if is_edit else "white", 
              font=("Segoe UI", 10, "bold"), padx=20, pady=5, command=on_save).grid(row=row_idx, column=1, sticky="e", pady=20)