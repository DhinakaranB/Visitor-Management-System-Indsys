import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

from src.Api.vehicle_screen import vehicle_form

LIST_API = "/artemis/api/resource/v1/vehicle/vehicleList"
DELETE_API = "/artemis/api/resource/v1/vehicle/single/delete"

# Store data for editing
current_vehicle_data = []

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

def fetch_list(tree):
    global current_vehicle_data
    if not common_signature_api: return

    # Standard pagination
    payload = {"pageNo": 1, "pageSize": 50}
    print("📡 Fetching Vehicles...")
    
    data = call_api(LIST_API, payload)
    
    if data and data.get("code") == "0":
        rows = data.get("data", {}).get("list", [])
        current_vehicle_data = rows
        
        # UI Update
        tree.after(0, update_tree, tree, rows)
    else:
        print(f"Fetch Failed: {data}")

def update_tree(tree, rows):
    for item in tree.get_children(): tree.delete(item)
    
    for v in rows:
        plate = v.get("plateNo", "-")
        # Map Type ID to Name (Optional)
        vtype = str(v.get("vehicleType", "-"))
        color = v.get("vehicleColor", "-")
        
        tree.insert("", "end", values=(plate, vtype, color))

def on_edit(tree, parent):
    sel = tree.selection()
    if not sel: 
        messagebox.showwarning("Select", "Please select a vehicle.")
        return
    
    plate_in_row = tree.item(sel[0])['values'][0]
    
    # Find full object
    obj = next((x for x in current_vehicle_data if x["plateNo"] == str(plate_in_row)), None)
    
    if obj:
        vehicle_form.show_vehicle_form(parent, lambda: show_list(parent), edit_data=obj)
    else:
        messagebox.showerror("Error", "Details not found.")

def on_delete(tree):
    sel = tree.selection()
    if not sel: 
        messagebox.showwarning("Select", "Please select a vehicle.")
        return
        
    plate_in_row = tree.item(sel[0])['values'][0]
    
    if messagebox.askyesno("Confirm", f"Delete vehicle {plate_in_row}?"):
        payload = {"plateNo": str(plate_in_row)}
        
        res = call_api(DELETE_API, payload)
        if res and res.get("code") == "0":
            messagebox.showinfo("Deleted", "Vehicle Deleted.")
            fetch_list(tree)
        else:
            msg = res.get("msg") if res else "Unknown"
            messagebox.showerror("Error", f"Delete Failed: {msg}")

def show_list(parent_frame):
    for w in parent_frame.winfo_children(): w.destroy()

    # Header
    header = tk.Frame(parent_frame, bg="#D6EAF8", pady=10)
    header.pack(fill="x", padx=20)
    tk.Label(header, text="Vehicle List", font=("Segoe UI", 20, "bold"), bg="#D6EAF8").pack(side="left")

    btns = tk.Frame(header, bg="#D6EAF8")
    btns.pack(side="right")

    tk.Button(btns, text="Refresh", bg="#17a2b8", fg="white", command=lambda: fetch_list(tree)).pack(side="left", padx=2)
    tk.Button(btns, text="Add New", bg="#28a745", fg="white", command=lambda: vehicle_form.show_vehicle_form(parent_frame, lambda: show_list(parent_frame))).pack(side="left", padx=2)
    tk.Button(btns, text="Edit", bg="#ffc107", command=lambda: on_edit(tree, parent_frame)).pack(side="left", padx=2)
    tk.Button(btns, text="Delete", bg="#dc3545", fg="white", command=lambda: on_delete(tree)).pack(side="left", padx=2)

    # Treeview
    cols = ("Plate", "Type", "Color")
    tree = ttk.Treeview(parent_frame, columns=cols, show="headings", height=15)
    
    tree.heading("Plate", text="Plate No")
    tree.heading("Type", text="Vehicle Type")
    tree.heading("Color", text="Color")
    
    tree.column("Plate", width=150)
    tree.column("Type", width=100)
    tree.column("Color", width=100)
    
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # Load Data
    threading.Thread(target=fetch_list, args=(tree,), daemon=True).start()