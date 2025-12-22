import tkinter as tk
from tkinter import ttk, messagebox
import json

try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# --- API ENDPOINT (Logical Organization Add) ---
# Supported by HikCentral V3.0.1
ADD_ORG_API = "/artemis/api/resource/v1/org/single/add"

def call_api(url, payload):
    if not common_signature_api: return None
    try:
        if hasattr(common_signature_api, 'call_api'):
            response = common_signature_api.call_api(url, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            response = common_signature_api.send_to_api(url, payload)
        elif hasattr(common_signature_api, 'post'):
            response = common_signature_api.post(url, payload)
        return response if isinstance(response, dict) else json.loads(response)
    except Exception as e:
        print(f"API Error: {e}")
        return None

def show_org_creation(parent_frame):
    for w in parent_frame.winfo_children(): w.destroy()

    header = tk.Frame(parent_frame, bg="white", pady=10)
    header.pack(fill="x")
    tk.Label(header, text="Create Organization (Logical Group)", font=("Segoe UI", 18, "bold"), bg="white").pack(side="left", padx=20)

    form = tk.Frame(parent_frame, bg="white", padx=30, pady=20)
    form.pack(fill="both", expand=True)

    vars = {
        "name": tk.StringVar(),
        "parent": tk.StringVar(value="root000000"), # Default Root
        "code": tk.StringVar()
    }

    row = 0
    tk.Label(form, text="Org Name:", bg="white").grid(row=row, column=0, pady=10, sticky="w")
    tk.Entry(form, textvariable=vars["name"], width=40).grid(row=row, column=1, pady=10, padx=10)
    row += 1
    
    tk.Label(form, text="Parent Org Code:", bg="white").grid(row=row, column=0, pady=10, sticky="w")
    tk.Entry(form, textvariable=vars["parent"], width=40).grid(row=row, column=1, pady=10, padx=10)
    row += 1
    
    tk.Label(form, text="Custom Org Code (Optional):", bg="white").grid(row=row, column=0, pady=10, sticky="w")
    tk.Entry(form, textvariable=vars["code"], width=40).grid(row=row, column=1, pady=10, padx=10)
    row += 1

    def on_save():
        if not vars["name"].get():
            messagebox.showwarning("Error", "Name is required.")
            return

        payload = {
            "orgName": vars["name"].get(),
            "parentOrgIndexCode": vars["parent"].get()
        }
        if vars["code"].get():
            payload["orgIndexCode"] = vars["code"].get()

        res = call_api(ADD_ORG_API, payload)
        if res and res.get("code") == "0":
            messagebox.showinfo("Success", "Organization Created!")
        else:
            messagebox.showerror("Error", f"Failed: {res.get('msg') if res else 'Unknown'}")

    tk.Button(form, text="Create Org", bg="#28a745", fg="white", command=on_save).grid(row=row, column=1, sticky="e", pady=20)