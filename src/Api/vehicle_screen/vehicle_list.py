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

# --- API ENDPOINTS ---
LIST_API = "/artemis/api/resource/v1/vehicle/vehicleList"
DELETE_API = "/artemis/api/resource/v1/vehicle/single/delete"

# Store data for editing
current_vehicle_data = []

def call_api(url, payload):
    """Helper to call API safely"""
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
    """Fetches vehicle list from API and updates UI"""
    global current_vehicle_data
    if not common_signature_api: return

    # --- UPDATED PAYLOAD FOR YOUR API ---
    # Added 'vehicleGroupIndexCode' because your API requires it.
    payload = {
        "pageNo": 1, 
        "pageSize": 50,
        "vehicleGroupIndexCode": "1"  # Using 1 based on Postman screenshot
    }
    
    print(f"📡 Fetching Vehicles from {LIST_API} with payload: {payload}")
    
    data = call_api(LIST_API, payload)
    
    if data and data.get("code") == "0":
        rows = data.get("data", {}).get("list", [])
        current_vehicle_data = rows
        
        # Update UI safely
        tree.after(0, update_tree, tree, rows)
    else:
        print(f"Fetch Failed: {data}")
        # Show error on screen so you know why it failed
        msg = data.get("msg") if data else "Unknown"
        tree.after(0, lambda: messagebox.showerror("Fetch Failed", f"API Error: {msg}"))

def update_tree(tree, rows):
    """Clears and fills the treeview"""
    for item in tree.get_children(): tree.delete(item)
    
    for v in rows:
        plate = v.get("plateNo", "-")
        # Map Type ID to Name (Optional logic)
        vtype = str(v.get("vehicleType", "-"))
        color = v.get("vehicleColor", "-")
        
        # NEW: Show Group Code
        group = v.get("vehicleGroupIndexCode", "-")
        
        tree.insert("", "end", values=(plate, vtype, color, group))

def on_edit(tree, parent):
    """Finds selected vehicle and opens Edit Form"""
    sel = tree.selection()
    if not sel: 
        messagebox.showwarning("Select", "Please select a vehicle to edit.")
        return
    
    plate_in_row = tree.item(sel[0])['values'][0]
    
    obj = next((x for x in current_vehicle_data if x["plateNo"] == str(plate_in_row)), None)
    
    if obj:
        vehicle_form.show_vehicle_form(parent, lambda: show_list(parent), edit_data=obj)
    else:
        messagebox.showerror("Error", "Could not find vehicle details.")

def on_delete(tree):
    """Deletes selected vehicle"""
    sel = tree.selection()
    if not sel: 
        messagebox.showwarning("Select", "Please select a vehicle to delete.")
        return
        
    plate_in_row = tree.item(sel[0])['values'][0]
    
    if messagebox.askyesno("Confirm", f"Are you sure you want to delete {plate_in_row}?"):
        payload = {"plateNo": str(plate_in_row)}
        
        res = call_api(DELETE_API, payload)
        if res and res.get("code") == "0":
            messagebox.showinfo("Deleted", "Vehicle Deleted Successfully.")
            fetch_list(tree)
        else:
            msg = res.get("msg") if res else "Unknown"
            messagebox.showerror("Error", f"Delete Failed: {msg}")

def show_list(parent_frame):
    """Displays the Vehicle List Screen"""
    for w in parent_frame.winfo_children(): w.destroy()

    # Header
    header = tk.Frame(parent_frame, bg="#D6EAF8", pady=10)
    header.pack(fill="x", padx=20)
    tk.Label(header, text="Vehicle List", font=("Segoe UI", 20, "bold"), bg="#D6EAF8").pack(side="left")

    btns = tk.Frame(header, bg="#D6EAF8")
    btns.pack(side="right")

    # Treeview
    cols = ("Plate", "Type", "Color", "Group")
    tree = ttk.Treeview(parent_frame, columns=cols, show="headings", height=15)
    
    tree.heading("Plate", text="Plate No")
    tree.heading("Type", text="Vehicle Type")
    tree.heading("Color", text="Color")
    tree.heading("Group", text="Group Index")
    
    tree.column("Plate", width=150)
    tree.column("Type", width=100)
    tree.column("Color", width=100)
    tree.column("Group", width=100)
    
    scrolly = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrolly.set)
    scrolly.pack(side="right", fill="y")
    
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # Buttons
    tk.Button(btns, text="Refresh", bg="#17a2b8", fg="white", 
              command=lambda: fetch_list(tree)).pack(side="left", padx=2)
              
    tk.Button(btns, text="Add New", bg="#28a745", fg="white", 
              command=lambda: vehicle_form.show_vehicle_form(parent_frame, lambda: show_list(parent_frame))).pack(side="left", padx=2)
              
    tk.Button(btns, text="Edit", bg="#ffc107", 
              command=lambda: on_edit(tree, parent_frame)).pack(side="left", padx=2)
              
    tk.Button(btns, text="Delete", bg="#dc3545", fg="white", 
              command=lambda: on_delete(tree)).pack(side="left", padx=2)

    # Load Data
    threading.Thread(target=fetch_list, args=(tree,), daemon=True).start()