import tkinter as tk
from tkinter import ttk, messagebox
from Api.Common_signature import common_signature_api

# ---------------- COLORS ----------------
HEADER_BG = "#F3F4F6"
HEADER_FG = "#4B5563"
ROW_ODD = "#FFFFFF"
ROW_EVEN = "#F9FAFB"
BORDER_COLOR = "#E5E7EB"
TEXT_DARK = "#111827"

def modern_treeview_style():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Modern.Treeview.Heading",
        background=HEADER_BG,
        foreground=HEADER_FG,
        font=("Segoe UI", 10, "bold"),
        padding=10,
        relief="flat",
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

    style.map("Modern.Treeview.Heading",
              background=[("active", HEADER_BG)])


# ------------------- MAIN DOOR LIST --------------------
def show_door_list(parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    parent_frame.configure(bg="white")
    modern_treeview_style()

    # 🔵 Title
    tk.Label(
        parent_frame,
        text="🚪 Door Device List",
        font=("Segoe UI", 18, "bold"),
        bg="white",
        fg=TEXT_DARK,
        anchor="w"
    ).pack(fill="x", padx=20, pady=(10, 5))

    # -------------- TABLE --------------
    table_frame = tk.Frame(parent_frame, bg="white")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = ("id", "name", "ip", "port", "status", "protocol")

    tree = ttk.Treeview(
        table_frame,
        columns=cols,
        show="headings",
        style="Modern.Treeview"
    )
    tree.pack(fill="both", expand=True, side="left")

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # --- Column Headings ---
    headings = {
        "id": "Device ID",
        "name": "Device Name",
        "ip": "IP Address",
        "port": "Port",
        "status": "Status",
        "protocol": "Protocol"
    }

    for key, text in headings.items():
        tree.heading(key, text=text)
        tree.column(key, anchor="center", width=160)

    # Row color style
    tree.tag_configure("odd", background=ROW_ODD)
    tree.tag_configure("even", background=ROW_EVEN)

    # -------------- Refresh Button --------------
    ttk.Button(
        parent_frame,
        text="🔄 Refresh",
        command=lambda: show_door_list(parent_frame)
    ).pack(pady=5)

    # ------------ API CALL ------------
    api_path = "/artemis/api/resource/v1/acsDevice/acsDeviceList"
    payload = {"pageNo": 1, "pageSize": 200}

    res = common_signature_api.call_api(api_path, payload)

    if not res:
        messagebox.showerror("Error", "No response from Hikvision API.")
        return

    if res.get("code") != "0":
        messagebox.showerror("API Error", res.get("msg", "Unknown error"))
        return

    devices = res.get("data", {}).get("list", [])

    # -------------- Insert Rows --------------
    for i, dev in enumerate(devices):
        status_code = dev.get("status", -1)

        if status_code == 1:
            status_text = "🟢 Online"
        elif status_code == 0:
            status_text = "🔴 Offline"
        else:
            status_text = "⚪ Unknown"

        tree.insert(
            "",
            "end",
            values=(
                dev.get("acsDevIndexCode", "-"),
                dev.get("acsDevName", "-"),
                dev.get("acsDevIp", "-"),
                dev.get("acsDevPort", "-"),
                status_text,
                dev.get("treatyType", "-")
            ),
            tags=("odd" if i % 2 == 0 else "even",)
        )
