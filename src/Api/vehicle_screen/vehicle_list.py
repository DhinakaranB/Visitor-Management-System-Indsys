import tkinter as tk
from tkinter import ttk, messagebox
import math

# --- IMPORTS ---
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None

try:
    from Api.Common_signature.action_grid import ActionGrid
except ImportError:
    ActionGrid = None

# Import Form and Delete modules
try:
    from src.Api.vehicle_screen import vehicle_form
    from src.Api.vehicle_screen import vehicle_delete
except ImportError:
    vehicle_form = None
    vehicle_delete = None

# ================= CONFIG =================
BG_COLOR = "#F4F6F7"
CARD_BG = "white"
PRIMARY_COLOR = "#3498DB"

# API Endpoints
API_VEHICLE_LIST = "/artemis/api/resource/v1/vehicle/vehicleList"
API_GROUP_LIST   = "/artemis/api/resource/v1/vehicleGroup/vehicleGroupList"

# Color Mapping
VEHICLE_COLORS = {
    0: "Other", 1: "White", 2: "Silver", 3: "Gray", 4: "Black",
    5: "Red", 6: "Blue", 7: "Yellow", 8: "Green", 9: "9 - Brown"
}

# State
current_page = 1
page_size = 10
total_records = 0
vehicle_cache = []

table = None
pagination_frame = None
plate_var = None
group_combo = None
main_frame_ref = None

def show_list(content_frame):
    """
    Renamed to show_list to match other modules.
    """
    global table, pagination_frame, plate_var, group_combo, current_page, main_frame_ref
    main_frame_ref = content_frame
    current_page = 1

    # 1. Setup UI
    for widget in content_frame.winfo_children(): widget.destroy()
    content_frame.config(bg=CARD_BG)

    # Header
    header = tk.Frame(content_frame, bg=CARD_BG, padx=20, pady=15)
    header.pack(fill="x")
    tk.Label(header, text="Vehicle List", font=("Segoe UI", 20, "bold"), bg=CARD_BG, fg="#2C3E50").pack(side="left")

    # Add Button
    tk.Button(header, text="+ Add Vehicle", bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5, bd=0, cursor="hand2",
              command=lambda: vehicle_form.show_vehicle_form(content_frame, lambda: show_list(content_frame))
              ).pack(side="right")

    # --- Search Bar ---
    search_frame = tk.Frame(content_frame, bg=BG_COLOR, pady=10, padx=20)
    search_frame.pack(fill="x")
    
    # Plate Filter
    plate_var = tk.StringVar()
    tk.Label(search_frame, text="Plate No:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
    ttk.Entry(search_frame, textvariable=plate_var, width=15).pack(side="left", padx=(5, 15))

    # Group Filter (Dropdown)
    tk.Label(search_frame, text="Group:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
    group_combo = ttk.Combobox(search_frame, width=20, state="readonly")
    group_combo.pack(side="left", padx=(5, 15))
    
    load_group_options()

    tk.Button(search_frame, text="🔍 Search", bg=PRIMARY_COLOR, fg="white", bd=0, padx=15, 
              command=lambda: load_data(1)).pack(side="left", padx=5)
    
    tk.Button(search_frame, text="✖ Clear", bg="white", fg="#7F8C8D", bd=1, padx=10, 
              command=clear_search).pack(side="left")

    # --- Action Grid ---
    tree_frame = tk.Frame(content_frame, bg="white")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # ✅ UPDATED COLUMNS: Removed 'Group Index' / System IDs
    cols = [
        ("plateNo", "Plate No", 3),
        ("personName", "Owner Name", 4),
        ("vehicleColor", "Color", 2),
        ("phoneNo", "Phone", 3)
    ]

    if ActionGrid:
        table = ActionGrid(
            tree_frame,
            columns=cols,
            edit_command=handle_edit,
            delete_command=handle_delete
        )
        table.pack(fill="both", expand=True)
    else:
        tk.Label(tree_frame, text="ActionGrid Missing", fg="red").pack()

    # Pagination
    pagination_frame = tk.Frame(content_frame, bg=BG_COLOR, pady=10)
    pagination_frame.pack(fill="x")

    load_data(1)

# ================= LOGIC =================
def load_group_options():
    """ Fetches vehicle groups to populate the search dropdown """
    if not api_handler: return
    try:
        res = api_handler.call_api(API_GROUP_LIST, {"pageNo": 1, "pageSize": 100})
        if res and str(res.get("code")) == "0":
            rows = res.get("data", {}).get("list", [])
            options = ["All"] + [f"{g['vehicleGroupIndexCode']} - {g['vehicleGroupName']}" for g in rows]
            group_combo['values'] = options
            group_combo.current(0)
    except:
        pass

def load_data(page):
    global current_page, total_records, vehicle_cache
    current_page = page
    
    payload = {
        "pageNo": current_page,
        "pageSize": page_size
    }
    
    plate = plate_var.get().strip()
    if plate: payload["plateNo"] = plate

    group_val = group_combo.get()
    if group_val and group_val != "All":
        gid = group_val.split(" - ")[0]
        payload["vehicleGroupIndexCode"] = gid

    if api_handler:
        res = api_handler.call_api(API_VEHICLE_LIST, payload)
        
        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            rows = data.get("list", [])
            total_records = data.get("total", 0)
            vehicle_cache = rows 

            formatted_rows = []
            for r in rows:
                new_row = r.copy()
                c_id = r.get("vehicleColor")
                try: c_id = int(c_id)
                except: c_id = -1
                new_row["vehicleColor"] = VEHICLE_COLORS.get(c_id, str(c_id))
                formatted_rows.append(new_row)

            if table: table.render_data(formatted_rows)
            render_pagination()
        else:
            if table: table.render_data([])
            render_pagination()
    else:
        if table: table.render_data([])

def render_pagination():
    for w in pagination_frame.winfo_children(): w.destroy()
    total_pages = math.ceil(total_records / page_size) if total_records else 1
    
    left_frame = tk.Frame(pagination_frame, bg=BG_COLOR)
    left_frame.pack(side="left", padx=20)

    state_prev = "normal" if current_page > 1 else "disabled"
    tk.Button(left_frame, text="◀ Prev", command=lambda: load_data(current_page - 1), 
              state=state_prev, bg="white", bd=1).pack(side="left", padx=5)

    tk.Label(left_frame, text=f"Page {current_page}", bg=BG_COLOR, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

    state_next = "normal" if current_page < total_pages else "disabled"
    tk.Button(left_frame, text="Next ▶", command=lambda: load_data(current_page + 1), 
              state=state_next, bg="white", bd=1).pack(side="left", padx=5)

    tk.Label(pagination_frame, text=f"(Total: {total_records})", bg=BG_COLOR, fg="#7F8C8D").pack(side="right", padx=20)

def clear_search():
    plate_var.set("")
    if group_combo['values']: group_combo.current(0)
    load_data(1)

# ================= HANDLERS =================
def handle_edit(row_data):
    plate = row_data.get("plateNo")
    full_obj = next((v for v in vehicle_cache if v.get("plateNo") == plate), row_data)
    
    if vehicle_form:
        vehicle_form.show_vehicle_form(
            main_frame_ref, 
            on_success_callback=lambda: show_list(main_frame_ref), 
            edit_data=full_obj
        )

def handle_delete(row_data):
    plate = row_data.get("plateNo")
    
    if messagebox.askyesno("Confirm Delete", f"Delete Vehicle '{plate}'?"):
        if vehicle_delete and vehicle_delete.delete_vehicle(plate):
            messagebox.showinfo("Deleted", "Vehicle deleted successfully.")
            load_data(current_page)