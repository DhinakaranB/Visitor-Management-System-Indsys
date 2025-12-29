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

# Import your Form and Delete modules
try:
    from src.Api.vehicle_screen import vehicle_group_form
    from src.Api.vehicle_screen import vehicle_group_delete
except ImportError:
    vehicle_group_form = None
    vehicle_group_delete = None

# ================= CONFIG =================
BG_COLOR = "#F4F6F7"
CARD_BG = "white"
PRIMARY_COLOR = "#3498DB"
TEXT_COLOR = "#2C3E50"

# API Endpoint
API_GROUP_LIST = "/artemis/api/resource/v1/vehicleGroup/vehicleGroupList"

# State
current_page = 1
page_size = 20
total_records = 0
group_cache = []

table = None
pagination_frame = None
name_var = None
main_frame_ref = None

def show_group_list(content_frame):
    global table, pagination_frame, name_var, current_page, main_frame_ref
    main_frame_ref = content_frame
    current_page = 1

    # 1. Setup UI
    for widget in content_frame.winfo_children(): widget.destroy()
    content_frame.config(bg=CARD_BG)

    # Header
    header = tk.Frame(content_frame, bg=CARD_BG, padx=20, pady=15)
    header.pack(fill="x")
    tk.Label(header, text="Vehicle Group List", font=("Segoe UI", 20, "bold"), bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")

    # Add New Button
    tk.Button(header, text="+ Add Group", bg="#28a745", fg="white", font=("Segoe UI", 10, "bold"),
              padx=15, pady=5, bd=0, cursor="hand2",
              command=lambda: vehicle_group_form.show_group_form(content_frame, lambda: show_group_list(content_frame))
              ).pack(side="right")

    # Search Bar
    search_frame = tk.Frame(content_frame, bg=BG_COLOR, pady=10, padx=20)
    search_frame.pack(fill="x")
    
    name_var = tk.StringVar()
    tk.Label(search_frame, text="Group Name:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
    entry = ttk.Entry(search_frame, textvariable=name_var, width=25)
    entry.pack(side="left", padx=(5, 15))
    entry.bind("<Return>", lambda e: load_data(1))

    tk.Button(search_frame, text="🔍 Search", bg=PRIMARY_COLOR, fg="white", bd=0, padx=15, 
              command=lambda: load_data(1)).pack(side="left", padx=5)
    
    tk.Button(search_frame, text="✖ Clear", bg="white", fg="#7F8C8D", bd=1, padx=10, 
              command=lambda: [name_var.set(""), load_data(1)]).pack(side="left")

    # Action Grid
    tree_frame = tk.Frame(content_frame, bg="white")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # ✅ CORRECTED COLUMNS (Matches API Response)
    cols = [
        ("vehicleGroupIndexCode", "Index Code", 2), # Was 'indexCode'
        ("vehicleGroupName", "Group Name", 4),      # Was 'name'
        ("parentIndexCode", "Parent Index", 2),
        ("description", "Description", 3)
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
def load_data(page):
    global current_page, total_records, group_cache
    current_page = page
    
    # Payload
    payload = {
        "pageNo": current_page,
        "pageSize": page_size
    }
    
    if name_var.get().strip():
        payload["vehicleGroupName"] = name_var.get().strip() # Also updated filter key

    if api_handler:
        res = api_handler.call_api(API_GROUP_LIST, payload)
        
        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            rows = data.get("list", [])
            total_records = data.get("total", 0)
            group_cache = rows 

            if table: table.render_data(rows)
            render_pagination()
        else:
            if table: table.render_data([])
            render_pagination()
    else:
        # Mock Data (Updated keys)
        if table: table.render_data([
            {"vehicleGroupIndexCode": "1", "vehicleGroupName": "Staff", "parentIndexCode": "0", "description": "Employees"},
            {"vehicleGroupIndexCode": "2", "vehicleGroupName": "Visitor", "parentIndexCode": "0", "description": "Guests"}
        ])

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

# ================= HANDLERS =================
def handle_edit(row_data):
    # ✅ Corrected Key
    code = str(row_data.get("vehicleGroupIndexCode"))
    obj = next((g for g in group_cache if str(g.get("vehicleGroupIndexCode")) == code), row_data)
    
    if vehicle_group_form:
        vehicle_group_form.show_group_form(
            main_frame_ref, 
            on_success_callback=lambda: show_group_list(main_frame_ref), 
            edit_data=obj
        )

def handle_delete(row_data):
    # ✅ Corrected Key
    code = str(row_data.get("vehicleGroupIndexCode"))
    name = row_data.get("vehicleGroupName")
    
    if messagebox.askyesno("Confirm Delete", f"Delete Group '{name}'?"):
        if vehicle_group_delete and vehicle_group_delete.delete_group(code):
            messagebox.showinfo("Deleted", "Group deleted successfully.")
            load_data(current_page)