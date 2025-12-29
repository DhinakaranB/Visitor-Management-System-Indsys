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
API_ADD_VEHICLE = "/artemis/api/resource/v1/vehicle/single/add"
API_PERSON_LIST = "/artemis/api/resource/v1/person/personList"

# Common Colors
BG_COLOR = "white"
SECTION_COLOR = "#3498DB" # Blue for section headers

def show_vehicle_form(content_frame, on_success_callback=None):
    # 1. Clear previous content
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    content_frame.config(bg=BG_COLOR)

    # --- Header ---
    header = tk.Frame(content_frame, bg=BG_COLOR, pady=10)
    header.pack(fill="x", padx=20)
    
    if on_success_callback:
        tk.Button(header, text="← Back", bg="white", bd=0, font=("Segoe UI", 10), 
                  command=on_success_callback).pack(side="left")
    
    tk.Label(header, text="Add Vehicle", font=("Segoe UI", 18, "bold"), bg=BG_COLOR).pack(side="left", padx=10)

    # --- Scrollable Main Area (Optional, but good for long forms) ---
    # For simplicity, using a direct frame here
    form_frame = tk.Frame(content_frame, bg=BG_COLOR, padx=40, pady=10)
    form_frame.pack(fill="both", expand=True)

    # Variables
    var_plate = tk.StringVar()
    var_category = tk.StringVar(value="123") # Default from image
    var_area = tk.StringVar(value="TN")      # Default from image
    var_group = tk.StringVar(value="1")
    var_color = tk.StringVar(value="3 - Gray")
    
    # Owner Variables
    var_search_code = tk.StringVar()
    var_person_id = tk.StringVar()   # Hidden System ID
    var_given_name = tk.StringVar()
    var_family_name = tk.StringVar()
    var_phone = tk.StringVar()

    # Dates
    today = datetime.now()
    future = today + timedelta(days=365*10) # 10 years default

    # ================= UI HELPER =================
    row_idx = 0
    def add_section(title):
        nonlocal row_idx
        lbl = tk.Label(form_frame, text=title, font=("Segoe UI", 10, "bold"), fg=SECTION_COLOR, bg=BG_COLOR)
        lbl.grid(row=row_idx, column=0, sticky="w", pady=(20, 10))
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
    add_field("Plate No:", var_plate)
    add_field("Plate Category:", var_category)
    add_field("Plate Area:", var_area)
    add_field("Vehicle Group Index:", var_group)

    # Color Dropdown
    tk.Label(form_frame, text="Color:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
    colors = ["0 - Other", "1 - White", "2 - Silver", "3 - Gray", "4 - Black", "5 - Red", "6 - Blue", "7 - Yellow", "8 - Green", "9 - Brown"]
    ttk.Combobox(form_frame, textvariable=var_color, values=colors, width=38, state="readonly").grid(row=row_idx, column=1, sticky="w", padx=20)
    row_idx += 1

    # ================= SECTION 2: OWNER INFO =================
    add_section("--- Owner Info (Search by Person Code) ---")

    # Search Row
    tk.Label(form_frame, text="Search Person Code:", font=("Segoe UI", 10, "bold"), bg=BG_COLOR).grid(row=row_idx, column=0, sticky="w", pady=5)
    
    search_container = tk.Frame(form_frame, bg=BG_COLOR)
    search_container.grid(row=row_idx, column=1, sticky="w", padx=20)
    
    ttk.Entry(search_container, textvariable=var_search_code, width=25).pack(side="left")
    
    # FETCH LOGIC
    def fetch_person():
        code = var_search_code.get().strip()
        if not code:
            messagebox.showwarning("Validation", "Please enter a Person Code")
            return
        
        # Call API to find person
        payload = {"pageNo": 1, "pageSize": 100} # Get list to filter
        
        if common_signature_api:
            res = common_signature_api.call_api(API_PERSON_LIST, payload)
            
            if res and str(res.get("code")) == "0":
                data = res.get("data", {}).get("list", [])
                
                # Find exact match
                found = next((p for p in data if str(p.get("personCode")) == code), None)
                
                if found:
                    var_person_id.set(found.get("personId", ""))
                    var_given_name.set(found.get("personGivenName", ""))
                    var_family_name.set(found.get("personFamilyName", ""))
                    var_phone.set(found.get("phoneNo", ""))
                    messagebox.showinfo("Found", f"Person found: {found.get('personName')}")
                else:
                    messagebox.showerror("Not Found", "Person Code not found in list.")
            else:
                messagebox.showerror("API Error", "Failed to fetch person list.")

    tk.Button(search_container, text="🔍 Fetch Details", bg="#17a2b8", fg="white", bd=0, 
              command=fetch_person).pack(side="left", padx=5)
    row_idx += 1

    # Read-only fields
    add_field("Person ID (System):", var_person_id, readonly=True)
    add_field("Given Name:", var_given_name, readonly=True)
    add_field("Family Name:", var_family_name, readonly=True)
    add_field("Phone No:", var_phone, readonly=True)

    # ================= SECTION 3: VALIDITY =================
    add_section("--- Validity Period ---")
    
    def add_date(label, default_date):
        nonlocal row_idx
        tk.Label(form_frame, text=label, font=("Segoe UI", 10, "bold"), bg=BG_COLOR, fg="#555").grid(row=row_idx, column=0, sticky="w", pady=5)
        de = DateEntry(form_frame, width=37, background='#3498DB', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        de.set_date(default_date)
        de.grid(row=row_idx, column=1, sticky="w", padx=20)
        row_idx += 1
        return de

    eff_date = add_date("Effective Date:", today)
    exp_date = add_date("Expired Date:", future)

    # ================= SAVE BUTTON =================
    def save_vehicle():
        plate = var_plate.get().strip()
        pid = var_person_id.get().strip()
        
        if not plate:
            messagebox.showwarning("Missing Info", "Plate Number is required.")
            return
        if not pid:
            messagebox.showwarning("Missing Info", "Please fetch an Owner first.")
            return

        # Prepare Payload
        try: color_index = int(var_color.get().split(" ")[0])
        except: color_index = 0

        payload = {
            "plateNo": plate,
            "personId": pid, # Use the fetched System ID
            "vehicleColor": color_index,
            "vehicleType": 1, # Default type
            "effectiveTime": f"{eff_date.get_date()}T00:00:00+05:30",
            "expiredTime": f"{exp_date.get_date()}T23:59:59+05:30"
        }

        # Call API
        if common_signature_api:
            res = common_signature_api.call_api(API_ADD_VEHICLE, payload)
            if res and str(res.get("code")) == "0":
                messagebox.showinfo("Success", "Vehicle Added Successfully!")
                if on_success_callback: on_success_callback()
            else:
                msg = res.get("msg", "Unknown Error") if res else "No Response"
                messagebox.showerror("Error", f"Failed: {msg}")

    tk.Button(form_frame, text="Save Vehicle", bg="#28a745", fg="white", font=("Segoe UI", 11, "bold"), 
              padx=30, pady=5, command=save_vehicle).grid(row=row_idx, column=1, sticky="e", pady=30)