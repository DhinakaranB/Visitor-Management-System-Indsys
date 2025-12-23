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

# --- API ENDPOINTS ---
API_VISITOR_INFO = "/artemis/api/visitor/v1/visitor/visitorInfo"
API_APPOINTMENT = "/artemis/api/visitor/v1/appointment/queryAppointmentList"

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

    # Wide date range for appointments
    start_time = "2020-01-01T00:00:00+05:30"
    end_time = "2030-12-31T23:59:59+05:30"

    print(f"\n🔹 --- DASHBOARD REFRESH ---")

    # --- 1. Fetch Visitor Info ---
    payload_info = {"pageNo": 1, "pageSize": 100}
    data_info = call_api(API_VISITOR_INFO, payload_info)
    if isinstance(data_info, str): 
        try: data_info = json.loads(data_info)
        except: pass

    # --- 2. Fetch Appointments ---
    payload_app = {
        "pageNo": 1, "pageSize": 100,
        "startTime": start_time, "endTime": end_time
    }
    data_app = call_api(API_APPOINTMENT, payload_app)
    if isinstance(data_app, str): 
        try: data_app = json.loads(data_app)
        except: pass

    # --- MERGE & DEDUPLICATE ---
    combined_rows = []
    seen_unique_keys = set() # To track duplicates (ID or Plate)
    
    in_count = 0
    out_count = 0
    total_val = 0

    # Helper function to extract data safely
    def process_record(r, source_type):
        # 1. FLATTEN DATA: Get fields whether they are at root or in 'visitorBaseInfo'
        base = r.get("visitorBaseInfo", {})
        
        # 2. NAME FIX: Check ALL possible name fields
        name = (r.get("visitorFullName") or 
                r.get("visitorName") or 
                base.get("visitorName") or 
                (r.get("visitorGivenName", "") + " " + r.get("visitorFamilyName", "")).strip())
        
        if not name or name == " ": name = "Unknown"

        # 3. ID / Plate (Used for Deduplication)
        vid = str(r.get("visitorId") or base.get("visitorId") or "")
        plate = str(r.get("plateNo") or base.get("plateNo") or "-")
        
        # 4. COMPANY FIX
        org = r.get("companyName") or r.get("visitorWorkUnit") or base.get("companyNam") or "-"

        # 5. TIME FIX
        # Appointments use 'appointStartTime'. Info uses 'checkInTime' or 'visitStartTime'
        t_raw = (r.get("checkInTime") or 
                 r.get("visitStartTime") or 
                 r.get("appointStartTime") or 
                 r.get("startTime") or 
                 r.get("registerTime") or "")
        
        # Clean Time
        t_display = t_raw.replace("T", " ")[:16] # YYYY-MM-DD HH:MM

        # 6. STATUS LOGIC
        status_raw = str(r.get("status", r.get("visitorStatus", "0")))
        
        if source_type == "APP":
             status_txt = "Registered"
        else:
            if status_raw == "2" or r.get("checkOutTime"):
                status_txt = "Checked Out"
            elif status_raw == "1" or r.get("checkInTime"):
                status_txt = "Checked In"
            else:
                status_txt = "Registered"

        return {
            "id": vid,
            "plate": plate,
            "sort_key": t_raw if t_raw else "0000", # Sort by real ISO time string
            "values": (name, org, plate, t_display, status_txt)
        }

    # --- EXTRACT ROWS ---
    
    # List 1: Visitor Info (The main list)
    if data_info and data_info.get("code") == "0":
        data_block = data_info.get("data", {})
        total_val = data_block.get("total", 0)
        
        # KEY FIX: Check 'VisitorInfo' key as seen in your screenshot
        rows = data_block.get("VisitorInfo") or data_block.get("list", [])
        
        for r in rows:
            item = process_record(r, "INFO")
            
            # Count In/Out
            if item["values"][4] == "Checked In": in_count += 1
            if item["values"][4] == "Checked Out": out_count += 1
            
            combined_rows.append(item)
            
            # Mark ID/Plate as seen
            if item["id"]: seen_unique_keys.add(item["id"])
            if item["plate"] != "-": seen_unique_keys.add(item["plate"])

    # List 2: Appointments
    if data_app and data_app.get("code") == "0":
        rows = data_app.get("data", {}).get("list", [])
        
        for r in rows:
            item = process_record(r, "APP")
            
            # DEDUPLICATION LOGIC:
            # Only add appointment if we haven't seen this ID or Plate in the main list
            is_duplicate = False
            
            if item["id"] and item["id"] in seen_unique_keys: is_duplicate = True
            # Optional: Strict Plate Check (Uncomment if you want 1 record per car)
            # if item["plate"] != "-" and item["plate"] in seen_unique_keys: is_duplicate = True 
            
            if not is_duplicate:
                combined_rows.append(item)

    # --- SORTING & CLEANUP ---
    # Sort Newest First
    combined_rows.sort(key=lambda x: x["sort_key"], reverse=True)
    
    # If the API returned a Total count, use it. Otherwise count rows.
    final_total = total_val if total_val > 0 else len(combined_rows)
    
    # Final List for Table
    final_display_list = [item["values"] for item in combined_rows]

    # --- UPDATE UI ---
    vars_dict['total'].set(str(final_total))
    vars_dict['in'].set(str(in_count))
    vars_dict['out'].set(str(out_count))
    vars_dict['time'].set(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    tree.after(0, update_table, tree, final_display_list)

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
    
    stats = { 
        "total": tk.StringVar(value="-"), 
        "in": tk.StringVar(value="-"), 
        "out": tk.StringVar(value="-"), 
        "time": tk.StringVar(value="Loading...") 
    }

    # Header
    header = tk.Frame(parent_frame, bg=BG_MAIN, pady=25, padx=30)
    header.pack(fill="x")
    tk.Label(header, text="Dashboard Overview", font=("Segoe UI", 24, "bold"), fg=TEXT_PRI, bg=BG_MAIN).pack(side="left")
    
    right = tk.Frame(header, bg=BG_MAIN)
    right.pack(side="right")
    tk.Label(right, textvariable=stats['time'], font=("Segoe UI", 9), fg=TEXT_SEC, bg=BG_MAIN).pack(side="right", padx=10)
    tk.Button(right, text="🔄 Refresh", bg="#2563EB", fg="white", bd=0, padx=15, pady=6, font=("Segoe UI", 9, "bold"),
              command=lambda: threading.Thread(target=fetch_dashboard_data, args=(stats, table), daemon=True).start()).pack(side="right")

    # Cards
    stats_frame = tk.Frame(parent_frame, bg=BG_MAIN, padx=20)
    stats_frame.pack(fill="x", pady=(0, 20))
    create_stat_card(stats_frame, "TOTAL VISITORS", stats['total'], "👥", COLOR_TOTAL)
    create_stat_card(stats_frame, "CHECKED IN", stats['in'], "📥", COLOR_IN)
    create_stat_card(stats_frame, "CHECKED OUT", stats['out'], "📤", COLOR_OUT)
    
    # Table
    table_container = tk.Frame(parent_frame, bg=BG_CARD, padx=2, pady=2, highlightbackground="#E5E7EB", highlightthickness=1)
    table_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))
    
    lbl_frame = tk.Frame(table_container, bg="white", pady=10, padx=15)
    lbl_frame.pack(fill="x")
    tk.Label(lbl_frame, text="Recent Visitor Activity", font=("Segoe UI", 12, "bold"), fg=TEXT_PRI, bg="white").pack(side="left")

    style = ttk.Style()
    style.configure("Dash.Treeview", font=("Segoe UI", 10), rowheight=30)
    style.configure("Dash.Treeview.Heading", font=("Segoe UI", 10, "bold"))
    
    cols = ("Name", "Company", "Vehicle", "Time", "Status")
    table = ttk.Treeview(table_container, columns=cols, show="headings", style="Dash.Treeview", height=12)
    
    table.heading("Name", text="Visitor Name", anchor="w")
    table.heading("Company", text="Company", anchor="w")
    table.heading("Vehicle", text="Plate No", anchor="w")
    table.heading("Time", text="Register/Visit Time", anchor="w")
    table.heading("Status", text="Status", anchor="w")
    
    table.column("Name", width=150)
    table.column("Company", width=150)
    table.column("Vehicle", width=100)
    table.column("Time", width=120)
    table.column("Status", width=100)
    
    sb = ttk.Scrollbar(table_container, orient="vertical", command=table.yview)
    table.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")
    table.pack(fill="both", expand=True)

    threading.Thread(target=fetch_dashboard_data, args=(stats, table), daemon=True).start()