import tkinter as tk
from tkinter import ttk, messagebox
import json

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# API Endpoints (Matched to your Postman)
API_ADD_GROUP = "/artemis/api/resource/v1/vehicleGroup/single/add"
API_UPDATE_GROUP = "/artemis/api/resource/v1/vehicleGroup/single/update"

# Colors
BG_COLOR = "white"
SECTION_COLOR = "#3498DB"

def show_group_form(content_frame, on_success_callback=None, edit_data=None):
    """
    Renders the Add/Edit Vehicle Group Screen.
    """
    # 1. Clear previous content
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    content_frame.config(bg=BG_COLOR)

    is_edit = edit_data is not None
    title_text = f"Edit Vehicle Group" if is_edit else "Add Vehicle Group"
    btn_text = "Update Group" if is_edit else "Save Group"
    btn_color = "#ffc107" if is_edit else "#28a745"

    # --- Header ---
    header = tk.Frame(content_frame, bg=BG_COLOR, pady=10)
    header.pack(fill="x", padx=20)
    
    if on_success_callback:
        tk.Button(header, text="← Back", bg="white", bd=0, font=("Segoe UI", 10), 
                  command=on_success_callback).pack(side="left")
    
    tk.Label(header, text=title_text, font=("Segoe UI", 18, "bold"), bg=BG_COLOR).pack(side="left", padx=10)

    # --- Form Container ---
    form_frame = tk.Frame(content_frame, bg=BG_COLOR, padx=40, pady=20)
    form_frame.pack(fill="both", expand=True)

    # Variables
    # Note: Keys match the response from your Postman screenshot
    var_name = tk.StringVar(value=edit_data.get("vehicleGroupName", "") if is_edit else "")
    var_desc = tk.StringVar(value=edit_data.get("description", "") if is_edit else "")
    var_parent = tk.StringVar(value=edit_data.get("parentIndexCode", "0") if is_edit else "0") 
    var_index_code = tk.StringVar(value=edit_data.get("vehicleGroupIndexCode", "") if is_edit else "")

    # ================= FORM FIELDS =================
    row_idx = 0
    
    # Index Code (Read-Only, only shown if Editing)
    if is_edit:
        tk.Label(form_frame, text="Group Index Code:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
        ttk.Entry(form_frame, textvariable=var_index_code, width=40, state="readonly").grid(row=row_idx, column=1, sticky="w", padx=20)
        row_idx += 1

    # Group Name
    tk.Label(form_frame, text="Vehicle Group Name:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
    ttk.Entry(form_frame, textvariable=var_name, width=40).grid(row=row_idx, column=1, sticky="w", padx=20)
    row_idx += 1

    # Description (From your Postman Image)
    tk.Label(form_frame, text="Description:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
    ttk.Entry(form_frame, textvariable=var_desc, width=40).grid(row=row_idx, column=1, sticky="w", padx=20)
    row_idx += 1

    # Parent Group (Optional, Default '0')
    tk.Label(form_frame, text="Parent Index (Default 0):", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
    ttk.Entry(form_frame, textvariable=var_parent, width=40).grid(row=row_idx, column=1, sticky="w", padx=20)
    row_idx += 1

    # ================= SAVE LOGIC =================
    def on_save():
        name = var_name.get().strip()
        desc = var_desc.get().strip()
        parent = var_parent.get().strip()

        if not name:
            messagebox.showwarning("Required", "Vehicle Group Name is required.")
            return

        # Prepare Payload (Matching your Postman Image)
        payload = {
            "vehicleGroupName": name,
            "description": desc,
            "parentIndexCode": parent
        }

        # Select API Endpoint
        target_api = API_ADD_GROUP
        if is_edit:
            target_api = API_UPDATE_GROUP
            # For update, we usually need the IndexCode
            payload["vehicleGroupIndexCode"] = var_index_code.get()

        print(f"Sending to {target_api}: {payload}")

        if common_signature_api:
            # Call API
            res = common_signature_api.call_api(target_api, payload)
            
            # Handle Response
            if res and str(res.get("code")) == "0":
                msg = "Vehicle Group Updated!" if is_edit else "Vehicle Group Added Successfully!"
                messagebox.showinfo("Success", msg)
                if on_success_callback: on_success_callback()
            else:
                err = res.get("msg", "Unknown Error") if res else "No Response"
                messagebox.showerror("Error", f"Failed: {err}")
        else:
            messagebox.showerror("Configuration Error", "API Handler not found.")

    # Save Button
    tk.Button(form_frame, text=btn_text, bg=btn_color, fg="white" if not is_edit else "black", 
              font=("Segoe UI", 11, "bold"), padx=30, pady=5, 
              command=on_save).grid(row=row_idx, column=1, sticky="e", pady=30)