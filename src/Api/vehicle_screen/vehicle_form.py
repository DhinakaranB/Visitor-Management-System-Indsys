import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import json

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# API Endpoints
API_ADD_VEHICLE    = "/artemis/api/resource/v1/vehicle/single/add"
API_UPDATE_VEHICLE = "/artemis/api/resource/v1/vehicle/single/update" # ✅ New Endpoint
API_PERSON_LIST    = "/artemis/api/resource/v1/person/personList"
API_GROUP_LIST     = "/artemis/api/resource/v1/vehicleGroup/vehicleGroupList"

# Colors
BG_COLOR = "white"
SECTION_COLOR = "#3498DB" 

# Color Map for Pre-selection
COLOR_MAP = {
    0: "0 - Other", 1: "1 - White", 2: "2 - Silver", 3: "3 - Gray", 4: "4 - Black",
    5: "5 - Red", 6: "6 - Blue", 7: "7 - Yellow", 8: "8 - Green", 9: "9 - Brown"
}

def show_vehicle_form(content_frame, on_success_callback=None, edit_data=None):
    """
    Renders the Vehicle Form. If 'edit_data' is provided, it enters Edit Mode.
    """
    # 1. Clear previous content
    for widget in content_frame.winfo_children(): widget.destroy()
    content_frame.config(bg=BG_COLOR)

    is_edit = edit_data is not None
    title_text = f"Edit Vehicle ({edit_data.get('plateNo')})" if is_edit else "Add Vehicle"
    btn_text = "Update Vehicle" if is_edit else "Save Vehicle"
    btn_color = "#ffc107" if is_edit else "#28a745"

    # --- Header ---
    header = tk.Frame(content_frame, bg=BG_COLOR, pady=10)
    header.pack(fill="x", padx=20)
    
    if on_success_callback:
        tk.Button(header, text="← Back", bg="white", bd=0, font=("Segoe UI", 10), 
                  command=on_success_callback).pack(side="left")
    
    tk.Label(header, text=title_text, font=("Segoe UI", 18, "bold"), bg=BG_COLOR).pack(side="left", padx=10)

    # --- Main Form ---
    form_frame = tk.Frame(content_frame, bg=BG_COLOR, padx=40, pady=10)
    form_frame.pack(fill="both", expand=True)

    # --- VARIABLES & PRE-FILL ---
    var_plate = tk.StringVar(value=edit_data.get("plateNo", "") if is_edit else "")
    var_group_display = tk.StringVar() 
    
    # Color Pre-fill
    pre_color_code = int(edit_data.get("vehicleColor", 3)) if is_edit else 3
    var_color = tk.StringVar(value=COLOR_MAP.get(pre_color_code, "3 - Gray"))
    
    # Owner Pre-fill
    # Note: Edit data might have 'personName' instead of 'personGivenName'
    p_name = edit_data.get("personName", "") if is_edit else ""
    p_given = edit_data.get("personGivenName", p_name) if is_edit else ""
    
    var_search_code = tk.StringVar()
    var_person_id = tk.StringVar(value=edit_data.get("personId", "") if is_edit else "")
    var_given_name = tk.StringVar(value=p_given)
    var_family_name = tk.StringVar(value=edit_data.get("personFamilyName", "") if is_edit else "")
    var_phone = tk.StringVar(value=edit_data.get("phoneNo", "") if is_edit else "")

    # ================= UI HELPER =================
    row_idx = 0
    def add_section(title):
        nonlocal row_idx
        tk.Label(form_frame, text=title, font=("Segoe UI", 10, "bold"), fg=SECTION_COLOR, bg=BG_COLOR).grid(row=row_idx, column=0, sticky="w", pady=(20, 10))
        row_idx += 1

    def add_field(label, var, width=40, readonly=False):
        nonlocal row_idx
        tk.Label(form_frame, text=label, font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
        entry = ttk.Entry(form_frame, textvariable=var, width=width)
        if readonly: entry.config(state="readonly")
        entry.grid(row=row_idx, column=1, sticky="w", padx=20, pady=5)
        row_idx += 1
        return entry

    # ================= SECTION 1: VEHICLE INFO =================
    add_section("--- Vehicle Info ---")
    
    # Plate No is usually the Primary Key, so it's Read-Only in Edit Mode
    add_field("Plate No:", var_plate, readonly=is_edit)
    
    # Group Dropdown
    tk.Label(form_frame, text="Vehicle Group:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
    combo_group = ttk.Combobox(form_frame, textvariable=var_group_display, width=38, state="readonly")
    combo_group.grid(row=row_idx, column=1, sticky="w", padx=20)
    row_idx += 1

    # Fetch Groups & Select Current
    def fetch_groups():
        if not common_signature_api: return
        try:
            res = common_signature_api.call_api(API_GROUP_LIST, {"pageNo": 1, "pageSize": 100})
            if res and str(res.get("code")) == "0":
                rows = res.get("data", {}).get("list", [])
                group_options = [f"{g['vehicleGroupIndexCode']} - {g['vehicleGroupName']}" for g in rows]
                combo_group['values'] = group_options
                
                # If Editing, Select the correct group
                if is_edit:
                    target_id = str(edit_data.get("vehicleGroupIndexCode", ""))
                    for opt in group_options:
                        if opt.startswith(target_id + " -"):
                            combo_group.set(opt)
                            break
                elif group_options:
                    combo_group.current(0)
        except Exception as e:
            print(f"Group fetch error: {e}")

    fetch_groups()

    # Color Dropdown
    tk.Label(form_frame, text="Color:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
    colors = list(COLOR_MAP.values())
    ttk.Combobox(form_frame, textvariable=var_color, values=colors, width=38, state="readonly").grid(row=row_idx, column=1, sticky="w", padx=20)
    row_idx += 1

    # ================= SECTION 2: OWNER INFO =================
    add_section("--- Owner Info ---")

    # Search (Disabled in Edit Mode to prevent accidental owner change, or keep enabled if allowed)
    tk.Label(form_frame, text="Search Person Code:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR).grid(row=row_idx, column=0, sticky="w", pady=5)
    search_container = tk.Frame(form_frame, bg=BG_COLOR)
    search_container.grid(row=row_idx, column=1, sticky="w", padx=20)
    
    ent_search = ttk.Entry(search_container, textvariable=var_search_code, width=25)
    ent_search.pack(side="left")
    
    def fetch_person():
        code = var_search_code.get().strip()
        if not code: return
        if common_signature_api:
            # Client-side filter for person code
            res = common_signature_api.call_api(API_PERSON_LIST, {"pageNo": 1, "pageSize": 100})
            if res and str(res.get("code")) == "0":
                data = res.get("data", {}).get("list", [])
                found = next((p for p in data if str(p.get("personCode")) == code), None)
                if found:
                    var_person_id.set(found.get("personId", ""))
                    var_given_name.set(found.get("personName", ""))
                    var_phone.set(found.get("phoneNo", ""))
                    messagebox.showinfo("Found", f"Person: {found.get('personName')}")
                else:
                    messagebox.showerror("Not Found", "Person Code not found.")

    btn_search = tk.Button(search_container, text="🔍 Fetch", bg="#17a2b8", fg="white", bd=0, command=fetch_person)
    btn_search.pack(side="left", padx=5)

    add_field("System ID:", var_person_id, readonly=True)
    add_field("Name:", var_given_name, readonly=True)
    add_field("Phone:", var_phone, readonly=True)

    # ================= SECTION 3: VALIDITY =================
    add_section("--- Validity Period ---")
    
    def add_date(label, default_val=None):
        nonlocal row_idx
        tk.Label(form_frame, text=label, font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
        de = DateEntry(form_frame, width=37, background='#3498DB', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        
        # Set Date logic
        if default_val:
            try:
                # Handle ISO format "2025-12-29T00:00:00+05:30"
                dt_obj = datetime.fromisoformat(default_val.replace("Z", "+00:00"))
                de.set_date(dt_obj)
            except:
                de.set_date(datetime.now()) # Fallback
        
        de.grid(row=row_idx, column=1, sticky="w", padx=20)
        row_idx += 1
        return de

    # Pre-fill dates if editing, else default
    eff_val = edit_data.get("effectiveDate") if is_edit else None
    exp_val = edit_data.get("expiredDate") if is_edit else None
    
    eff_date = add_date("Effective Date:", eff_val)
    exp_date = add_date("Expired Date:", exp_val)

    # ================= SAVE LOGIC =================
    def save_vehicle():
        plate = var_plate.get().strip()
        pid = var_person_id.get().strip()
        
        # Extract Group ID "1 - Staff" -> "1"
        group_val = var_group_display.get()
        group_index = group_val.split(" - ")[0] if " - " in group_val else group_val

        if not plate:
            messagebox.showwarning("Validation", "Plate Number is required.")
            return
        if not pid:
            messagebox.showwarning("Validation", "Owner (Person ID) is required.")
            return
        if not group_index:
            messagebox.showwarning("Validation", "Vehicle Group is required.")
            return

        try: color_index = int(var_color.get().split(" ")[0])
        except: color_index = 0

        # Construct Payload
        payload = {
            "plateNo": plate,
            "plateCategory": "123",
            "plateArea": "TN",
            "personId": pid,
            "vehicleColor": color_index,
            "vehicleType": 1,
            "vehicleGroupIndexCode": group_index,
            "personGivenName": var_given_name.get(),
            "personFamilyName": var_family_name.get(),
            "phoneNo": var_phone.get(),
            "effectiveDate": f"{eff_date.get_date()}T00:00:00+05:30",
            "expiredDate": f"{exp_date.get_date()}T23:59:59+05:30"
        }

        # Choose API (Add vs Update)
        target_api = API_UPDATE_VEHICLE if is_edit else API_ADD_VEHICLE
        
        # NOTE: For Update, some APIs strictly require "vehicleId" or "plateNo" in specific places.
        # Assuming payload handles identification via 'plateNo'.

        print(f"Sending to {target_api}: {json.dumps(payload, indent=2)}")

        if common_signature_api:
            res = common_signature_api.call_api(target_api, payload)
            
            if res and str(res.get("code")) == "0":
                msg = "Vehicle Updated!" if is_edit else "Vehicle Added!"
                messagebox.showinfo("Success", msg)
                if on_success_callback: on_success_callback()
            else:
                msg = res.get("msg", "Unknown Error") if res else "No Response"
                messagebox.showerror("Error", f"Failed: {msg}")

    tk.Button(form_frame, text=btn_text, bg=btn_color, fg="white" if not is_edit else "black", 
              font=("Segoe UI", 11, "bold"), padx=30, pady=5, 
              command=save_vehicle).grid(row=row_idx, column=1, sticky="e", pady=30)