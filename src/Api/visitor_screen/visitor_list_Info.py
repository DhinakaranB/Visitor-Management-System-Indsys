import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import urllib3
urllib3.disable_warnings()

from Api.Common_signature.common_signature_api import get_visitor_list
# ✅ FIX: Import the new unified function
from Api.visitor_screen.visitor_registerment import show_register_screen
from Api.visitor_screen.visitor_delete import delete_appointment_logic

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

# ================= TABLE STYLE =================
def apply_table_style():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview", background="#FFFFFF", foreground="#111827", rowheight=34, fieldbackground="#FFFFFF", bordercolor="#CBD5E1", borderwidth=1, font=("Segoe UI", 10))
    style.configure("Custom.Treeview.Heading", background="#E5E7EB", foreground="#111827", font=("Segoe UI", 10, "bold"), relief="solid", borderwidth=1)
    style.map("Custom.Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "#FFFFFF")])

# ================= MAIN SCREEN =================
def show_single_visitor_list(root):
    global content_frame, table, pagination_frame, from_picker, to_picker, search_var
    content_frame = root  

    for w in root.winfo_children(): w.destroy()
    apply_table_style()

    # Title
    tk.Label(root, text="Appointment List", font=("Segoe UI", 18, "bold"), bg="#DBEAFE", anchor="w").pack(fill="x", padx=20, pady=10)

    # Search Bar
    top = tk.Frame(root, bg="#DBEAFE")
    top.pack(fill="x", padx=20, pady=5)
    search_var = tk.StringVar()
    ttk.Entry(top, textvariable=search_var, width=25).pack(side="left", padx=5)
    ttk.Label(top, text="From").pack(side="left")
    from_picker = DateEntry(top, width=12, date_pattern="yyyy-mm-dd", maxdate=date.today())
    from_picker.pack(side="left", padx=5)
    ttk.Label(top, text="To").pack(side="left")
    to_picker = DateEntry(top, width=12, date_pattern="yyyy-mm-dd", maxdate=date.today())
    to_picker.pack(side="left", padx=5)
    ttk.Button(top, text="Search", command=lambda: load_data(1)).pack(side="left", padx=5)
    ttk.Button(top, text="Clear", command=clear_search).pack(side="left")

    # Table
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=10)
    cols = ("appointID", "visitorId", "visitorName", "visitReason", "receptionist", "startTime", "endTime", "approval", "actions")
    table = ttk.Treeview(frame, columns=cols, show="headings", style="Custom.Treeview")
    table.pack(fill="both", expand=True)

    headers = [("appointID", "Appoint ID"), ("visitorId", "Visitor ID"), ("visitorName", "Name"), ("visitReason", "Reason"), ("receptionist", "Receptionist"), ("startTime", "Start"), ("endTime", "End"), ("approval", "Approval"), ("actions", "Actions")]
    for c, t in headers: table.heading(c, text=t); table.column(c, anchor="center")
    
    table.column("appointID", width=150)
    table.column("visitorName", width=150, anchor="w")
    table.bind("<Button-1>", on_action_click)

    # Pagination
    pagination_frame = tk.Frame(root)
    pagination_frame.pack(pady=10)
    load_data(1)

# ================= LOAD DATA =================
def load_data(page):
    global current_page, appointments_cache
    current_page = page
    start = from_picker.get_date().strftime("%Y-%m-%dT00:00:00+05:30")
    end = to_picker.get_date().strftime("%Y-%m-%dT23:59:59+05:30")
    appointments_cache = get_visitor_list(page_no=current_page, page_size=PAGE_SIZE, appoint_start=start, appoint_end=end)
    apply_search(search_var.get())

def fill_table():
    table.delete(*table.get_children())
    for i, v in enumerate(filtered_cache):
        visitor = v.get("visitorInfo") or {}
        tag = "odd" if i % 2 == 0 else "even"
        table.insert("", "end", values=(
            v.get("appointID"), visitor.get("visitorId", "-"), visitor.get("visitorName", "-"),
            v.get("visitorReasonName"), v.get("receptionistName"), v.get("appointStartTime"),
            v.get("appointEndTime"), v.get("approvalFlowCode"), "Edit | Delete"
        ), tags=(tag,))

def apply_search(text):
    global filtered_cache
    text = text.lower().strip()
    filtered_cache = appointments_cache if not text else [v for v in appointments_cache if text in str(v).lower()]
    fill_table()
    render_pagination()

def clear_search():
    search_var.set("")
    from_picker.set_date(date.today())
    to_picker.set_date(date.today())
    load_data(1)

# ================= ACTION CLICK =================
def on_action_click(event):
    row = table.identify_row(event.y)
    col = table.identify_column(event.x)
    if not row or col != "#9": return # Only click on 'actions' column

    item_vals = table.item(row)["values"]
    appoint_id = item_vals[0]
    
    # Calculate click position for Edit/Delete split
    x, y, w, h = table.bbox(row, col)
    if event.x - x < w // 2:
        open_registration_for_edit(appoint_id)
    else:
        if messagebox.askyesno("Confirm Delete", f"Delete ID {appoint_id}?"):
            if delete_appointment_logic(appoint_id):
                messagebox.showinfo("Deleted", "Appointment removed.")
                load_data(current_page)
            else:
                messagebox.showerror("Error", "Could not delete.")

def open_registration_for_edit(appoint_id):
    """ Opens the Unified Register Screen in EDIT Mode """
    record = next((r for r in appointments_cache if str(r.get("appointID")) == str(appoint_id)), None)
    if not record:
        messagebox.showerror("Error", "Record not found locally.")
        return

    visitor_info = record.get("visitorInfo", {})
    # ✅ FIX: Call the unified screen with 'edit_data'
    show_register_screen(content_frame, lambda: show_single_visitor_list(content_frame), edit_data=visitor_info)

def render_pagination():
    for w in pagination_frame.winfo_children(): w.destroy()
    ttk.Button(pagination_frame, text="◀", state="normal" if current_page > 1 else "disabled", command=lambda: load_data(current_page - 1)).pack(side="left")
    ttk.Label(pagination_frame, text=f" Page {current_page} ").pack(side="left")
    ttk.Button(pagination_frame, text="▶", command=lambda: load_data(current_page + 1)).pack(side="left")