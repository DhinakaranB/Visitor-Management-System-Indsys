import tkinter as tk
from tkinter import ttk, messagebox
from common_api import get_visitor_list

# --- UI Style Constants ---
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
HEADER_FONT = ("Segoe UI", 16, "bold")
CELL_FONT = ("Segoe UI", 10)

def show_single_visitor_list(root_instance):
    """Display all visitor records in a scrollable grid."""
    for widget in root_instance.winfo_children():
        widget.destroy()

    tk.Label(
        root_instance,
        text="👥 Visitor List",
        font=HEADER_FONT,
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=(15, 5))

    frame = tk.Frame(root_instance, bg=BG_COLOR)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Scrollbars
    yscroll = ttk.Scrollbar(frame, orient="vertical")
    xscroll = ttk.Scrollbar(frame, orient="horizontal")

    columns = ("visitorId", "visitorFullName", "companyName", "phoneNo", "gender", "remark")
    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        yscrollcommand=yscroll.set,
        xscrollcommand=xscroll.set
    )

    yscroll.config(command=table.yview)
    xscroll.config(command=table.xview)
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    # Define headings
    table.heading("visitorId", text="Visitor ID")
    table.heading("visitorFullName", text="Name")
    table.heading("companyName", text="Company")
    table.heading("phoneNo", text="Phone No")
    table.heading("gender", text="Gender")
    table.heading("remark", text="Remark")

    # Column width & alignment
    table.column("visitorId", width=80, anchor="center")
    table.column("visitorFullName", width=150, anchor="center")
    table.column("companyName", width=150, anchor="center")
    table.column("phoneNo", width=120, anchor="center")
    table.column("gender", width=100, anchor="center")
    table.column("remark", width=200, anchor="w")

    # Style
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#EAF2F8", foreground=TEXT_COLOR)
    style.configure("Treeview", rowheight=25, font=CELL_FONT)
    style.map("Treeview", background=[("selected", "#D6EAF8")])

    # Load visitor data
    try:
        visitor_data = get_visitor_list()
        print("DEBUG visitors:", visitor_data)

        if not visitor_data:
            tk.Label(
                root_instance,
                text="No visitors found.",
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI", 12)
            ).pack(pady=15)
            return

        gender_map = {0: "Undefined", 1: "Male", 2: "Female"}

        for v in visitor_data:
            try:
                table.insert("", "end", values=(
                    v.get("visitorId", ""),
                    v.get("visitorFullName", ""),
                    v.get("companyName", ""),
                    v.get("phoneNo", ""),
                    gender_map.get(v.get("gender", 0), "Unknown"),
                    v.get("remark", "")
                ))
            except Exception as err:
                print(f"⚠ Error inserting visitor row: {err}, data={v}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visitors:\n{e}")

    # Refresh Button
    ttk.Button(
        root_instance,
        text="🔄 Refresh",
        command=lambda: show_single_visitor_list(root_instance),
        style="TInfo.TButton"
    ).pack(pady=10)
import tkinter as tk
from tkinter import ttk, messagebox
from common_api import get_visitor_list

# --- UI Style Constants ---
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"
HEADER_FONT = ("Segoe UI", 16, "bold")
CELL_FONT = ("Segoe UI", 10)

def show_single_visitor_list(root_instance):
    """Display all visitor records in a scrollable grid."""
    for widget in root_instance.winfo_children():
        widget.destroy()

    tk.Label(
        root_instance,
        text="👥 Visitor List",
        font=HEADER_FONT,
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=(15, 5))

    frame = tk.Frame(root_instance, bg=BG_COLOR)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Scrollbars
    yscroll = ttk.Scrollbar(frame, orient="vertical")
    xscroll = ttk.Scrollbar(frame, orient="horizontal")

    columns = ("visitorId", "visitorFullName", "companyName", "phoneNo", "gender", "remark")
    table = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        yscrollcommand=yscroll.set,
        xscrollcommand=xscroll.set
    )

    yscroll.config(command=table.yview)
    xscroll.config(command=table.xview)
    yscroll.pack(side="right", fill="y")
    xscroll.pack(side="bottom", fill="x")
    table.pack(fill="both", expand=True)

    # Define headings
    table.heading("visitorId", text="Visitor ID")
    table.heading("visitorFullName", text="Name")
    table.heading("companyName", text="Company")
    table.heading("phoneNo", text="Phone No")
    table.heading("gender", text="Gender")
    table.heading("remark", text="Remark")

    # Column width & alignment
    table.column("visitorId", width=80, anchor="center")
    table.column("visitorFullName", width=150, anchor="center")
    table.column("companyName", width=150, anchor="center")
    table.column("phoneNo", width=120, anchor="center")
    table.column("gender", width=100, anchor="center")
    table.column("remark", width=200, anchor="w")

    # Style
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#EAF2F8", foreground=TEXT_COLOR)
    style.configure("Treeview", rowheight=25, font=CELL_FONT)
    style.map("Treeview", background=[("selected", "#D6EAF8")])

    # Load visitor data
    try:
        visitor_data = get_visitor_list()
        print("DEBUG visitors:", visitor_data)

        if not visitor_data:
            tk.Label(
                root_instance,
                text="No visitors found.",
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI", 12)
            ).pack(pady=15)
            return

        gender_map = {0: "Undefined", 1: "Male", 2: "Female"}

        for v in visitor_data:
            try:
                table.insert("", "end", values=(
                    v.get("visitorId", ""),
                    v.get("visitorFullName", ""),
                    v.get("companyName", ""),
                    v.get("phoneNo", ""),
                    gender_map.get(v.get("gender", 0), "Unknown"),
                    v.get("remark", "")
                ))
            except Exception as err:
                print(f"⚠ Error inserting visitor row: {err}, data={v}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load visitors:\n{e}")

    # Refresh Button
    ttk.Button(
        root_instance,
        text="🔄 Refresh",
        command=lambda: show_single_visitor_list(root_instance),
        style="TInfo.TButton"
    ).pack(pady=10)
