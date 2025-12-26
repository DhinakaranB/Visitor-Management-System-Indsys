import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta

# Try to import your API handler
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None

# --- CONFIG & COLORS ---
BG_COLOR = "#F4F6F7"       
HEADER_BG = "#E0E0E0"      
HEADER_TEXT = "#2C3E50"    
BTN_COLOR = "#2980B9"      
BTN_TEXT = "white"

API_REGISTER_RECORD = "/artemis/api/visitor/v1/register/getVistorRegisterRecord"

# --- STATUS MAPPING ---
def get_status_text(status_code):
    """Maps the API status code to a readable string."""
    status_map = {
        "0": "Checked In",
        "1": "Checked Out",
        "2": "Auto Checked Out",
        "3": "Self-Service Out",
        "4": "Overstay / Not Checked Out"
    }
    # Handle comma-separated statuses if they occur (e.g. "1,2")
    if str(status_code) in status_map:
        return status_map[str(status_code)]
    return f"Status {status_code}"

class VisitorRegistrationScreen:
    def __init__(self, parent):
        self.parent = parent
        
        # Determine if parent is root or a frame
        if isinstance(parent, tk.Tk) or isinstance(parent, tk.Toplevel):
            parent.title("Visitor Management System")
            parent.geometry("1200x700") # Slightly wider for extra time column
            parent.configure(bg=BG_COLOR)
        else:
            parent.configure(bg=BG_COLOR)

        # --- STYLE CONFIGURATION ---
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Treeview Header Style
        self.style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background=HEADER_BG, 
                        foreground="black",
                        relief="flat")
        
        # Treeview Row Style
        self.style.configure("Treeview", 
                        font=("Segoe UI", 10), 
                        rowheight=28, 
                        background="white", 
                        fieldbackground="white")
        
        self.style.map("Treeview", background=[("selected", "#0078d7")])

        # --- 1. HEADER TITLE ---
        header_frame = tk.Frame(parent, bg=BG_COLOR, pady=10, padx=20)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Visitor Registration Records", 
                 font=("Segoe UI", 18, "bold"), 
                 bg=BG_COLOR, fg="#003366").pack(anchor="w")

        # --- 2. FILTER BAR ---
        filter_frame = tk.Frame(parent, bg=BG_COLOR, padx=20, pady=5)
        filter_frame.pack(fill="x")

        # Start Date
        tk.Label(filter_frame, text="Start Date:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
        
        now = datetime.now()
        start_default = now - timedelta(days=30)
        
        self.start_entry = DateEntry(filter_frame, width=12, background='darkblue', 
                                     foreground='white', borderwidth=2, 
                                     year=start_default.year, month=start_default.month, day=start_default.day,
                                     date_pattern='mm/dd/yy')
        self.start_entry.pack(side="left", padx=(5, 15))

        # End Date
        tk.Label(filter_frame, text="End Date:", bg=BG_COLOR, font=("Segoe UI", 10)).pack(side="left")
        self.end_entry = DateEntry(filter_frame, width=12, background='darkblue', 
                                   foreground='white', borderwidth=2,
                                   date_pattern='mm/dd/yy')
        self.end_entry.pack(side="left", padx=(5, 15))

        # Search Button
        search_btn = tk.Button(filter_frame, text="Search Records", command=self.fetch_records,
                               bg=BTN_COLOR, fg=BTN_TEXT, font=("Segoe UI", 9, "bold"), 
                               padx=10, relief="flat", activebackground="#1A5276", activeforeground="white")
        search_btn.pack(side="left")

        # --- 3. DATA GRID ---
        table_frame = tk.Frame(parent, bg=BG_COLOR, padx=20, pady=10)
        table_frame.pack(fill="both", expand=True)

        # Updated Columns to match requirements
        columns = ("recordId", "visitorName", "status", "startTime", "endTime")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Column Config
        headers = [
            ("recordId", "Record ID", 220),
            ("visitorName", "Visitor Name", 180),
            ("status", "Status", 150),
            ("startTime", "Start Time", 180),
            ("endTime", "End Time", 180)
        ]

        for col, text, width in headers:
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, anchor="w")

        self.tree.tag_configure("odd", background="white")
        self.tree.tag_configure("even", background="#f2f2f2")

        # --- 4. FOOTER ---
        footer_frame = tk.Frame(parent, bg="#EAECEE", pady=8)
        footer_frame.pack(fill="x", side="bottom")
        
        tk.Label(footer_frame, text="© 2025 Indsys Holdings - All rights reserved.", 
                 font=("Segoe UI", 8), bg="#EAECEE", fg="#555").pack()

        # Initial Load
        self.fetch_records()

    def fetch_records(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        s_date = self.start_entry.get_date().strftime("%Y-%m-%dT00:00:00+05:30")
        e_date = self.end_entry.get_date().strftime("%Y-%m-%dT23:59:59+05:30")

        rows = []

        if api_handler:
            payload = {
                "pageNo": 1, "pageSize": 50,
                "visitStartTime": s_date, "visitEndTime": e_date,
                "sortField": "visitingTime", "orderType": "0"
            }
            try:
                res = api_handler.call_api(API_REGISTER_RECORD, payload)
                if res and res.get("code") == "0":
                    data = res.get("data", {})
                    rows = data.get("list", [])
                else:
                    print(f"API Error: {res.get('msg') if res else 'No response'}")
            except Exception as e:
                print(f"API Exception: {e}")
        else:
            # Mock Data (Simulating the structure you provided)
            base_id = 640814489989545984
            for i in range(20):
                rows.append({
                    "recordId": str(base_id + i),
                    "visitorStatus": str(i % 5), # Rotates 0-4
                    "visitorBaseInfo": {
                        "fullName": f"Visitor {i+1}",
                        "visitStartTime": f"2025-12-19T09:00:00+08:00",
                        "visitEndTime": f"2025-12-19T17:00:00+08:00",
                    }
                })

        if not rows:
            messagebox.showinfo("Info", "No records found.")
            return

        for index, r in enumerate(rows):
            # Parse nested info
            rec_id = r.get("recordId", "-")
            status_code = r.get("visitorStatus", "-")
            
            # Access the nested dictionary
            base_info = r.get("visitorBaseInfo") or {}
            
            name = base_info.get("fullName", "N/A")
            start_time = base_info.get("visitStartTime", "")
            end_time = base_info.get("visitEndTime", "")
            
            # Convert status code to text
            status_text = get_status_text(status_code)

            tag = "even" if index % 2 == 0 else "odd"
            
            self.tree.insert("", "end", values=(
                rec_id,
                name,
                status_text,
                start_time,
                end_time
            ), tags=(tag,))

# ---------------------------------------------------------
#  REQUIRED FUNCTION FOR Ui.py
# ---------------------------------------------------------
def render_register_details(parent):
    """
    Entry point called by Ui.py.
    """
    for widget in parent.winfo_children():
        widget.destroy()

    VisitorRegistrationScreen(parent)

# ---------------------------------------------------------
#  SELF-TEST BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    render_register_details(root)
    root.mainloop()