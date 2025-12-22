import tkinter as tk
from tkinter import ttk
import json
import threading
from datetime import datetime

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# --- API ENDPOINT (User Provided) ---
# This is the endpoint that works for your version
API_VISITOR_INFO = "/artemis/api/visitor/v1/visitor/visitorInfo"

# --- COLORS ---
BG_MAIN = "#F3F4F6"      
BG_CARD = "#FFFFFF"      
TEXT_PRI = "#111827"     
TEXT_SEC = "#6B7280"     
COLOR_TOTAL = "#3B82F6" 
COLOR_IN = "#10B981"    
COLOR_OUT = "#6B7280"   

def call_api(url, payload):
    if not common_signature_api: return None
    try:
        if hasattr(common_signature_api, 'call_api'):
            return common_signature_api.call_api(url, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            return common_signature_api.send_to_api(url, payload)
        elif hasattr(common_signature_api, 'post'):
            return common_signature_api.post(url, payload)
    except Exception as e:
        print(f"API Error: {e}")
    return None

def fetch_dashboard_data(vars_dict, tree):
    if not common_signature_api: return

    # Payload based on your request
    # We fetch 100 to get a good sample for the counters
    payload = {
        "pageNo": 1, 
        "pageSize": 100
    }

    print(f"\n🔹 Requesting Visitor Info: {payload}")
    data = call_api(API_VISITOR_INFO, payload)
    
    # DEBUG: Print Raw Response to Console
    if isinstance(data, str): 
        try: data = json.loads(data)
        except: pass

    # Initialize Counters
    total_val = 0
    count_in = 0
    count_out = 0
    display_rows = []

    if data and isinstance(data, dict) and data.get("code") == "0":
        data_block = data.get("data", {})
        
        # 1. Total Count (From Metadata)
        total_val = data_block.get("total", 0)
        
        # 2. List of Visitors
        rows = data_block.get("list", []) or []
        print(f"   ✅ Success! Found {len(rows)} rows (Total Metadata: {total_val})")
        
        for r in rows:
            # --- STATUS COUNTING LOGIC ---
            # We check different status fields that HikCentral might use
            status = str(r.get("status", r.get("visitorStatus", "")))
            
            # Common HikCentral Status Codes:
            # 1 = Checked In
            # 2 = Checked Out
            # 0 = Registered / Appointed
            
            if status == "1":
                count_in += 1
                status_txt = "Checked In"
            elif status == "2":
                count_out += 1
                status_txt = "Checked Out"
            else:
                # Fallback: Check if timestamps exist
                if r.get("checkOutTime"): 
                    count_out += 1
                    status_txt = "Checked Out"
                elif r.get("checkInTime"): 
                    count_in += 1
                    status_txt = "Checked In"
                else:
                    status_txt = "Registered"

            # Prepare Table Data
            name = r.get("visitorName", "Unknown")
            org = r.get("visitorWorkUnit", "-") # or companyNam
            plate = r.get("plateNo", "-")
            
            # Try to find a date field
            date_str = r.get("visitStartTime") or r.get("registerTime") or r.get("startTime") or ""
            
            display_rows.append((name, org, plate, date_str[:16], status_txt))
            
    else:
        print(f"   ❌ API Response: {data}")

    # --- UPDATE UI ---
    print(f"   -> Counts: Total={total_val}, In={count_in}, Out={count_out}")
    
    vars_dict['total'].set(str(total_val))
    vars_dict['in'].set(str(count_in))
    vars_dict['out'].set(str(count_out))
    vars_dict['time'].set(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    tree.after(0, update_table, tree, display_rows[:50])

def update_table(tree, rows):
    for item in tree.get_children():
        tree.delete(item)
    for row in rows:
        tree.insert("", "end", values=row)

def create_stat_card(parent, title, var, icon_char, color):
    card = tk.Frame(parent, bg=BG_CARD, highlightbackground="#E5E7EB", highlightthickness=1)
    card.pack(side="left", fill="both", expand=True, padx=10, pady=5)
    inner = tk.Frame(card, bg=BG_CARD, padx=20, pady=20)
    inner.pack(fill="both", expand=True)
    top = tk.Frame(inner, bg=BG_CARD)
    top.pack(fill="x")
    tk.Label(top, text=title, font=("Segoe UI", 10, "bold"), fg=TEXT_SEC, bg=BG_CARD).pack(side="left")
    tk.Label(top, text=icon_char, font=("Segoe UI", 14), fg=color, bg=BG_CARD).pack(side="right")
    tk.Label(inner, textvariable=var, font=("Segoe UI", 32, "bold"), fg=TEXT_PRI, bg=BG_CARD).pack(anchor="w", pady=(5,0))

def load_home_screen(parent_frame):
    for w in parent_frame.winfo_children(): w.destroy()
    parent_frame.config(bg=BG_MAIN)
    stats = { "total": tk.StringVar(value="0"), "in": tk.StringVar(value="0"), "out": tk.StringVar(value="0"), "time": tk.StringVar(value="Loading...") }

    header = tk.Frame(parent_frame, bg=BG_MAIN, pady=25, padx=30)
    header.pack(fill="x")
    tk.Label(header, text="Dashboard Overview", font=("Segoe UI", 24, "bold"), fg=TEXT_PRI, bg=BG_MAIN).pack(side="left")
    
    right_header = tk.Frame(header, bg=BG_MAIN)
    right_header.pack(side="right")
    tk.Label(right_header, textvariable=stats['time'], font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG_MAIN).pack(side="right", padx=10)
    tk.Button(right_header, text="🔄 Refresh Stats", bg="#2563EB", fg="white", bd=0, padx=15, pady=6, font=("Segoe UI", 9, "bold"),
              command=lambda: threading.Thread(target=fetch_dashboard_data, args=(stats, table), daemon=True).start()).pack(side="right")

    stats_frame = tk.Frame(parent_frame, bg=BG_MAIN, padx=20)
    stats_frame.pack(fill="x", pady=(0, 20))

    create_stat_card(stats_frame, "TOTAL VISITORS", stats['total'], "👥", COLOR_TOTAL)
    create_stat_card(stats_frame, "CHECKED IN", stats['in'], "📥", COLOR_IN)
    create_stat_card(stats_frame, "CHECKED OUT", stats['out'], "📤", COLOR_OUT)
    
    table_container = tk.Frame(parent_frame, bg=BG_CARD, padx=2, pady=2, highlightbackground="#E5E7EB", highlightthickness=1)
    table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    
    lbl_frame = tk.Frame(table_container, bg="white", pady=10, padx=15)
    lbl_frame.pack(fill="x")
    tk.Label(lbl_frame, text="Visitor List (From visitorInfo)", font=("Segoe UI", 12, "bold"), fg=TEXT_PRI, bg="white").pack(side="left")

    style = ttk.Style()
    style.configure("Dash.Treeview", font=("Segoe UI", 10), rowheight=30)
    style.configure("Dash.Treeview.Heading", font=("Segoe UI", 10, "bold"))
    
    cols = ("Name", "Company", "Vehicle", "Date", "Status")
    table = ttk.Treeview(table_container, columns=cols, show="headings", style="Dash.Treeview", height=10)
    
    table.heading("Name", text="Visitor Name", anchor="w")
    table.heading("Company", text="Company", anchor="w")
    table.heading("Vehicle", text="Plate No", anchor="w")
    table.heading("Date", text="Time", anchor="w")
    table.heading("Status", text="Status", anchor="w")
    
    table.column("Name", width=150)
    table.column("Company", width=150)
    table.column("Vehicle", width=100)
    table.column("Date", width=120)
    table.column("Status", width=100)
    
    sb = ttk.Scrollbar(table_container, orient="vertical", command=table.yview)
    table.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")
    table.pack(fill="both", expand=True)

    threading.Thread(target=fetch_dashboard_data, args=(stats, table), daemon=True).start()