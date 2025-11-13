import tkinter as tk
from tkinter import ttk

BG_COLOR = "#D6EAF8"
CARD_BG = "white"
CARD_BORDER = "#D5D8DC"
TEXT_DARK = "#2C3E50"
PRIMARY = "#0A74FF"


def show_homepage(parent):
    """Render the full home page inside content_frame"""

    # Clear previous page
    for w in parent.winfo_children():
        w.destroy()

    # Main container
    container = tk.Frame(parent, bg=BG_COLOR)
    container.pack(fill="both", expand=True)

    # ----------- HEADER (Simple Like Screenshot Top Info Bar) -----------
    header = tk.Frame(container, bg="white", padx=20, pady=10)
    header.pack(fill="x")

    tk.Label(
        header, text="Visitor Management System", font=("Segoe UI", 18, "bold"),
        fg=TEXT_DARK, bg="white"
    ).pack(side="left")

    tk.Label(
        header, text="Business Date: 06-07-2023", font=("Segoe UI", 10),
        fg="#444", bg="white"
    ).pack(side="right", padx=20)

    # ----------- ACTION BUTTON (New Visitor) -----------
    action_area = tk.Frame(container, bg=BG_COLOR)
    action_area.pack(fill="x", pady=(10, 5), padx=30)

    new_btn = tk.Button(
        action_area, text="  ➕  New Visitor Entry  ",
        bg=PRIMARY, fg="white", relief="flat",
        font=("Segoe UI", 12, "bold"), pady=7, padx=10
    )
    new_btn.pack(side="left")

    # ----------- SEARCH BAR -----------
    search_area = tk.Frame(container, bg=BG_COLOR)
    search_area.pack(fill="x", pady=10, padx=30)

    search_entry = tk.Entry(search_area, font=("Segoe UI", 12), bd=0)
    search_entry.pack(side="left", fill="x", expand=True, ipady=7)

    tk.Button(
        search_area, text="🔍", font=("Segoe UI", 12),
        bg=PRIMARY, fg="white", relief="flat", padx=15
    ).pack(side="left", padx=(10, 0))

    # ----------- TABLE AREA -----------
    table_frame = tk.Frame(container, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=30, pady=10)

    cols = ("visitor_id", "name", "purpose", "door", "status")

    tree = ttk.Treeview(
        table_frame,
        columns=cols,
        show="headings",
        height=15
    )

    # Headings
    tree.heading("visitor_id", text="Visitor ID")
    tree.heading("name", text="Name")
    tree.heading("purpose", text="Purpose")
    tree.heading("door", text="Door")
    tree.heading("status", text="Status")

    # Column widths
    tree.column("visitor_id", width=140)
    tree.column("name", width=160)
    tree.column("purpose", width=200)
    tree.column("door", width=100)
    tree.column("status", width=120)

    # Dummy data
    sample = [
        ("VIS123", "Arun Kumar", "Meeting", "Door-1", "Approved"),
        ("VIS124", "Priya Devi", "Interview", "Door-2", "Processing"),
        ("VIS125", "Dinesh", "Delivery", "Door-1", "Rejected"),
    ]

    for row in sample:
        tree.insert("", "end", values=row)

    # Scrollbar
    scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
