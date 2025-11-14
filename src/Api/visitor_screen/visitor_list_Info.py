import tkinter as tk
from tkinter import ttk, messagebox

from Api.Common_signature.common_signature_api import get_visitor_list

# ---------------- COLORS ----------------
HEADER_BG = "#F3F4F6"
HEADER_FG = "#4B5563"
ROW_ODD = "#FFFFFF"
ROW_EVEN = "#F9FAFB"
BORDER_COLOR = "#E5E7EB"
TEXT_DARK = "#111827"

PAGE_SIZE = 16

visitors_cache = []
filtered_cache = []
current_page = 1
table = None
pagination_frame = None


# ----------------------------------------------------
# Modern Table Style
# ----------------------------------------------------
def modern_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Modern.Treeview.Heading",
        background=HEADER_BG,
        foreground=HEADER_FG,
        font=("Segoe UI", 10, "bold"),
        padding=10,
        relief="flat"
    )

    style.configure(
        "Modern.Treeview",
        background="white",
        foreground=TEXT_DARK,
        rowheight=32,
        fieldbackground="white",
        bordercolor=BORDER_COLOR,
        bordersize=1,
        font=("Segoe UI", 10)
    )


# ----------------------------------------------------
# Main Screen
# ----------------------------------------------------
def show_single_visitor_list(root):
    global table, pagination_frame, visitors_cache, filtered_cache, current_page

    for w in root.winfo_children():
        w.destroy()

    root.configure(bg="white")
    modern_treeview_style()

    # Title
    tk.Label(
        root, text="Visitor List",
        font=("Segoe UI", 18, "bold"),
        bg="white", fg=TEXT_DARK,
        anchor="w"
    ).pack(fill="x", padx=20, pady=(10, 5))

    # ---------------- SEARCH BAR ----------------
    search_frame = tk.Frame(root, bg="white")
    search_frame.pack(fill="x", padx=20, pady=(0, 10))

    search_var = tk.StringVar()

    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40)
    search_entry.pack(side="left", padx=(0, 10), ipady=5)

    ttk.Button(search_frame, text="Search",
               command=lambda: apply_search(search_var.get())
               ).pack(side="left")

    ttk.Button(search_frame, text="Clear",
               command=lambda: clear_search(search_var)
               ).pack(side="left", padx=5)

    # ---------------- TABLE ----------------
    table_frame = tk.Frame(root, bg="white")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    yscroll = ttk.Scrollbar(table_frame, orient="vertical")
    xscroll = ttk.Scrollbar(table_frame, orient="horizontal")

    cols = ("visitorId", "visitorFullName", "companyName", "phoneNo", "gender", "remark")

    global table
    table = ttk.Treeview(
        table_frame,
        style="Modern.Treeview",
        columns=cols,
        show="headings",
        yscrollcommand=yscroll.set,
        xscrollcommand=xscroll.set
    )

    yscroll.config(command=table.yview)
    xscroll.config(command=table.xview)
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    # Headers
    headers = [
        ("visitorId", "Visitor ID"),
        ("visitorFullName", "Name"),
        ("companyName", "Company"),
        ("phoneNo", "Phone No"),
        ("gender", "Gender"),
        ("remark", "Remark"),
    ]

    for c, t in headers:
        table.heading(c, text=t)
        table.column(c, anchor="w", width=180)

    table.tag_configure("odd", background=ROW_ODD)
    table.tag_configure("even", background=ROW_EVEN)

    # Load data
    try:
        visitors_cache = get_visitor_list()
        filtered_cache = visitors_cache.copy()
        current_page = 1
        fill_table()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visitor list:\n{e}")

    # ---------------- PAGINATION ----------------
    global pagination_frame
    pagination_frame = tk.Frame(root, bg="white")
    pagination_frame.pack(pady=15)

    render_pagination()


# ----------------------------------------------------
# Fill Table Rows
# ----------------------------------------------------
def fill_table():
    table.delete(*table.get_children())

    start = (current_page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE

    rows = filtered_cache[start:end]

    for i, v in enumerate(rows):
        gender = "Male" if v.get("gender") == 1 else "Female"
        table.insert(
            "",
            "end",
            values=(
                v.get("visitorId"),
                v.get("visitorFullName"),
                v.get("companyName"),
                v.get("phoneNo"),
                gender,
                v.get("remark")
            ),
            tags=("odd" if i % 2 == 0 else "even",)
        )


# ----------------------------------------------------
# Search
# ----------------------------------------------------
def apply_search(text):
    global filtered_cache, current_page
    text = text.lower().strip()

    if not text:
        filtered_cache = visitors_cache.copy()
    else:
        filtered_cache = [
            v for v in visitors_cache
            if text in str(v).lower()
        ]

    current_page = 1
    fill_table()
    render_pagination()


def clear_search(var):
    var.set("")
    apply_search("")


# ----------------------------------------------------
# Pagination Buttons
# ----------------------------------------------------
def render_pagination():
    for w in pagination_frame.winfo_children():
        w.destroy()

    total_pages = max(1, (len(filtered_cache) + PAGE_SIZE - 1) // PAGE_SIZE)

    # ---------- BUTTON STYLE ----------
    def page_btn(txt, active=False, cmd=None):
        bg = "#FFFFFF" if not active else TEXT_DARK
        fg = TEXT_DARK if not active else "white"
        font = ("Segoe UI", 10, "bold" if active else "normal")

        btn = tk.Button(
            pagination_frame, text=txt, command=cmd,
            bg=bg, fg=fg, font=font,
            relief="solid", borderwidth=1,
            width=3, height=1,
            cursor="hand2", highlightthickness=0
        )
        btn.pack(side="left", padx=4)
        return btn

    # ---------- PREVIOUS ----------
    page_btn("◀", False,
             lambda: change_page(-1) if current_page > 1 else None)

    # ---------- PAGE NUMBERS ----------
    display = []

    if total_pages <= 7:
        display = list(range(1, total_pages + 1))

    else:
        display.append(1)

        if current_page > 3:
            display.append("...")

        start = max(2, current_page - 1)
        end = min(total_pages - 1, current_page + 1)
        display.extend(range(start, end + 1))

        if current_page < total_pages - 2:
            display.append("...")

        display.append(total_pages)

    for p in display:
        if p == "...":
            tk.Label(pagination_frame, text="...", bg="white",
                     font=("Segoe UI", 10)).pack(side="left", padx=3)
        else:
            page_btn(str(p), p == current_page,
                     lambda pp=p: goto_page(pp))

    # ---------- NEXT ----------
    page_btn("▶", False,
             lambda: change_page(1) if current_page < total_pages else None)


def change_page(step):
    global current_page
    current_page += step
    fill_table()
    render_pagination()


def goto_page(num):
    global current_page
    current_page = num
    fill_table()
    render_pagination()
