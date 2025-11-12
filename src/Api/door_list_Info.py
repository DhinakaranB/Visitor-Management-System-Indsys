import tkinter as tk
from tkinter import ttk, messagebox
from Api import common_signature_api

# 🎨 Colors
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"

def show_door_list(parent_frame):
    """Fetch and display Access Control Device List from Hikvision"""
    for widget in parent_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent_frame, bg=BG_COLOR)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(
        frame,
        text="🚪 Door Device List",
        font=("Segoe UI", 16, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=10)

    columns = (
        "acsDevIndexCode",
        "acsDevName",
        "acsDevIp",
        "acsDevPort",
        "status",
        "treatyType",
    )
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=20)
    tree.pack(fill="both", expand=True, pady=10)

    # Headings
    tree.heading("acsDevIndexCode", text="Device ID")
    tree.heading("acsDevName", text="Device Name")
    tree.heading("acsDevIp", text="IP Address")
    tree.heading("acsDevPort", text="Port")
    tree.heading("status", text="Status")
    tree.heading("treatyType", text="Protocol Type")

    # Column width
    tree.column("acsDevIndexCode", width=150, anchor="center")
    tree.column("acsDevName", width=200, anchor="center")
    tree.column("acsDevIp", width=150, anchor="center")
    tree.column("acsDevPort", width=100, anchor="center")
    tree.column("status", width=120, anchor="center")
    tree.column("treatyType", width=150, anchor="center")

    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Refresh button
    ttk.Button(frame, text="🔄 Refresh", command=lambda: show_door_list(parent_frame)).pack(pady=5)

    # Fetch API
    api_path = "/artemis/api/resource/v1/acsDevice/acsDeviceList"
    payload = {"pageNo": 1, "pageSize": 50}

    res = common_signature_api.call_api(api_path, payload)
    print("DEBUG Raw Response:", res)  # Keep for debugging

    if not res:
        messagebox.showerror("Error", "No response from Hikvision API.")
        return

    if res.get("code") == "0":
        data = res.get("data", {})
        devices = data.get("list", [])

        if not devices:
            messagebox.showinfo("Info", "No Access Control Devices found.")
            return

        for dev in devices:
            status_value = dev.get("status", -1)
            if status_value == 1:
                status_text = "🟢 Online"
            elif status_value == 0:
                status_text = "🔴 Offline"
            elif status_value == 2:
                status_text = "⚪ Unknown"
            else:
                status_text = "❔ N/A"

            tree.insert("", "end", values=(
                dev.get("acsDevIndexCode", "-"),
                dev.get("acsDevName", "-"),
                dev.get("acsDevIp", "-"),
                dev.get("acsDevPort", "-"),
                status_text,
                dev.get("treatyType", "-")
            ))
    else:
        messagebox.showerror("API Error", f"Code: {res.get('code')}\nMessage: {res.get('msg')}")
