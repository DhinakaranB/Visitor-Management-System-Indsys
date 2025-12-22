import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime
import json
import urllib3
import inspect 

# --- IMPORT THE DATEPICKER ---
from tkcalendar import DateEntry 

# --- IMPORT YOUR SIGNATURE API ---
try:
    from src.Api.Common_signature import common_signature_api
    print("✅ Loaded common_signature_api")
except ImportError:
    print("❌ Could not load common_signature_api. Check folder structure.")
    common_signature_api = None

# HTTPS Warnings disable
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- API CONFIGURATION ---
API_PATH = "/artemis/api/resource/v1/person/single/add"

def generate_unique_id():
    """Generates a unique numeric ID."""
    timestamp = datetime.now().strftime("%Y%m%d")
    rand_num = random.randint(1000, 9999)
    return f"{timestamp}{rand_num}"

def show_create_form(parent_frame, on_success_callback=None):
    # 1. Clear previous widgets
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Header
    header_frame = tk.Frame(parent_frame, bg="white", pady=10)
    header_frame.pack(fill="x")
    tk.Button(header_frame, text="← Back", bg="white", bd=0, font=("Segoe UI", 10), 
              command=on_success_callback).pack(side="left", padx=10)
    tk.Label(header_frame, text="Add Person (Secure API)", font=("Segoe UI", 18, "bold"), bg="white").pack(side="left", padx=10)

    # 3. Form Container
    form_frame = tk.Frame(parent_frame, bg="white", padx=30, pady=20)
    form_frame.pack(fill="both", expand=True)

    # --- INPUT VARIABLES ---
    vars = {
        "id": tk.StringVar(value=generate_unique_id()),
        "first_name": tk.StringVar(),
        "last_name": tk.StringVar(),
        "phone": tk.StringVar(),
        "email": tk.StringVar(),
        "card": tk.StringVar(),
        "gender": tk.StringVar(value="1 - Male"), 
        "remark": tk.StringVar()
    }

    # --- HELPER: Create Text Rows ---
    row_idx = 0
    def add_row(label, var):
        nonlocal row_idx
        tk.Label(form_frame, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
        entry = tk.Entry(form_frame, textvariable=var, font=("Segoe UI", 10), width=40, bg="white")
        entry.grid(row=row_idx, column=1, pady=(5, 10), padx=20, sticky="w")
        row_idx += 1

    # --- RENDER FIELDS ---
    add_row("Person Code (ID):", vars["id"])
    add_row("First Name:", vars["first_name"])
    add_row("Last Name:", vars["last_name"])
    
    # Gender
    tk.Label(form_frame, text="Gender:", bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
    gender_cb = ttk.Combobox(form_frame, textvariable=vars["gender"], values=["1 - Male", "2 - Female"], width=38)
    gender_cb.grid(row=row_idx, column=1, pady=(5, 10), padx=20, sticky="w")
    row_idx += 1

    add_row("Phone No:", vars["phone"])
    add_row("Email:", vars["email"])
    add_row("Card No:", vars["card"])
    
    # --- DATE PICKERS ---
    tk.Label(form_frame, text="--- Effective Period ---", bg="white", fg="#007bff", font=("Segoe UI", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=(15, 5))
    row_idx += 1
    
    # Begin Date
    tk.Label(form_frame, text="Begin Date:", bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
    begin_date_ent = DateEntry(form_frame, width=37, background='#007bff', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    begin_date_ent.grid(row=row_idx, column=1, pady=(5, 10), padx=20, sticky="w")
    row_idx += 1

    # End Date
    tk.Label(form_frame, text="End Date:", bg="white", font=("Segoe UI", 10, "bold"), fg="#555").grid(row=row_idx, column=0, sticky="w", pady=(10, 0))
    end_date_ent = DateEntry(form_frame, width=37, background='#007bff', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
    try:
        current_year = int(datetime.now().year)
        end_date_ent.set_date(datetime.now().replace(year=current_year + 10))
    except:
        pass
    end_date_ent.grid(row=row_idx, column=1, pady=(5, 10), padx=20, sticky="w")
    row_idx += 1
    
    add_row("Remark:", vars["remark"])

    # --- API SAVE FUNCTION (FIXED: Using 'call_api') ---
    # def save_to_api(payload):
    #     if not common_signature_api:
    #         messagebox.showerror("Error", "Signature Module not found!\nCannot connect to Artemis.")
    #         return

    #     try:
    #         print(f"📡 Sending Secure Request to: {API_PATH}")
    #         response = None
    #         json_body = json.dumps(payload)

    #         # --- USING THE FUNCTION NAME FROM YOUR SCREENSHOT ---
    #         if hasattr(common_signature_api, 'call_api'):
    #              print("👉 Using 'call_api' function")
    #              # call_api likely takes (api_url, json_body, method="POST")
    #              # If it fails, try adding method="POST"
    #              response = common_signature_api.call_api(API_PATH, json_body)
            
    #         elif hasattr(common_signature_api, 'send_to_api'):
    #              print("👉 Using 'send_to_api' function")
    #              response = common_signature_api.send_to_api(API_PATH, json_body)

    #         else:
    #              messagebox.showerror("Code Error", "Neither 'call_api' nor 'send_to_api' worked. Check parameter arguments.")
    #              return

    #         # 3. HANDLE RESPONSE
    #         print(f"📄 Raw Response: {response}")

    #         if isinstance(response, str):
    #             data = json.loads(response)
    #         else:
    #             try:
    #                 data = response.json()
    #             except:
    #                 data = response 

    #         if data.get("code") == "0":
    #             messagebox.showinfo("Success", f"Person Added Successfully!\nMsg: {data.get('msg')}")
    #             if on_success_callback:
    #                 on_success_callback()
    #         else:
    #             messagebox.showerror("API Error", f"Failed to add person.\nError: {data.get('msg')}\nCode: {data.get('code')}")

    #     except Exception as e:
    #         print("❌ API Exception:", e)
    #         messagebox.showerror("Connection Error", f"Could not connect to API.\n{e}")

    # --- API SAVE FUNCTION (FIXED) ---
    def save_to_api(payload):
        if not common_signature_api:
            messagebox.showerror("Error", "Signature Module not found!\nCannot connect to Artemis.")
            return

        try:
            print(f"📡 Sending Secure Request to: {API_PATH}")
            response = None
            
            # --- CRITICAL FIX ---
            # Do NOT use json.dumps(payload). 
            # Send 'payload' (the dictionary) directly.
            # Your common_signature_api handles the conversion internally.
            
            if hasattr(common_signature_api, 'call_api'):
                 print("👉 Using 'call_api' with Dictionary")
                 response = common_signature_api.call_api(API_PATH, payload)
            
            elif hasattr(common_signature_api, 'send_to_api'):
                 print("👉 Using 'send_to_api' with Dictionary")
                 response = common_signature_api.send_to_api(API_PATH, payload)
            
            elif hasattr(common_signature_api, 'post'):
                 # Some versions of 'post' might strictly require a string.
                 # If the above fails, uncomment the line below:
                 # payload = json.dumps(payload) 
                 response = common_signature_api.post(API_PATH, payload)

            else:
                 messagebox.showerror("Code Error", "Could not find API function (call_api/send_to_api).")
                 return

            # --- HANDLE RESPONSE ---
            print(f"📄 Raw Response: {response}")

            # If response is a string, convert to JSON
            if isinstance(response, str):
                try:
                    data = json.loads(response)
                except:
                    messagebox.showerror("API Error", f"Invalid Response:\n{response}")
                    return
            else:
                # If it's a Requests object
                try:
                    data = response.json()
                except:
                    data = response 

            # Check Artemis Result Code
            if data.get("code") == "0":
                messagebox.showinfo("Success", f"Person Added Successfully!\nID: {payload['personCode']}")
                if on_success_callback:
                    on_success_callback()
            else:
                messagebox.showerror("API Error", f"Failed to add person.\nError: {data.get('msg')}\nCode: {data.get('code')}")

        except Exception as e:
            print("❌ API Exception:", e)
            messagebox.showerror("Connection Error", f"Could not connect to API.\n{e}")

    # --- SAVE ACTION ---
    def on_save():
        # 1. Validation
        if not vars["first_name"].get():
            messagebox.showwarning("Required", "First Name is required!")
            return

        # 2. Get Dates
        b_date = begin_date_ent.get_date()
        e_date = end_date_ent.get_date()
        
        fmt_begin = f"{b_date.strftime('%Y-%m-%d')}T15:00:00+08:00" 
        fmt_end   = f"{e_date.strftime('%Y-%m-%d')}T15:00:00+08:00"

        # 3. Construct Payload
        try:
            gender_val = int(vars["gender"].get().split(" ")[0])
        except:
            gender_val = 1 

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

        # 4. Call API
        save_to_api(payload)

    # Save Button
    tk.Button(form_frame, text="Save to API", bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"), 
              padx=20, pady=5, command=on_save).grid(row=row_idx, column=1, sticky="e", pady=20)