import json
import tkinter as tk
from tkinter import ttk, messagebox

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# --- API ENDPOINTS ---
# Get all regions (root and children)
GET_ALL_REGIONS_API = "/artemis/api/resource/v1/regions"
# Get sub-regions of a specific parent
GET_SUB_REGIONS_API = "/artemis/api/resource/v1/regions/subRegions"

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

def fetch_regions(tree):
    """Fetches all regions and populates the treeview"""
    # 1. Prepare Payload (Pagination)
    payload = {
        "pageNo": 1,
        "pageSize": 500,
        "treeCode": "0" # "0" usually fetches the whole tree
    }
    
    print(f"📡 Fetching Regions...")
    data = call_api(GET_ALL_REGIONS_API, payload)
    
    # 2. Clear Tree
    for item in tree.get_children():
        tree.delete(item)

    # 3. Parse Response
    if data and data.get("code") == "0":
        regions = data.get("data", {}).get("list", [])
        
        for r in regions:
            r_name = r.get("name", "Unknown")
            r_code = r.get("indexCode", "-")
            r_parent = r.get("parentIndexCode", "-")
            
            # Insert into Treeview
            tree.insert("", "end", values=(r_name, r_code, r_parent))
            
        messagebox.showinfo("Success", f"Fetched {len(regions)} regions.")
    else:
        err = data.get("msg") if data else "Unknown Error"
        messagebox.showerror("Error", f"Failed to fetch regions: {err}")

def show_region_list(parent_frame):
    for w in parent_frame.winfo_children(): w.destroy()

    # Header
    header = tk.Frame(parent_frame, bg="#D6EAF8", pady=10)
    header.pack(fill="x", padx=20)
    tk.Label(header, text="Region / Area List (Physical View)", font=("Segoe UI", 18, "bold"), bg="#D6EAF8").pack(side="left")
    
    # Refresh Button
    tk.Button(header, text="🔄 Refresh List", bg="#17a2b8", fg="white", 
              command=lambda: fetch_regions(tree)).pack(side="right", padx=10)

    # Treeview
    cols = ("Name", "Index Code", "Parent Code")
    tree = ttk.Treeview(parent_frame, columns=cols, show="headings", height=20)
    
    tree.heading("Name", text="Region Name")
    tree.heading("Index Code", text="Region Index Code")
    tree.heading("Parent Code", text="Parent Index Code")
    
    tree.column("Name", width=200)
    tree.column("Index Code", width=200)
    tree.column("Parent Code", width=200)
    
    tree.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Auto-load
    fetch_regions(tree)