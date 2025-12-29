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
API_APPOINTMENT_LIST = "/artemis/api/visitor/v1/appointment/appointmentlist"

# --- COLORS ---
BG_MAIN = "#F8F9FA"       
BG_CARD = "#FFFFFF"       
TEXT_PRI = "#111827"      
TEXT_SEC = "#6B7280"      
HEADER_BG = "#F3F4F6"     
BORDER_COLOR = "#E5E7EB"  
DARK_BLUE_TEXT = "#062F6C" 

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

    # --- 1. Fetch Stats ---
    payload_info = {"pageNo": 1, "pageSize": 1}
    data_info = call_api(API_VISITOR_INFO, payload_info)
    if isinstance(data_info, str): 
        try: data_info = json.loads(data_info)
        except: pass

    # --- 2. Fetch Appointments ---
    payload_app = {
        "pageNo": 1,
        "pageSize": 500,
        "appointStartTime": start_time,
        "appointEndTime": end_time
    }
    data_app = call_api(API_APPOINTMENT_LIST, payload_app)
    if isinstance(data_app, str): 
        try: data_app = json.loads(data_app)
        except: pass

    # --- PROCESS STATS ---
    real_total_visitors = 0
    in_count = 0
    out_count = 0
    
    if data_info and data_info.get("code") == "0":
        data_block = data_info.get("data", {})
        real_total_visitors = data_block.get("total", 0)
        rows = data_block.get("VisitorInfo") or []
        for r in rows:
            status = str(r.get("status", "0"))
            if status == "1": in_count += 1
            elif status == "2": out_count += 1

    # --- PROCESS GRID ---
    grid_rows = []
    
    if data_app and data_app.get("code") == "0":
        app_list = data_app.get("data", {}).get("list", [])
        
        for r in app_list:
            v_info = r.get("visitorInfo", {})
            
            # 1. ID
            vid = str(v_info.get("visitorId") or "")
            
            # 2. Name
            name = v_info.get("visitorGivenName", "")
            if not name: name = v_info.get("visitorName", "Unknown")

            # 3. Gender
            g_code = v_info.get("gender")
            gender = "Male" if g_code == 1 else "Female" if g_code == 2 else "--"

            # 4. Phone
            phone = v_info.get("phoneNo") or v_info.get("certificateNo") or "--"

            # 5. Reason
            reason = str(r.get("visitorReasonName", "--"))
            
            # 6. Receptionist
            receptionist = str(r.get("receptionistName", "Admin"))
            
            # 7. Times
            t_start_raw = r.get("appointStartTime", "")
            t_end_raw = r.get("appointEndTime", "")
            t_start = t_start_raw.replace("T", " ")[:16] if t_start_raw else "--"
            t_end = t_end_raw.replace("T", " ")[:16] if t_end_raw else "--"

            # Create Row
            grid_rows.append({
                "sort_key": t_start_raw,
                "values": (vid, name, gender, phone, reason, receptionist, t_start, t_end)
            })

    # Sort & Finalize
    grid_rows.sort(key=lambda x: x["sort_key"], reverse=True)
    final_display_list = [x["values"] for x in grid_rows]

    # --- UPDATE UI ---
    vars_dict['total'].set(str(real_total_visitors))
    vars_dict['in'].set(str(in_count))
    vars_dict['out'].set(str(out_count))
    vars_dict['time'].set(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

    tree.after(0, update_table, tree, final_display_list)

def update_table(tree, rows):
    for item in tree.get_children():
        tree.delete(item)
    
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=row, tags=(tag,))

def create_stat_card(parent, title, var, icon_char, color):
    card = tk.Frame(parent, bg=BG_CARD, highlightbackground="#E5E7EB", highlightthickness=1)
    card.pack(side="left", fill="both", expand=True, padx=10, pady=5)
    
    inner = tk.Frame(card, bg=BG_CARD, padx=24, pady=24)
    inner.pack(fill="both", expand=True)
    
    top = tk.Frame(inner, bg=BG_CARD)
    top.pack(fill="x")
    tk.Label(top, text=title.upper(), font=("Segoe UI", 9, "bold"), fg=TEXT_SEC, bg=BG_CARD).pack(side="left")
    tk.Label(top, text=icon_char, font=("Segoe UI", 16), fg=color, bg=BG_CARD).pack(side="right")
    
    tk.Label(inner, textvariable=var, font=("Segoe UI", 36, "bold"), fg=TEXT_PRI, bg=BG_CARD).pack(anchor="w", pady=(8,0))

