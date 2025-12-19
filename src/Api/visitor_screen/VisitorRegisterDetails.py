import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta

# Try to import your API handler
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None
    print("⚠️ Warning: api_handler not found. Make sure the 'Api' folder is in the same directory.")

# --- CONFIG ---
BG_COLOR = "#F4F6F7"
HEADER_TEXT = "#2C3E50"
API_REGISTER_RECORD = "/artemis/api/visitor/v1/register/getVistorRegisterRecord"

def render_register_details(parent):
    """
    Renders the Visitor Register Details tab inside the parent frame.
    """
    frame = tk.Frame(parent, bg=BG_COLOR, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    # Title
    tk.Label(frame, text="Visitor Registration Records", font=("Segoe UI", 16, "bold"), 
             bg=BG_COLOR, fg=HEADER_TEXT).pack(anchor="w", pady=(0, 10))

    # --- Search Controls ---
    controls = tk.Frame(frame, bg=BG_COLOR)
    controls.pack(fill="x", pady=10)

    # Date Logic (Default: Last 30 days)
    now = datetime.now()
    start_default = now - timedelta(days=30)
    
    # Start Date
    tk.Label(controls, text="Start Date:", bg=BG_COLOR).pack(side="left", padx=5)
    start_entry = DateEntry(controls, width=12, background='darkblue', foreground='white', borderwidth=2, year=start_default.year, month=start_default.month, day=start_default.day)
    start_entry.pack(side="left", padx=5)

    # End Date
    tk.Label(controls, text="End Date:", bg=BG_COLOR).pack(side="left", padx=5)
    end_entry = DateEntry(controls, width=12, background='darkblue', foreground='white', borderwidth=2)
    end_entry.pack(side="left", padx=5)

    # --- Table Setup ---
    columns = ("recordId", "visitorName", "status", "regTime")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True, pady=10)

    # Columns
    tree.heading("recordId", text="Record ID")
    tree.column("recordId", width=120)
    tree.heading("visitorName", text="Visitor Name")
    tree.column("visitorName", width=150)
    tree.heading("status", text="Status")
    tree.column("status", width=80)
    tree.heading("regTime", text="Register Time")
    tree.column("regTime", width=150)

    def fetch_records():
        # Clear table
        for item in tree.get_children():
            tree.delete(item)

        # Format dates for API (ISO 8601 format)
        s_date = start_entry.get_date().strftime("%Y-%m-%dT00:00:00+05:30")
        e_date = end_entry.get_date().strftime("%Y-%m-%dT23:59:59+05:30")

        payload = {
            "pageNo": 1,
            "pageSize": 50,
            "visitStartTime": s_date,
            "visitEndTime": e_date,
            "sortField": "visitingTime",
            "orderType": "0"
        }

        if api_handler:
            res = api_handler.call_api(API_REGISTER_RECORD, payload)
            if res and res.get("code") == "0":
                data = res.get("data", {})
                rows = data.get("list", [])
                
                if not rows:
                    messagebox.showinfo("Result", "No records found for this date range.")
                    return

                for r in rows:
                    rec_id = r.get("recordId", "-")
                    v_name = r.get("visitorName", "N/A") 
                    v_status = r.get("visitorStatus", "-")
                    reg_time = r.get("registerTime", "-")
                    
                    tree.insert("", "end", values=(rec_id, v_name, v_status, reg_time))
            else:
                 msg = res.get("msg") if res else "Unknown Error"
                 messagebox.showerror("API Error", msg)
        else:
            messagebox.showerror("Error", "API Handler not connected.")

    # Search Button
    tk.Button(controls, text="Search Records", command=fetch_records, bg="#3498DB", fg="white", font=("Segoe UI", 9, "bold")).pack(side="left", padx=15)

# Self-test block
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    render_register_details(root)
    root.mainloop()