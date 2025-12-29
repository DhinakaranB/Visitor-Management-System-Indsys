import tkinter as tk
from tkinter import ttk, messagebox
import math
import json

# Try importing your API handler
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None

# IMPORT THE ACTION GRID (Crucial for the Edit/Delete icons)
try:
    from Api.Common_signature.action_grid import ActionGrid 
except ImportError:
    print("⚠️ ActionGrid not found. Icons will be missing.")
    ActionGrid = None

# --- IMPORT YOUR EDIT/DELETE MODULES ---
try:
    from src.Api.person_screen import person_form
    from src.Api.person_screen import person_delete
except ImportError:
    print("⚠️ Person modules (form/delete) not found.")
    person_form = None
    person_delete = None

# ================= CONFIGURATION =================
BG_COLOR = "#F4F6F7"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#3498DB"   
TEXT_COLOR = "#2C3E50"
LABEL_COLOR = "#7F8C8D"

# API Endpoint 
API_PERSON_LIST = "/artemis/api/resource/v1/person/personList"

# --- STATE VARIABLES ---
current_page = 1
page_size = 15  
total_records = 0
person_cache = [] # Stores full objects for Editing

table = None
pagination_frame = None
name_var = None
id_var = None
main_frame_ref = None # Reference to refresh the screen