def load_home_screen(parent_frame):
    for w in parent_frame.winfo_children(): w.destroy()
    parent_frame.config(bg=BG_MAIN)
    
    stats = { 
        "total": tk.StringVar(value="-"), 
        "in": tk.StringVar(value="-"), 
        "out": tk.StringVar(value="-"), 
        "time": tk.StringVar(value="Loading...") 
    }

    # --- HEADER ---
    header = tk.Frame(parent_frame, bg=BG_MAIN, pady=30, padx=40)
    header.pack(fill="x")
    
    tk.Label(header, text="Dashboard Overview", font=("Segoe UI", 28, "bold"), fg=DARK_BLUE_TEXT, bg=BG_MAIN).pack(side="left")
    
    right = tk.Frame(header, bg=BG_MAIN)
    right.pack(side="right")
    tk.Label(right, textvariable=stats['time'], font=("Segoe UI", 10), fg=TEXT_SEC, bg=BG_MAIN).pack(side="right", padx=15)
    
    tk.Button(right, text=" ↻ Refresh ", bg="#2563EB", fg="white", bd=0, padx=25, pady=8, 
              font=("Segoe UI", 10, "bold"), cursor="hand2", activebackground="#1E40AF", activeforeground="white",
              command=lambda: threading.Thread(target=fetch_dashboard_data, args=(stats, table), daemon=True).start()
    ).pack(side="right")

    # --- STAT CARDS ---
    stats_frame = tk.Frame(parent_frame, bg=BG_MAIN, padx=30)
    stats_frame.pack(fill="x", pady=(0, 30))
    create_stat_card(stats_frame, "Total Visitors", stats['total'], "👥", "#3B82F6")
    create_stat_card(stats_frame, "Checked In", stats['in'], "📥", "#10B981")
    create_stat_card(stats_frame, "Checked Out", stats['out'], "📤", "#6B7280")
    
    # --- TABLE CONTAINER ---
    table_outer = tk.Frame(parent_frame, bg=BG_CARD, padx=1, pady=1, highlightbackground="#E5E7EB", highlightthickness=1)
    table_outer.pack(fill="both", expand=True, padx=40, pady=(0, 40))
    
    lbl_frame = tk.Frame(table_outer, bg="white", pady=20, padx=20)
    lbl_frame.pack(fill="x")
    
    tk.Label(lbl_frame, text="Recent Visitor Appointment Activity", font=("Segoe UI", 14, "bold"), fg=DARK_BLUE_TEXT, bg="white").pack(side="left")

    style = ttk.Style()
    style.theme_use("clam")

    # Row Style
    style.configure("Dash.Treeview", 
                    background="white",
                    foreground="#111827",
                    rowheight=45, 
                    fieldbackground="white",
                    bordercolor="white", 
                    font=("Segoe UI", 10))
    
    # --- HEADER STYLE (DARK MODE) ---
    style.configure("Dash.Treeview.Heading", 
                    background="#0F3168",      # Dark Blue Background
                    foreground="white",        # White Text
                    font=("Segoe UI", 10, "bold"),
                    relief="flat",
                    padding=(10, 10))

    # High Contrast Selection
    style.map("Dash.Treeview", 
        background=[('selected', '#3498DB')], 
        foreground=[('selected', 'white')]
    )

    # --- TABLE SETUP ---
    cols = ("ID", "Visitor Name", "Gender", "Phone", "Reason", "Receptionist", "Start Time", "End Time")
    table = ttk.Treeview(table_outer, columns=cols, show="headings", style="Dash.Treeview")
    
    # Headers
    table.heading("ID", text="ID", anchor="center")
    table.heading("Visitor Name", text="Visitor Name", anchor="w")
    table.heading("Gender", text="Gender", anchor="center")
    table.heading("Phone", text="Phone / ID", anchor="w")
    table.heading("Reason", text="Reason", anchor="center")
    table.heading("Receptionist", text="Receptionist", anchor="center")
    table.heading("Start Time", text="Start Time", anchor="center")
    table.heading("End Time", text="End Time", anchor="center")
    
    # Columns
    table.column("ID", width=60, minwidth=50, stretch=False, anchor="center")      
    table.column("Visitor Name", width=150, anchor="w") 
    table.column("Gender", width=80, anchor="center")
    table.column("Phone", width=120, anchor="w")
    table.column("Reason", width=110, anchor="center")
    table.column("Receptionist", width=130, anchor="center")
    table.column("Start Time", width=140, anchor="center")
    table.column("End Time", width=140, anchor="center")
    
    sb = ttk.Scrollbar(table_outer, orient="vertical", command=table.yview)
    table.configure(yscroll=sb.set)
    sb.pack(side="right", fill="y")
    table.pack(fill="both", expand=True)

    table.tag_configure("odd", background="white")
    table.tag_configure("even", background="#F9FAFB")

    threading.Thread(target=fetch_dashboard_data, args=(stats, table), daemon=True).start()