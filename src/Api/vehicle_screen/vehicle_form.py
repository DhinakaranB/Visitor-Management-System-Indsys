import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from tkcalendar import DateEntry 

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# --- API ENDPOINTS ---
ADD_VEHICLE_API = "/artemis/api/resource/v1/vehicle/single/add"
UPDATE_VEHICLE_API = "/artemis/api/resource/v1/vehicle/single/update"

# Query endpoints
QUERY_PERSON_SINGLE = "/artemis/api/resource/v1/person/single/query"
QUERY_PERSON_LIST = "/artemis/api/resource/v1/person/personList"

# --- COLOR MAPPING ---
COLOR_MAP = {
    "0": "Other", "1": "White", "2": "Silver", "3": "Gray", "4": "Black",
    "5": "Red", "6": "Blue", "7": "Yellow", "8": "Green", "9": "Brown"
}
COLOR_OPTIONS = [f"{k} - {v}" for k, v in COLOR_MAP.items()]

def call_api(url, payload):
    if not common_signature_api: return None
    try:
        if hasattr(common_signature_api, 'call_api'):
            response = common_signature_api.call_api(url, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            response = common_signature_api.send_to_api(url, payload)
        elif hasattr(common_signature_api, 'post'):
            response = common_signature_api.post(url, payload)
        else:
            return None
        
        if isinstance(response, dict): return response
        if isinstance(response, str): return json.loads(response)
        if hasattr(response, 'json'): return response.json()
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

def fetch_person_details(person_code, vars_dict):
    """
    Robust Person Fetcher: Tries Single Query first, then List Search.
    """
    if not person_code:
        messagebox.showwarning("Warning", "Please enter a Person Code to search.")
        return

    print(f"🔍 Searching for Person Code: {person_code}")
    
    # METHOD 1: Try Single Query
    payload_1 = {"personCode": person_code}
    data = call_api(QUERY_PERSON_SINGLE, payload_1)
    
    found_data = None
    
    if data and data.get("code") == "0":
        found_data = data.get("data")
    else:
        # METHOD 2: Try List Search
        print("⚠️ Single query failed, trying List Search...")
        payload_2 = {
            "pageNo": 1, 
            "pageSize": 20, 
            "personName": person_code 
        }
        data2 = call_api(QUERY_PERSON_LIST, payload_2)
        if data2 and data2.get("code") == "0":
            rows = data2.get("data", {}).get("list", [])
            for p in rows:
                if p.get("personCode") == person_code:
                    found_data = p
                    break

    # --- PROCESS RESULT ---
    if found_data:
        pid = found_data.get("personId", "")
        fname = found_data.get("personGivenName", "") or found_data.get("personName", "")
        lname = found_data.get("personFamilyName", "")
        phone = found_data.get("phoneNo", "")
        
        vars_dict["person_id"].set(pid)
        vars_dict["first_name"].set(fname)
        vars_dict["last_name"].set(lname)
        vars_dict["phone"].set(phone)
        
        messagebox.showinfo("Found", f"Person Found:\nName: {fname} {lname}\nID: {pid}")
    else:
        messagebox.showerror("Not Found", f"Could not find person with code: {person_code}")

def show_vehicle_form(parent_frame, on_success_callback=None, edit_data=None):
    for widget in parent_frame.winfo_children(): widget.destroy()

    is_edit = edit_data is not None
    title = f"Edit Vehicle ({edit_data.get('plateNo')})" if is_edit else "Add Vehicle"
    btn_txt = "Update Vehicle" if is_edit else "Save to API"
    btn_color = "#ffc107" if is_edit else "#28a745"

    header = tk.Frame(parent_frame, bg="white", pady=10)
    header.pack(fill="x")
    tk.Button(header, text="← Back", bg="white", bd=0, command=on_success_callback).pack(side="left", padx=10)
    tk.Label(header, text=title, font=("Segoe UI", 18, "bold"), bg="white").pack(side="left", padx=10)

    form = tk.Frame(parent_frame, bg="white", padx=30, pady=20)
    form.pack(fill="both", expand=True)

    # --- VARIABLES ---
    vars = {
        "plate": tk.StringVar(value=edit_data.get("plateNo", "") if is_edit else ""),
        "category": tk.StringVar(value=edit_data.get("plateCategory", "123") if is_edit else "123"),
        "area": tk.StringVar(value=edit_data.get("plateArea", "TN") if is_edit else "TN"),
        "color": tk.StringVar(value="3 - Gray"), 
        
        # NEW: Vehicle Group Index (Required by your API)
        "group_index": tk.StringVar(value=edit_data.get("vehicleGroupIndexCode", "1") if is_edit else "1"),

        "search_code": tk.StringVar(), 
        "person_id": tk.StringVar(value=edit_data.get("personId", "") if is_edit else ""),
        "first_name": tk.StringVar(value=edit_data.get("personGivenName", "") if is_edit else ""),
        "last_name": tk.StringVar(value=edit_data.get("personFamilyName", "") if is_edit else ""),
        "phone": tk.StringVar(value=edit_data.get("phoneNo", "") if is_edit else "")
    }

    if is_edit:
        c_code = str(edit_data.get("vehicleColor", "0"))
        c_name = COLOR_MAP.get(c_code, "Other")
        vars["color"].set(f"{c_code} - {c_name}")

    row_idx = 0
    def add_row(label, var, width=40, readonly=False):
        nonlocal row_idx
        tk.Label(form, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=10)
        ent = tk.Entry(form, textvariable=var, font=("Segoe UI", 10), width=width, bg="#eee" if readonly else "white")
        if readonly: ent.config(state="readonly")
        ent.grid(row=row_idx, column=1, pady=5, padx=20, sticky="w")
        row_idx += 1
        return ent

    tk.Label(form, text="--- Vehicle Info ---", bg="white", fg="#007bff", font=("Segoe UI", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=(10, 5)); row_idx+=1
    
    add_row("Plate No:", vars["plate"], readonly=is_edit)
    add_row("Plate Category:", vars["category"])
    add_row("Plate Area:", vars["area"])
    
    # NEW: Group Index Field
    add_row("Vehicle Group Index:", vars["group_index"])

    tk.Label(form, text="Color:", bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=10)
    ttk.Combobox(form, textvariable=vars["color"], values=COLOR_OPTIONS, width=38, state="readonly").grid(row=row_idx, column=1, pady=5, padx=20, sticky="w")
    row_idx += 1

    tk.Label(form, text="--- Owner Info (Search by Person Code) ---", bg="white", fg="#007bff", font=("Segoe UI", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=(15, 5)); row_idx+=1
    
    tk.Label(form, text="Search Person Code:", bg="white", font=("Segoe UI", 10, "bold")).grid(row=row_idx, column=0, sticky="w", pady=10)
    search_frame = tk.Frame(form, bg="white")
    search_frame.grid(row=row_idx, column=1, sticky="w", padx=20)
    tk.Entry(search_frame, textvariable=vars["search_code"], width=25, bg="#fff").pack(side="left")
    tk.Button(search_frame, text="🔍 Fetch Details", bg="#17a2b8", fg="white", 
              command=lambda: fetch_person_details(vars["search_code"].get(), vars)).pack(side="left", padx=5)
    row_idx += 1

    add_row("Person ID (System):", vars["person_id"], readonly=True)
    add_row("Given Name:", vars["first_name"], readonly=True)
    add_row("Family Name:", vars["last_name"], readonly=True)
    add_row("Phone No:", vars["phone"], readonly=False)

    tk.Label(form, text="--- Validity Period ---", bg="white", fg="#007bff", font=("Segoe UI", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=(15, 5)); row_idx+=1
    
    def create_date(label, date_str=None):
        nonlocal row_idx
        tk.Label(form, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=10)
        d_ent = DateEntry(form, width=37, background='#007bff', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        if is_edit and date_str:
            try: d_ent.set_date(datetime.strptime(date_str[:10], "%Y-%m-%d"))
            except: pass
        d_ent.grid(row=row_idx, column=1, pady=5, padx=20, sticky="w")
        row_idx += 1
        return d_ent

    eff_date = create_date("Effective Date:", edit_data.get("effectiveDate") if is_edit else None)
    exp_date = create_date("Expired Date:", edit_data.get("expiredDate") if is_edit else None)

    if not is_edit:
        try: exp_date.set_date(datetime.now().replace(year=datetime.now().year + 10))
        except: pass

    def on_save():
        if not vars["plate"].get():
            messagebox.showwarning("Required", "Plate Number is required!")
            return
        if not vars["person_id"].get():
            messagebox.showwarning("Required", "Please search and select a Person first.")
            return

        color_val = int(vars["color"].get().split(" ")[0])
        fmt_eff = f"{eff_date.get_date().strftime('%Y-%m-%d')}T15:00:00+08:00"
        fmt_exp = f"{exp_date.get_date().strftime('%Y-%m-%d')}T15:00:00+08:00"

        # Construct Payload with New Group Code
        payload = {
            "plateNo": vars["plate"].get(),
            "plateCategory": vars["category"].get(),
            "plateArea": vars["area"].get(),
            "vehicleColor": color_val,
            
            # --- FIXED: Use the variable from input ---
            "vehicleGroupIndexCode": vars["group_index"].get(), 
            
            "personId": vars["person_id"].get(),
            "personGivenName": vars["first_name"].get(),
            "personFamilyName": vars["last_name"].get(),
            "phoneNo": vars["phone"].get(),
            "effectiveDate": fmt_eff,
            "expiredDate": fmt_exp
        }

        if is_edit:
            payload["vehicleId"] = edit_data.get("vehicleId")
            res = call_api(UPDATE_VEHICLE_API, payload)
        else:
            res = call_api(ADD_VEHICLE_API, payload)

        if res and res.get("code") == "0":
            msg = "Vehicle Updated!" if is_edit else "Vehicle Added Successfully!"
            messagebox.showinfo("Success", msg)
            if on_success_callback: on_success_callback()
        else:
            err = res.get("msg") if res else "Unknown Error"
            messagebox.showerror("API Error", f"Failed: {err}")

    tk.Button(form, text=btn_txt, bg=btn_color, fg="black" if is_edit else "white", 
              font=("Segoe UI", 10, "bold"), padx=20, pady=5, command=on_save).grid(row=row_idx, column=1, sticky="e", pady=20)