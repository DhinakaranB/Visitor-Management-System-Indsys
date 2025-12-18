import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import requests
import urllib3
urllib3.disable_warnings()

from Api.Common_signature.common_signature_api import get_visitor_list
from Api.visitor_screen.visitor_registerment import show_create_form
# Add this with your other imports
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


# ================= TABLE STYLE =================
def apply_table_style():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Custom.Treeview",
        background="#FFFFFF",
        foreground="#111827",
        rowheight=34,
        fieldbackground="#FFFFFF",
        bordercolor="#CBD5E1",
        borderwidth=1,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Custom.Treeview.Heading",
        background="#E5E7EB",
        foreground="#111827",
        font=("Segoe UI", 10, "bold"),
        relief="solid",
        borderwidth=1
    )

    style.map(
        "Custom.Treeview",
        background=[("selected", "#2563EB")],
        foreground=[("selected", "#FFFFFF")]
    )


# ================= DELETE API =================
def delete_appointment_api(appoint_id):
    url = "https://127.0.0.1/artemis/api/visitor/v1/appointment/single/delete"
    body = {"appointRecordId": str(appoint_id)}
    return requests.post(url, json=body, verify=False).json()


# ================= MAIN SCREEN =================
def show_single_visitor_list(root):
    global content_frame
    content_frame = root  
    global table, pagination_frame, from_picker, to_picker, search_var

    for w in root.winfo_children():
        w.destroy()

    apply_table_style()

    # -------- TITLE --------
    tk.Label(
        root,
        text="Appointment List",
        font=("Segoe UI", 18, "bold"),
        bg="#DBEAFE",
        anchor="w"
    ).pack(fill="x", padx=20, pady=10)

    # -------- SEARCH BAR --------
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

    # -------- TABLE --------
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = (
        "appointID",
        "visitorId",
        "visitorName",
        "visitReason",
        "receptionist",
        "startTime",
        "endTime",
        "approval",
        "actions"
    )

    table = ttk.Treeview(frame, columns=cols, show="headings", style="Custom.Treeview")
    table.pack(fill="both", expand=True)

    headers = [
        ("appointID", "Appointment ID"),
        ("visitorId", "Visitor ID"),
        ("visitorName", "Visitor Name"),
        ("visitReason", "Visit Reason"),
        ("receptionist", "Receptionist"),
        ("startTime", "Start Time"),
        ("endTime", "End Time"),
        ("approval", "Approval Code"),
        ("actions", "Actions")
    ]

    for c, t in headers:
        table.heading(c, text=t)
        table.column(c, anchor="center")

    table.column("appointID", width=190)
    table.column("visitorId", width=90)
    table.column("visitorName", width=180, anchor="w")
    table.column("visitReason", width=120)
    table.column("receptionist", width=140)
    table.column("startTime", width=190)
    table.column("endTime", width=190)
    table.column("approval", width=130)
    table.column("actions", width=120)

    table.tag_configure("odd", background="#FFFFFF")
    table.tag_configure("even", background="#F8FAFC")

    table.bind("<Button-1>", on_action_click)

    # -------- PAGINATION --------
    pagination_frame = tk.Frame(root)
    pagination_frame.pack(pady=10)

    load_data(1)


# ================= LOAD DATA =================
def load_data(page):
    global current_page, appointments_cache

    current_page = page

    start = from_picker.get_date().strftime("%Y-%m-%dT00:00:00+05:30")
    end = to_picker.get_date().strftime("%Y-%m-%dT23:59:59+05:30")

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

        tag = "odd" if i % 2 == 0 else "even"

        table.insert(
            "",
            "end",
            values=(
                v.get("appointID"),
                visitor.get("visitorId", "-"),
                visitor.get("visitorName", "-"),
                v.get("visitorReasonName"),
                v.get("receptionistName"),
                v.get("appointStartTime"),
                v.get("appointEndTime"),
                v.get("approvalFlowCode"),
                "Edit | Delete"
            ),
            tags=(tag,)
        )


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


# ================= ACTION CLICK =================
def on_action_click(event):
    row = table.identify_row(event.y)
    col = table.identify_column(event.x)

    # ACTIONS column is #9
    if not row or col != "#9":
        return

    appoint_id = table.item(row)["values"][0]

    # Calculate click position
    x, y, w, h = table.bbox(row, col)
    click_x = event.x - x

    # Left half = Edit, Right half = Delete
    if click_x < w // 2:
        open_registration_for_edit(appoint_id)
    else:
        # --- CONFIRM DELETE ---
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete ID {appoint_id}?"):

            # CALL THE LOGIC FROM visitor_delete.py
            success = delete_appointment_logic(appoint_id)

            if success:
                messagebox.showinfo("Deleted", "Appointment removed.")
                load_data(current_page) # Refresh table
            else:
                messagebox.showerror("Error", "Could not delete appointment.")

def open_registration_for_edit(appoint_id):
    # 1. Find the specific record from local cache
    record_to_edit = None
    for record in appointments_cache:
        if str(record.get("appointID")) == str(appoint_id):
            record_to_edit = record
            break
            
    if not record_to_edit:
        messagebox.showerror("Error", "Could not find local record details.")
        return

    # 2. Import the new visitor_edit module
    from Api.visitor_screen.visitor_edit import show_visitor_edit

    # 3. Open the EDIT screen
    show_visitor_edit(
        root_instance=content_frame,
        show_main_screen_callback=lambda: show_single_visitor_list(content_frame),
        existing_data=record_to_edit
    )

def render_pagination():
    for w in pagination_frame.winfo_children():
        w.destroy()

    ttk.Button(
        pagination_frame,
        text="◀",
        state="normal" if current_page > 1 else "disabled",
        command=lambda: load_data(current_page - 1)
    ).pack(side="left", padx=5)

    ttk.Label(
        pagination_frame,
        text=f"Page {current_page}",
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=10)

    ttk.Button(
        pagination_frame,
        text="▶",
        command=lambda: load_data(current_page + 1)
    ).pack(side="left", padx=5)
