import tkinter as tk
from tkinter import ttk, messagebox
from Api.Common_signature import common_signature_api

# Colors
BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"

def show_linked_doors(content_frame):
    """Fetch and display linked doors using HikCentral APIs with fallback."""
    for w in content_frame.winfo_children():
        w.destroy()

    frame = tk.Frame(content_frame, bg=BG_COLOR)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="🔗 Linked Doors", font=("Segoe UI", 16, "bold"),
             bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

    columns = ("Door ID", "Door Name", "Linked Device", "Status", "Out State")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, width=160, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    status_map = {
        0: "🔴 Closed",
        1: "🟢 Open",
        2: "⚪ Unknown",
        3: "🟡 Fault",
        4: "🔒 Locked",
        -1: "❔ N/A"
    }

    # Candidate endpoints in order of preference
    endpoints = [
        "/artemis/api/resource/v1/acsDoor/advance/acsDoorList",
        "/artemis/api/resource/v1/acsDoor/acsDoorList",
        "/artemis/api/resource/v1/acsDoor/advance/acsDoorList"  # duplicate safe fallback
    ]

    # Clean payloads: try without regionIndexCode; some endpoints accept additional filters but not required
    payloads = [
        {"pageNo": 1, "pageSize": 100},
        # Some implementations accept 'pageNo' & 'pageSize' only — keep this list for easy extension.
    ]

    def fetch_doors():
        tree.delete(*tree.get_children())

        last_error = None
        success_res = None
        used_endpoint = None

        # Try each endpoint with each payload
        for ep in endpoints:
            for payload in payloads:
                try:
                    print(f"DEBUG: Trying endpoint {ep} with payload {payload}")
                    res = common_signature_api.call_api(ep, payload)
                    print("DEBUG: Response:", res)

                    # If empty res, treat as failure and continue
                    if not res:
                        last_error = "No response from API"
                        continue

                    # If API returned success code -> use it
                    if str(res.get("code", "")).strip() == "0":
                        success_res = res
                        used_endpoint = ep
                        break

                    # If API complained about regionIndexCode specifically, record message and continue trying other endpoints
                    msg = str(res.get("msg", "")).lower()
                    if "regionindexcode" in msg or "regionindex" in msg or "regionindexcode parameter" in msg:
                        last_error = f"Server rejected request: {res.get('msg')}"
                        # continue trying other endpoints/payloads
                        continue

                    # For any other error message, record and continue trying
                    last_error = f"API returned error: {res.get('msg', 'Unknown')}"
                except Exception as e:
                    print("DEBUG: Exception calling API:", e)
                    last_error = str(e)

            if success_res:
                break

        # If we never got success, show the last error
        if not success_res:
            messagebox.showerror("API Error", last_error or "Failed to fetch doors")
            return

        # Populate tree from successful response
        data_list = success_res.get("data", {}).get("list", [])
        if not data_list:
            messagebox.showinfo("Info", "No linked doors found.")
            return

        for door in data_list:
            door_id = door.get("doorIndexCode", door.get("doorIndex", "-"))
            door_name = door.get("doorName", "-")
            linked_device = door.get("acsDevIndexCode", door.get("acsDevIndex", "-"))
            door_state = door.get("doorState", -1)
            out_state = door.get("doorOutState", -1)

            tree.insert("", "end", values=(
                door_id,
                door_name,
                linked_device,
                status_map.get(door_state, "❔ Unknown"),
                status_map.get(out_state, "❔ Unknown")
            ))

    ttk.Button(frame, text="🔄 Refresh", command=fetch_doors).pack(pady=8)

    # initial load
    fetch_doors()
