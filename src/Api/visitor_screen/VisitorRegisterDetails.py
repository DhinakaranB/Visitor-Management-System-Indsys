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

class VisitorRegistrationScreen:
    def __init__(self, parent):
        self.parent = parent
        
        # Determine if parent is root or a frame to handle resizing gracefully
        # (We don't set geometry if it's just a frame inside a larger UI)
        if isinstance(parent, tk.Tk) or isinstance(parent, tk.Toplevel):
            parent.title("Visitor Management System")
            parent.geometry("1100x700")
            parent.configure(bg=BG_COLOR)
        else:
            # If it's a frame, ensure it has the background color
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
                        rowheight=25, 
                        background="white", 
                        fieldbackground="white")
        
        # Row Striping
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

        columns = ("recordId", "visitorName", "status", "regTime")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Column Config
        headers = [
            ("recordId", "Record ID", 250),
            ("visitorName", "Visitor Name", 200),
            ("status", "Status", 100),
            ("regTime", "Register Time", 200)
        ]

        for col, text, width in headers:
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, anchor="w")

        self.tree.tag_configure("odd", background="white")
        self.tree.tag_configure("even", background="#f2f2f2")

        # --- 4. FOOTER ---
        footer_frame = tk.Frame(parent, bg="#EAECEE", pady=8)
        footer_frame.pack(fill="x", side="bottom")
        
        # Initial Load
        self.fetch_records()

    def fetch_records(self):
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
            # Mock Data
            base_id = 640814489989545984
            for i in range(20):
                rows.append({
                    "recordId": str(base_id + i),
                    "visitorName": "N/A",
                    "visitorStatus": "2",
                    "registerTime": f"2025-11-04T{12+i%12}:58:00+05:30"
                })

        if not rows:
            messagebox.showinfo("Info", "No records found.")
            return

        for index, r in enumerate(rows):
            tag = "even" if index % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(
                r.get("recordId", "-"),
                r.get("visitorName", "N/A"),
                r.get("visitorStatus", "-"),
                r.get("registerTime", "-")
            ), tags=(tag,))


# ---------------------------------------------------------
#  REQUIRED FUNCTION FOR Ui.py
# ---------------------------------------------------------
def render_register_details(parent):
    """
    Entry point called by Ui.py.
    Clears the content frame and instantiates the screen class.
    """
    # 1. Clear existing widgets in the content frame
    for widget in parent.winfo_children():
        widget.destroy()

    # 2. Load the Visitor Registration Screen into the frame
    VisitorRegistrationScreen(parent)

# ---------------------------------------------------------
#  SELF-TEST BLOCK
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1100x700")
    render_register_details(root)
    root.mainloop()