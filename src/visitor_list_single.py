import tkinter as tk
from tkinter import ttk, messagebox
from common_api import get_visitor_list

# --- Constants ---
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
HEADER_FONT = ("Segoe UI", 16, "bold")
CELL_FONT = ("Segoe UI", 10)
PAGE_SIZE = 20

# Pagination globals
current_page = 1
visitors_cache = []

def show_single_visitor_list(root_instance):
    global current_page, visitors_cache

    for widget in root_instance.winfo_children():
        widget.destroy()

    # --- Title ---
    tk.Label(
        root_instance,
        text="👥 Visitor List",
        font=HEADER_FONT,
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=(15, 10))

    # --- Table Frame ---
    table_frame = tk.Frame(root_instance, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=30, pady=10)

    yscroll = ttk.Scrollbar(table_frame, orient="vertical")
    xscroll = ttk.Scrollbar(table_frame, orient="horizontal")

    columns = ("visitorId", "visitorFullName", "companyName", "phoneNo", "gender", "remark")

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

    # --- Column Setup ---
    table.heading("visitorId", text="Visitor ID")
    table.heading("visitorFullName", text="Name")
    table.heading("companyName", text="Company")
    table.heading("phoneNo", text="Phone No")
    table.heading("gender", text="Gender")
    table.heading("remark", text="Remark")

    table.column("visitorId", width=90, anchor="center")
    table.column("visitorFullName", width=150, anchor="center")
    table.column("companyName", width=150, anchor="center")
    table.column("phoneNo", width=130, anchor="center")
    table.column("gender", width=100, anchor="center")
    table.column("remark", width=180, anchor="center")

    # --- Custom Table Styling ---
    style = ttk.Style()
    style.theme_use("clam")  # ✅ stable and modern
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
        font=("Segoe UI", 10, "bold"),
        bordercolor="#2980B9"
    )

    # --- Alternate Row Colors ---
    table.tag_configure("oddrow", background="#F8F9F9")
    table.tag_configure("evenrow", background="#EAF2F8")

    # --- Load Data ---
    try:
        if not visitors_cache:
            visitors_cache = get_visitor_list()
            visitors_cache.sort(key=lambda x: int(x.get("visitorId", 0)))

        if not visitors_cache:
            tk.Label(root_instance, text="No visitors found.", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=15)
            return

        update_table_with_page_data(table, root_instance)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visitors:\n{e}")

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
    global current_page, visitors_cache
    table.delete(*table.get_children())

    gender_map = {0: "Undefined", 1: "Male", 2: "Female"}
    start = (current_page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_data = visitors_cache[start:end]

    for idx, v in enumerate(page_data):
        tag = "evenrow" if idx % 2 == 0 else "oddrow"
        table.insert("", "end", values=(
            v.get("visitorId", ""),
            v.get("visitorFullName", ""),
            v.get("companyName", ""),
            v.get("phoneNo", ""),
            gender_map.get(v.get("gender", 0), "Unknown"),
            v.get("remark", "")
        ), tags=(tag,))

def update_page_label(label):
    global current_page, visitors_cache
    total_pages = max(1, (len(visitors_cache) + PAGE_SIZE - 1) // PAGE_SIZE)
    label.config(text=f"Page {current_page} of {total_pages}")

def change_page(direction, table, root_instance):
    global current_page, visitors_cache
    total_pages = max(1, (len(visitors_cache) + PAGE_SIZE - 1) // PAGE_SIZE)
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
    global current_page, visitors_cache
    visitors_cache = []
    current_page = 1
    show_single_visitor_list(root_instance)