def show_list(content_frame):
    """
    Main entry point to render the Person List screen.
    """
    global table, pagination_frame, name_var, id_var, current_page, main_frame_ref
    main_frame_ref = content_frame
    current_page = 1 

    # 1. Clear previous content
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    content_frame.config(bg="white") 

    # --- HEADER ---
    header_frame = tk.Frame(content_frame, bg="white", padx=20, pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="Person List", font=("Segoe UI", 20, "bold"), bg="white", fg="#2C3E50").pack(side="left")

    # --- SEARCH BAR ---
    search_frame = tk.Frame(content_frame, bg=BG_COLOR, pady=10, padx=20)
    search_frame.pack(fill="x")

    # Variables
    name_var = tk.StringVar()
    id_var = tk.StringVar()

    # Inputs
    tk.Label(search_frame, text="Person Name:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
    entry_name = ttk.Entry(search_frame, textvariable=name_var, width=20)
    entry_name.pack(side="left", padx=(5, 15))
    entry_name.bind("<Return>", lambda e: load_data(1))
    
    tk.Label(search_frame, text="Person ID:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
    entry_id = ttk.Entry(search_frame, textvariable=id_var, width=15)
    entry_id.pack(side="left", padx=(5, 15))
    entry_id.bind("<Return>", lambda e: load_data(1))

    # Buttons
    tk.Button(search_frame, text="🔍 Search", bg=PRIMARY_COLOR, fg="white", bd=0, padx=15, 
              command=lambda: load_data(1)).pack(side="left", padx=5)
    
    tk.Button(search_frame, text="✖ Clear", bg="white", fg="#7F8C8D", bd=1, padx=10, 
              command=lambda: clear_search()).pack(side="left")

    # --- ACTION GRID (THE TABLE WITH ICONS) ---
    tree_frame = tk.Frame(content_frame, bg="white")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Column Definition: (JSON Key, Display Title, Width Weight)
    cols = [
        ("personCode", "Person ID", 2),
        ("personName", "Name", 3),
        ("gender", "Gender", 2),
        ("orgPathName", "Organization / Dept", 4),
        ("phoneNo", "Phone", 2)
    ]

    # Initialize your Custom Grid
    if ActionGrid:
        table = ActionGrid(
            tree_frame,
            columns=cols,
            edit_command=handle_edit_click,   # Edit Callback
            delete_command=handle_delete_click # Delete Callback
        )
        table.pack(fill="both", expand=True)
    else:
        tk.Label(tree_frame, text="ActionGrid Missing", fg="red").pack()

    # --- PAGINATION FOOTER ---
    pagination_frame = tk.Frame(content_frame, bg=BG_COLOR, pady=10)
    pagination_frame.pack(fill="x")

    # Initial Load
    load_data(1)


# ================= LOGIC =================

def load_data(page):
    global current_page, total_records, person_cache
    current_page = page
    
    # 1. Build Payload
    payload = {
        "pageNo": current_page,
        "pageSize": page_size
    }
    
    p_name = name_var.get().strip()
    p_id = id_var.get().strip()
    
    if p_name: payload["personName"] = p_name
    if p_id: payload["personId"] = p_id

    # 2. API Call
    if api_handler:
        res = api_handler.call_api(API_PERSON_LIST, payload)
        
        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            rows = data.get("list", [])
            total_records = data.get("total", 0)
            
            # --- CRITICAL: STORE FULL DATA FOR EDIT ---
            person_cache = rows 

            # Format Data for Display
            formatted_rows = []
            for r in rows:
                new_row = r.copy()
                
                # Gender Mapping
                g_val = str(r.get("gender", ""))
                new_row["gender"] = "Male" if g_val == "1" else "Female" if g_val == "2" else "-"
                
                # Ensure Organization has a value
                if not new_row.get("orgPathName"):
                    new_row["orgPathName"] = new_row.get("orgName", "-")
                    
                formatted_rows.append(new_row)

            # Render to Table
            if table:
                table.render_data(formatted_rows)
            
            render_pagination()
        else:
            if table: table.render_data([]) 
            render_pagination()
            # print(f"API Error: {res}") 
    else:
        # Mock Data
        print("Mocking Data...")
        mock_data = [
            {"personId": "101", "personName": "John Doe", "gender": "1", "orgPathName": "IT Dept", "phoneNo": "1234567890"},
            {"personId": "102", "personName": "Jane Smith", "gender": "2", "orgPathName": "HR Dept", "phoneNo": "0987654321"}
        ]
        person_cache = mock_data
        if table: table.render_data(mock_data)


def render_pagination():
    for w in pagination_frame.winfo_children(): w.destroy()
    
    total_pages = math.ceil(total_records / page_size) if total_records else 1

    # Left Container (Buttons)
    left_frame = tk.Frame(pagination_frame, bg=BG_COLOR)
    left_frame.pack(side="left", padx=20)

    # Prev Button
    state_prev = "normal" if current_page > 1 else "disabled"
    tk.Button(left_frame, text="◀ Prev", command=lambda: load_data(current_page - 1), 
              state=state_prev, bg="white", bd=1).pack(side="left", padx=5)

    # Page Label
    tk.Label(left_frame, text=f"Page {current_page}", bg=BG_COLOR, font=("Segoe UI", 10, "bold")).pack(side="left", padx=5)

    # Next Button
    state_next = "normal" if current_page < total_pages else "disabled"
    tk.Button(left_frame, text="Next ▶", command=lambda: load_data(current_page + 1), 
              state=state_next, bg="white", bd=1).pack(side="left", padx=5)

    # Right Container (Total Count)
    tk.Label(pagination_frame, text=f"(Total: {total_records})", bg=BG_COLOR, fg=LABEL_COLOR).pack(side="right", padx=20)


def clear_search():
    name_var.set("")
    id_var.set("")
    load_data(1)


# ================= ACTION HANDLERS =================

def handle_edit_click(row_data):
    """ Finds the full person object and calls the Edit Form """
    p_id = str(row_data.get("personId"))
    
    # 1. Find full object in cache (because row_data might be formatted/partial)
    person_obj = next((p for p in person_cache if str(p.get("personId")) == p_id), None)
    
    if person_obj and person_form:
        # 2. Call the Edit Form from your old code logic
        # We pass show_list as the callback so the list refreshes after saving
        person_form.show_create_form(
            main_frame_ref, 
            on_success_callback=lambda: show_list(main_frame_ref), 
            edit_data=person_obj
        )
    elif not person_form:
        messagebox.showerror("Error", "Person Form module missing.")
    else:
        messagebox.showerror("Error", "Could not find person details in cache.")

def handle_delete_click(row_data):
    """ Calls the Delete API """
    # ✅ FIX: Get 'personCode' instead of 'personId'
    p_code = str(row_data.get("personCode"))  
    name = row_data.get("personName")
    
    if not person_delete:
        messagebox.showerror("Error", "Person Delete module missing.")
        return

    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete?\n\nName: {name}\nCode: {p_code}"):
        # Call the fixed delete logic
        success = person_delete.delete_by_code(p_code)
        
        if success:
            messagebox.showinfo("Deleted", "Person deleted successfully.")
            load_data(current_page)