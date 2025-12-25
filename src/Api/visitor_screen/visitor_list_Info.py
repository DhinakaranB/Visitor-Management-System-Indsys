import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import urllib3
urllib3.disable_warnings()

from Api.Common_signature.common_signature_api import get_visitor_list
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

    # Header Style
    style.configure(
        "Custom.Treeview.Heading",
        background="#E5E7EB",
        foreground="#111827",
        font=("Segoe UI", 10, "bold"),
        relief="flat"
    )

    # Row Style
    style.configure(
        "Custom.Treeview",
        background="#FFFFFF",
        foreground="#111827",
        rowheight=40, # Taller rows for better icon visibility
        fieldbackground="#FFFFFF",
        bordercolor="#E5E7EB",
        borderwidth=0,
        font=("Segoe UI", 10)
    )

    # Selection Style
    style.map(
        "Custom.Treeview",
        background=[("selected", "#3498DB")],
        foreground=[("selected", "#FFFFFF")]
    )

# ================= MAIN SCREEN =================
def show_single_visitor_list(root):
    global content_frame
    content_frame = root  
    global table, pagination_frame, from_picker, to_picker, search_var

    # Clear previous content
    for w in root.winfo_children():
        w.destroy()

    apply_table_style()

    # --- Header ---
    header_frame = tk.Frame(root, bg="white", padx=20, pady=15)
    header_frame.pack(fill="x")
    
    tk.Label(
        header_frame,
        text="Appointment List",
        font=("Segoe UI", 20, "bold"),
        bg="white",
        fg="#2C3E50"
    ).pack(side="left")

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

    btn_search = tk.Button(search_frame, text="🔍 Search", bg="#3498DB", fg="white", bd=0, padx=15, command=lambda: load_data(1))
    btn_search.pack(side="left", padx=10)
    
    btn_clear = tk.Button(search_frame, text="✖ Clear", bg="white", fg="#7F8C8D", bd=1, padx=10, command=clear_search)
    btn_clear.pack(side="left")

    # --- Table ---
    tree_frame = tk.Frame(root, bg="white")
    tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = (
        "appointID",
        "visitorName",
        "visitReason",
        "receptionist",
        "startTime",
        "endTime",
        "actions" # Combined Edit/Delete column
    )

    table = ttk.Treeview(tree_frame, columns=cols, show="headings", style="Custom.Treeview")
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    table.pack(fill="both", expand=True)

    # Columns Config
    table.heading("appointID", text="ID")
    table.heading("visitorName", text="Visitor Name")
    table.heading("visitReason", text="Reason")
    table.heading("receptionist", text="Receptionist")
    table.heading("startTime", text="Start Time")
    table.heading("endTime", text="End Time")
    table.heading("actions", text="Actions")

    table.column("appointID", width=50, anchor="center")
    table.column("visitorName", width=150, anchor="w")
    table.column("visitReason", width=100, anchor="center")
    table.column("receptionist", width=100, anchor="center")
    table.column("startTime", width=120, anchor="center")
    table.column("endTime", width=120, anchor="center")
    table.column("actions", width=100, anchor="center") # Centered Actions

    # Bind Click Event
    table.bind("<Button-1>", on_action_click)

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

    # API Call
    appointments_cache = get_visitor_list(
        page_no=current_page,
        page_size=PAGE_SIZE,
        appoint_start=start,
        appoint_end=end
    )

    apply_search(search_var.get())


# ================= FILL TABLE =================
def fill_table():
    table.delete(*table.get_children())

    for i, v in enumerate(filtered_cache):
        visitor = v.get("visitorInfo") or {}
        
        # Format Times (Optional cleanup)
        s_time = v.get("appointStartTime", "")[:16].replace("T", " ")
        e_time = v.get("appointEndTime", "")[:16].replace("T", " ")

        tag = "odd" if i % 2 == 0 else "even"
        
        # INSERT ROW with ICONS
        # We use Unicode icons: ✎ (Edit) and 🗑 (Delete)
        # Added spaces for easier clicking separation
        table.insert(
            "",
            "end",
            values=(
                v.get("appointID"),
                visitor.get("visitorName", "Guest"),
                v.get("visitorReasonName", "--"),
                v.get("receptionistName", "--"),
                s_time,
                e_time,
                "✎      🗑"  # Icons
            ),
            tags=(tag,)
        )
    
    table.tag_configure("odd", background="white")
    table.tag_configure("even", background="#F8FAFC")


# ================= SEARCH =================
def apply_search(text):
    global filtered_cache
    text = text.lower().strip()

    if not text:
        filtered_cache = appointments_cache
    else:
        filtered_cache = [v for v in appointments_cache if text in str(v).lower()]

    fill_table()
    render_pagination()

def clear_search():
    search_var.set("")
    from_picker.set_date(date.today())
    to_picker.set_date(date.today())
    load_data(1)


# ================= ACTION CLICK HANDLER =================
def on_action_click(event):
    """ Handle clicks on the table, specifically for Edit/Delete icons """
    row_id = table.identify_row(event.y)
    col_id = table.identify_column(event.x)

    if not row_id: return

    # Check if clicked on "Actions" column (usually #7 based on our layout)
    # The column index might vary, but it's the last one.
    if col_id == "#7": 
        # Get data
        item_vals = table.item(row_id)["values"]
        appoint_id = item_vals[0] # ID is in first column

        # Determine if click was on Left (Edit) or Right (Delete)
        # We calculate the bounding box of the cell
        x, y, w, h = table.bbox(row_id, col_id)
        click_x_in_cell = event.x - x
        
        # Split cell in half: Left = Edit, Right = Delete
        if click_x_in_cell < w / 2:
            # --- EDIT ACTION ---
            open_registration_for_edit(appoint_id)
        else:
            # --- DELETE ACTION ---
            confirm_delete(appoint_id)

def confirm_delete(appoint_id):
    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Appointment {appoint_id}?"):
        success = delete_appointment_logic(appoint_id)
        if success:
            messagebox.showinfo("Deleted", "Appointment deleted successfully.")
            load_data(current_page) # Refresh list
        else:
            messagebox.showerror("Error", "Failed to delete appointment.")

def open_registration_for_edit(appoint_id):
    record = next((r for r in appointments_cache if str(r.get("appointID")) == str(appoint_id)), None)
    if not record:
        messagebox.showerror("Error", "Record details not found.")
        return

    visitor_info = record.get("visitorInfo", {})
    # Pass 'edit_data' to trigger Edit Mode in the unified screen
    show_register_screen(
        root_instance=content_frame,
        show_main_screen_callback=lambda: show_single_visitor_list(content_frame),
        edit_data=visitor_info
    )

def render_pagination():
    for w in pagination_frame.winfo_children(): w.destroy()

    btn_prev = tk.Button(pagination_frame, text="◀ Prev", command=lambda: load_data(current_page - 1),
                         state="normal" if current_page > 1 else "disabled", bg="white", bd=1)
    btn_prev.pack(side="left", padx=10)

    tk.Label(pagination_frame, text=f"Page {current_page}", bg="#F4F6F7", font=("Segoe UI", 10, "bold")).pack(side="left")

    btn_next = tk.Button(pagination_frame, text="Next ▶", command=lambda: load_data(current_page + 1),
                         bg="white", bd=1)
    btn_next.pack(side="left", padx=10)