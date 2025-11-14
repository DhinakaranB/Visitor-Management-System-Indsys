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

    style.map("Modern.Treeview.Heading",
              background=[("active", HEADER_BG)])


# ---------------- LINKED DOOR PAGE ----------------
def show_linked_doors(content_frame):
    for widget in content_frame.winfo_children():
        widget.destroy()

    content_frame.configure(bg="white")
    modern_treeview_style()

    # 🔵 Title
    tk.Label(
        content_frame,
        text="🔗 Linked Doors",
        font=("Segoe UI", 18, "bold"),
        bg="white",
        fg=TEXT_DARK,
        anchor="w"
    ).pack(fill="x", padx=20, pady=(10, 5))

    # -------------- TABLE FRAME --------------
    table_frame = tk.Frame(content_frame, bg="white")
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    columns = ("doorID", "doorName", "linkedDevice", "status", "outState")

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        style="Modern.Treeview",
    )
    tree.pack(fill="both", expand=True, side="left")

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Table Headings
    headers = {
        "doorID": "Door ID",
        "doorName": "Door Name",
        "linkedDevice": "Linked Device",
        "status": "Status",
        "outState": "Out State"
    }

    for col, text in headers.items():
        tree.heading(col, text=text)
        tree.column(col, anchor="center", width=180)

    # Row color tag
    tree.tag_configure("odd", background=ROW_ODD)
    tree.tag_configure("even", background=ROW_EVEN)

    # Status emojis
    status_map = {
        0: "🔴 Closed",
        1: "🟢 Open",
        2: "⚪ Unknown",
        3: "🟡 Fault",
        4: "🔒 Locked",
        -1: "❔ N/A"
    }

    # ---------------- FETCH FUNCTION ----------------
    def fetch_linked_doors():
        tree.delete(*tree.get_children())

        endpoints = [
            "/artemis/api/resource/v1/acsDoor/advance/acsDoorList",
            "/artemis/api/resource/v1/acsDoor/acsDoorList"
        ]

        payload = {"pageNo": 1, "pageSize": 200}
        ok_res = None
        last_error = None

        # Try all available API endpoints
        for ep in endpoints:
            try:
                res = common_signature_api.call_api(ep, payload)
                print("DEBUG:", ep, res)

                if not res:
                    continue

                if str(res.get("code")) == "0":
                    ok_res = res
                    break
                else:
                    last_error = res.get("msg")
            except Exception as e:
                last_error = str(e)

        if not ok_res:
            messagebox.showerror("API Error", last_error or "Cannot fetch linked doors.")
            return

        door_list = ok_res.get("data", {}).get("list", [])

        if not door_list:
            messagebox.showinfo("Info", "No linked doors found.")
            return

        # Insert rows
        for i, door in enumerate(door_list):
            door_id = door.get("doorIndexCode", "-")
            name = door.get("doorName", "-")
            linked_device = door.get("acsDevIndexCode", "-")
            status = status_map.get(door.get("doorState", -1), "❔ Unknown")
            out_state = status_map.get(door.get("doorOutState", -1), "❔ Unknown")

            tree.insert(
                "",
                "end",
                values=(door_id, name, linked_device, status, out_state),
                tags=("odd" if i % 2 == 0 else "even",)
            )

    # Refresh Button
    ttk.Button(
        content_frame,
        text="🔄 Refresh",
        command=fetch_linked_doors
    ).pack(pady=10)

    # Load initially
    fetch_linked_doors()
