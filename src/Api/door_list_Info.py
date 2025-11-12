import tkinter as tk
from tkinter import ttk, messagebox
from Api import common_signature_api

# 🎨 Colors
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"

def show_door_list(parent_frame):
    """Fetch and display Access Control Devices."""
    for widget in parent_frame.winfo_children():
        widget.destroy()

    frame = tk.Frame(parent_frame, bg=BG_COLOR)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    # 🔹 Title
    tk.Label(
        frame,
        text="🚪 Door Device List",
        font=("Segoe UI", 16, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack(pady=10)

    # 🔹 Device Table
    columns = ("acsDevIndexCode", "acsDevName", "acsDevIp", "acsDevPort", "status", "treatyType")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
    tree.pack(fill="x", padx=20, pady=10)

    for col in columns:
        tree.heading(col, text=col.replace("acsDevIndexCode", "Device ID")
                                   .replace("acsDevName", "Device Name")
                                   .replace("acsDevIp", "IP Address")
                                   .replace("acsDevPort", "Port")
                                   .replace("status", "Status")
                                   .replace("treatyType", "Protocol"))
        tree.column(col, anchor="center", width=160)

    # 🔹 Scrollbar
    scrollbar_device = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar_device.set)
    scrollbar_device.pack(side="right", fill="y")

    # 🔹 Refresh Button
    ttk.Button(frame, text="🔄 Refresh", command=lambda: show_door_list(parent_frame)).pack(pady=5)

    # 🛰️ Fetch Device Data
    api_path = "/artemis/api/resource/v1/acsDevice/acsDeviceList"
    payload = {"pageNo": 1, "pageSize": 50}

    res = common_signature_api.call_api(api_path, payload)
    print("DEBUG Device List:", res)

    if not res:
        messagebox.showerror("Error", "No response from Hikvision API.")
        return

    if res.get("code") == "0":
        devices = res.get("data", {}).get("list", [])
        if not devices:
            messagebox.showinfo("Info", "No devices found.")
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
        messagebox.showerror("API Error", res.get("msg", "Unknown Error"))
