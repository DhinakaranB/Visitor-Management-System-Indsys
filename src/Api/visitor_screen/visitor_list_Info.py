import tkinter as tk
from tkinter import ttk, messagebox

from Api.Common_signature.common_signature_api import get_visitor_list
from Api.Homepage.Ui import show_home   # ✅ Correct main-menu function import

# ---------------- UI CONSTANTS ----------------
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
HEADER_FONT = ("Segoe UI", 16, "bold")
CELL_FONT = ("Segoe UI", 10)
PAGE_SIZE = 20

current_page = 1
visitors_cache = []


# ---------------- MAIN SCREEN ----------------
def show_single_visitor_list(root_instance):
    global current_page, visitors_cache

    for widget in root_instance.winfo_children():
        widget.destroy()

    # ---------- Title + Back Button ----------
    title_frame = tk.Frame(root_instance, bg=BG_COLOR)
    title_frame.pack(fill="x", pady=(10, 5), padx=10)

    tk.Label(title_frame, text="👥 Visitor List",
             font=HEADER_FONT, bg=BG_COLOR, fg=PRIMARY_COLOR).pack(side="left")

    # back_btn = ttk.Button(title_frame, text="⬅ Back to Main Menu",
    #                       command=show_home)     # ✅ Works directly
    # back_btn.pack(side="right")

    # ---------- Table Frame ----------
    table_frame = tk.Frame(root_instance, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=30, pady=10)

    yscroll = ttk.Scrollbar(table_frame, orient="vertical")
    xscroll = ttk.Scrollbar(table_frame, orient="horizontal")

    columns = ("visitorId", "visitorFullName", "companyName", "phoneNo", "gender", "remark")
    table = ttk.Treeview(table_frame, columns=columns, show="headings",
                         yscrollcommand=yscroll.set, xscrollcommand=xscroll.set,
                         style="Modern.Treeview")

    yscroll.config(command=table.yview)
    xscroll.config(command=table.xview)
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    for col, text in [
        ("visitorId", "Visitor ID"),
        ("visitorFullName", "Name"),
        ("companyName", "Company"),
        ("phoneNo", "Phone No"),
        ("gender", "Gender"),
        ("remark", "Remark")
    ]:
        table.heading(col, text=text)
        table.column(col, width=150, anchor="center")

    # Table Style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Modern.Treeview",
                    background="white", foreground=TEXT_COLOR,
                    rowheight=28, fieldbackground="white", font=CELL_FONT)
    style.configure("Modern.Treeview.Heading",
                    background=PRIMARY_COLOR, foreground="white",
                    font=("Segoe UI", 10, "bold"))

    table.tag_configure("oddrow", background="#F8F9F9")
    table.tag_configure("evenrow", background="#EAF2F8")

    try:
        if not visitors_cache:
            visitors_cache = get_visitor_list()
            visitors_cache.sort(key=lambda x: int(x.get("visitorId", 0)))

        if not visitors_cache:
            tk.Label(root_instance, text="No visitors found.", bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=15)
            return

        update_table_with_page_data(table)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visitors:\n{e}")

    # ---------- Refresh Button ----------
    refresh_btn = ttk.Button(root_instance, text="🔄 Refresh",
                             command=lambda: refresh_data(root_instance))
    refresh_btn.pack(pady=(5, 0))

    # ---------- Pagination Frame ----------
    pagination_frame = tk.Frame(root_instance, bg=BG_COLOR)
    pagination_frame.pack(pady=15)
    render_pagination(pagination_frame, table)


# ---------------- TABLE UPDATE ----------------
def update_table_with_page_data(table):
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


# ---------------- PAGE SWITCH ----------------
def set_page_and_render(page, table, frame):
    global current_page
    current_page = page
    update_table_with_page_data(table)
    render_pagination(frame, table)


def change_page_with_render(direction, table, frame):
    global current_page, visitors_cache
    total_pages = max(1, (len(visitors_cache) + PAGE_SIZE - 1) // PAGE_SIZE)
    new_page = current_page + direction

    if 1 <= new_page <= total_pages:
        current_page = new_page
        update_table_with_page_data(table)
        render_pagination(frame, table)


# ---------------- MODERN PAGINATION UI ----------------
def render_pagination(frame, table):
    global current_page, visitors_cache

    for widget in frame.winfo_children():
        widget.destroy()

    total_pages = max(1, (len(visitors_cache) + PAGE_SIZE - 1) // PAGE_SIZE)

    # Back button
    back_btn = tk.Button(frame, text="◀ Back", font=("Segoe UI", 10), padx=10,
                         state="normal" if current_page > 1 else "disabled",
                         command=lambda: change_page_with_render(-1, table, frame))
    back_btn.pack(side="left", padx=5)

    # Page numbers
    def add_page_button(page):
        btn_bg = "#000" if page == current_page else "#FFF"
        btn_fg = "#FFF" if page == current_page else "#000"

        btn = tk.Button(frame, text=str(page), width=3,
                        bg=btn_bg, fg=btn_fg, font=("Segoe UI", 10),
                        relief="solid", borderwidth=1,
                        command=lambda p=page: set_page_and_render(p, table, frame))
        btn.pack(side="left", padx=3)

    if total_pages <= 7:
        for p in range(1, total_pages + 1):
            add_page_button(p)

    else:
        if current_page <= 4:
            for p in range(1, 6):
                add_page_button(p)
            tk.Label(frame, text="...", bg=BG_COLOR).pack(side="left")
            add_page_button(total_pages)

        elif current_page >= total_pages - 3:
            add_page_button(1)
            tk.Label(frame, text="...", bg=BG_COLOR).pack(side="left")
            for p in range(total_pages - 4, total_pages + 1):
                add_page_button(p)

        else:
            add_page_button(1)
            tk.Label(frame, text="...", bg=BG_COLOR).pack(side="left")
            for p in range(current_page - 1, current_page + 2):
                add_page_button(p)
            tk.Label(frame, text="...", bg=BG_COLOR).pack(side="left")
            add_page_button(total_pages)

    # Next button
    next_btn = tk.Button(frame, text="Next ▶", font=("Segoe UI", 10), padx=10,
                         state="normal" if current_page < total_pages else "disabled",
                         command=lambda: change_page_with_render(1, table, frame))
    next_btn.pack(side="left", padx=5)


# ---------------- REFRESH LOGIC ----------------
def refresh_data(root_instance):
    global current_page, visitors_cache
    visitors_cache = []
    current_page = 1
    show_single_visitor_list(root_instance)
