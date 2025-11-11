import tkinter as tk
from tkinter import ttk, messagebox
from Api.common_signature_api import call_api  # Reusing your common API utility

# --- Constants ---
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
HEADER_FONT = ("Segoe UI", 16, "bold")
CELL_FONT = ("Segoe UI", 10)
PAGE_SIZE = 20

current_page = 1
door_cache = []

def show_door_list(root_instance):
    """Display the Door List screen."""
    global current_page, door_cache

    for widget in root_instance.winfo_children():
        widget.destroy()

    tk.Label(
        root_instance,
        text="🚪 Door List",
        font=HEADER_FONT,
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=(15, 10))

    # --- Table Frame ---
    table_frame = tk.Frame(root_instance, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=30, pady=10)

    yscroll = ttk.Scrollbar(table_frame, orient="vertical")
    xscroll = ttk.Scrollbar(table_frame, orient="horizontal")

    columns = ("doorId", "doorName", "deviceName", "status", "description")

    table = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        yscrollcommand=yscroll.set,
        xscrollcommand=xscroll.set,
        style="Modern.Treeview"
    )

    yscroll.config(command=table.yview)
    xscroll.config(command=table.xview)
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    # --- Table Headers ---
    headers = {
        "doorId": "Door ID",
        "doorName": "Door Name",
        "deviceName": "Linked Device",
        "status": "Status",
        "description": "Description"
    }

    for col in columns:
        table.heading(col, text=headers[col], anchor="center")
        table.column(col, width=180, anchor="center")

    # --- Table Style ---
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Modern.Treeview",
        background="white",
        foreground=TEXT_COLOR,
        rowheight=28,
        fieldbackground="white",
        font=CELL_FONT,
        bordercolor="#D6DBDF",
        borderwidth=1
    )
    style.configure(
        "Modern.Treeview.Heading",
        background=PRIMARY_COLOR,
        foreground="white",
        font=("Segoe UI", 10, "bold")
    )
    table.tag_configure("oddrow", background="#F8F9F9")
    table.tag_configure("evenrow", background="#EAF2F8")

    # --- Load Data ---
    try:
        if not door_cache:
            response = call_api("api/resource/v1/door/list", method="POST", payload={"pageNo": 1, "pageSize": 200})
            data = response.get("data", {})
            door_cache = data.get("list", []) or data.get("DoorInfo", []) or []

        if not door_cache:
            tk.Label(root_instance, text="No doors found.", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=15)
            return

        door_cache.sort(key=lambda x: int(x.get("doorId", 0)))
        update_table_with_page_data(table, root_instance)

    except Exception as e:
        messagebox.showerror("API Error", f"Failed to load doors:\n{e}")

    # --- Controls (Pagination + Refresh) ---
    control_frame = tk.Frame(root_instance, bg=BG_COLOR)
    control_frame.pack(pady=10)

    prev_btn = ttk.Button(control_frame, text="⬅ Prev", command=lambda: change_page(-1, table, root_instance))
    next_btn = ttk.Button(control_frame, text="Next ➡", command=lambda: change_page(1, table, root_instance))
    refresh_btn = ttk.Button(control_frame, text="🔄 Refresh", command=lambda: refresh_data(root_instance))

    prev_btn.grid(row=0, column=0, padx=5)
    next_btn.grid(row=0, column=2, padx=5)
    refresh_btn.grid(row=0, column=3, padx=15)

    page_label = tk.Label(control_frame, text="", bg=BG_COLOR, fg=PRIMARY_COLOR, font=("Segoe UI", 10, "bold"))
    page_label.grid(row=0, column=1, padx=10)
    update_page_label(page_label)

# --- Helper Functions ---
def update_table_with_page_data(table, root_instance):
    global current_page, door_cache
    table.delete(*table.get_children())

    start = (current_page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_data = door_cache[start:end]

    for idx, door in enumerate(page_data):
        tag = "evenrow" if idx % 2 == 0 else "oddrow"
        status = "Online" if str(door.get("status", "1")) == "1" else "Offline"
        table.insert("", "end", values=(
            door.get("doorId", ""),
            door.get("doorName", ""),
            door.get("deviceName", ""),
            status,
            door.get("description", "")
        ), tags=(tag,))

def update_page_label(label):
    global current_page, door_cache
    total_pages = max(1, (len(door_cache) + PAGE_SIZE - 1) // PAGE_SIZE)
    label.config(text=f"Page {current_page} of {total_pages}")

def change_page(direction, table, root_instance):
    global current_page, door_cache
    total_pages = max(1, (len(door_cache) + PAGE_SIZE - 1) // PAGE_SIZE)
    new_page = current_page + direction
    if 1 <= new_page <= total_pages:
        current_page = new_page
        update_table_with_page_data(table, root_instance)
        for widget in root_instance.winfo_children():
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label) and "Page" in child.cget("text"):
                        update_page_label(child)
    else:
        messagebox.showinfo("Pagination", "No more pages.")

def refresh_data(root_instance):
    global current_page, door_cache
    door_cache = []
    current_page = 1
    show_door_list(root_instance)
