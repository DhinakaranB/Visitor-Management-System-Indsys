import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import urllib3
urllib3.disable_warnings()

from Api.Common_signature.common_signature_api import get_visitor_list
from Api.visitor_screen.visitor_registerment import show_register_screen
from Api.visitor_screen.visitor_delete import delete_appointment_logic

# IMPORT THE NEW GRID CLASS
from Api.Common_signature.action_grid import ActionGrid 

# ================= CONFIG =================
PAGE_SIZE = 15
current_page = 1
appointments_cache = []
filtered_cache = []

table = None
pagination_frame = None
from_picker = None
to_picker = None
search_var = None
content_frame = None  

# ================= MAIN SCREEN =================
def show_single_visitor_list(root):
    global content_frame
    content_frame = root  
    global table, pagination_frame, from_picker, to_picker, search_var

    for w in root.winfo_children(): w.destroy()
    root.configure(bg="white")

    # --- Header ---
    header_frame = tk.Frame(root, bg="white", padx=20, pady=15)
    header_frame.pack(fill="x")
    tk.Label(header_frame, text="Appointment List", font=("Segoe UI", 20, "bold"), bg="white", fg="#2C3E50").pack(side="left")

    # --- Search Bar ---
    search_frame = tk.Frame(root, bg="#F4F6F7", pady=10, padx=20)
    search_frame.pack(fill="x")

    search_var = tk.StringVar()
    entry_search = ttk.Entry(search_frame, textvariable=search_var, width=30)
    entry_search.pack(side="left", padx=(0, 10))
    entry_search.bind("<Return>", lambda e: load_data(1))

    tk.Label(search_frame, text="From:", bg="#F4F6F7").pack(side="left")
    from_picker = DateEntry(search_frame, width=12, date_pattern="yyyy-mm-dd", maxdate=date.today())
    from_picker.pack(side="left", padx=5)

    tk.Label(search_frame, text="To:", bg="#F4F6F7").pack(side="left")
    to_picker = DateEntry(search_frame, width=12, date_pattern="yyyy-mm-dd", maxdate=date.today())
    to_picker.pack(side="left", padx=5)

    tk.Button(search_frame, text="🔍 Search", bg="#3498DB", fg="white", bd=0, padx=15, command=lambda: load_data(1)).pack(side="left", padx=10)
    tk.Button(search_frame, text="✖ Clear", bg="white", fg="#7F8C8D", bd=1, padx=10, command=clear_search).pack(side="left")

    # --- ACTION GRID ---
    tree_frame = tk.Frame(root, bg="white")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # UPDATED COLUMNS: (JSON_Key, Title, Weight)
    # Weight determines how much space the column takes relative to others.
    cols = [
            ("appointID", "ID", 3),              # ID is usually short
            ("visitorName", "Visitor Name", 2),  # Name is long, give it more space
            ("visitReasonName", "Reason", 2),    
            ("receptionistName", "Receptionist", 2),
            ("appointStartTime", "Start Time", 2),
            ("appointEndTime", "End Time", 2)
        ]

    table = ActionGrid(
        tree_frame,
        columns=cols,
        edit_command=handle_edit_click,
        delete_command=handle_delete_click
    )
    table.pack(fill="both", expand=True)

    # --- Pagination ---
    pagination_frame = tk.Frame(root, bg="#F4F6F7", pady=10)
    pagination_frame.pack(fill="x")

    load_data(1)


# ================= LOAD DATA =================
def load_data(page):
    global current_page, appointments_cache
    current_page = page
    start = from_picker.get_date().strftime("%Y-%m-%dT00:00:00+05:30")
    end = to_picker.get_date().strftime("%Y-%m-%dT23:59:59+05:30")

    appointments_cache = get_visitor_list(page_no=current_page, page_size=PAGE_SIZE, appoint_start=start, appoint_end=end)
    apply_search(search_var.get())

# ================= SEARCH & RENDER =================
def apply_search(text):
    global filtered_cache
    text = text.lower().strip()
    
    if not text: filtered_cache = appointments_cache
    else: filtered_cache = [v for v in appointments_cache if text in str(v).lower()]

    flat_data = []
    for row in filtered_cache:
        r = row.copy()
        v_info = r.get("visitorInfo") or {}
        if not r.get("visitorName") and v_info.get("visitorName"):
            r["visitorName"] = v_info.get("visitorName")
            
        if r.get("appointStartTime"): r["appointStartTime"] = r["appointStartTime"][:16].replace("T", " ")
        if r.get("appointEndTime"): r["appointEndTime"] = r["appointEndTime"][:16].replace("T", " ")

        flat_data.append(r)

    table.render_data(flat_data)
    render_pagination()

def clear_search():
    search_var.set("")
    from_picker.set_date(date.today())
    to_picker.set_date(date.today())
    load_data(1)

# ================= ACTIONS =================
def handle_edit_click(row_data):
    appoint_id = row_data.get("appointID")
    open_registration_for_edit(appoint_id)

def handle_delete_click(row_data):
    appoint_id = row_data.get("appointID")
    if messagebox.askyesno("Confirm Delete", f"Delete Appointment {appoint_id}?"):
        if delete_appointment_logic(appoint_id):
            messagebox.showinfo("Deleted", "Appointment deleted successfully.")
            load_data(current_page) 
        else:
            messagebox.showerror("Error", "Failed to delete appointment.")

def open_registration_for_edit(appoint_id):
    record = next((r for r in appointments_cache if str(r.get("appointID")) == str(appoint_id)), None)
    if not record: return
    show_register_screen(root_instance=content_frame, show_main_screen_callback=lambda: show_single_visitor_list(content_frame), edit_data=record.get("visitorInfo", {}))

# ================= PAGINATION =================
def render_pagination():
    for w in pagination_frame.winfo_children(): w.destroy()
    
    state = "normal" if current_page > 1 else "disabled"
    tk.Button(pagination_frame, text="◀ Prev", command=lambda: load_data(current_page - 1), state=state, bg="white", bd=1).pack(side="left", padx=10)
    tk.Label(pagination_frame, text=f"Page {current_page}", bg="#F4F6F7", font=("Segoe UI", 10, "bold")).pack(side="left")
    tk.Button(pagination_frame, text="Next ▶", command=lambda: load_data(current_page + 1), bg="white", bd=1).pack(side="left", padx=10)