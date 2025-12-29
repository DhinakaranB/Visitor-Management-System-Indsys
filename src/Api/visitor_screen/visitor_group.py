import tkinter as tk
from tkinter import ttk, messagebox
import json
import math
from datetime import datetime

# --- IMPORT DATE ENTRY ---
try:
    from tkcalendar import DateEntry
except ImportError:
    print("⚠️ Warning: 'tkcalendar' library not found. Please install it.")
    DateEntry = None 

# Try importing the API handler safely
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None

# ================= CONFIGURATION =================
BG_COLOR = "#F4F6F7"        
CARD_BG = "#FFFFFF"         
PRIMARY_COLOR = "#3498DB"   
SECONDARY_COLOR = "#2980B9"
TEXT_COLOR = "#2C3E50"      
LABEL_COLOR = "#7F8C8D"     
DANGER_COLOR = "#E74C3C"    
SUCCESS_COLOR = "#27AE60"   

# Fonts
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 11, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BTN = ("Segoe UI", 10, "bold")

# ===== API ENDPOINTS =====
API_CREATE_GROUP = "/artemis/api/visitor/v1/visitorgroups"
API_GROUP_INFO   = "/artemis/api/visitor/v1/visitorgroups/groupinfo"
API_VISITOR_OUT  = "/artemis/api/visitor/v1/visitor/out"
API_CHECK_STATUS = "/artemis/api/visitor/v1/appointment/getVisitorStatus"

# ===== STATUS DEFINITIONS (From Documentation) =====
VISITOR_STATUS_MAP = {
    "-1": "Null / No Status",
    "0":  "Reserved",
    "1":  "Expired",
    "2":  "Visited",
    "3":  "Checked In (On Site)",
    "4":  "Checked Out",
    "5":  "Auto Checked Out (Time Over)",
    "6":  "Self-Service Check Out",
    "7":  "Not Checked Out (Overstay)",
    "8":  "Pending Approval",
    "9":  "Reservation Failed"
}

last_created_index_code = None

# ------------------------------------------------------
# TAB 1: VISITOR GROUP CREATE
# ------------------------------------------------------
def render_group_create(parent):
    card = tk.Frame(parent, bg=CARD_BG, padx=40, pady=40)
    card.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(card, text="Create New Visitor Group", font=FONT_TITLE, bg=CARD_BG, fg=PRIMARY_COLOR).pack(anchor="w", pady=(0, 10))
    tk.Label(card, text="Create a logical group to manage multiple visitors together.", font=("Segoe UI", 10), bg=CARD_BG, fg=LABEL_COLOR).pack(anchor="w", pady=(0, 30))

    form = tk.Frame(card, bg=CARD_BG)
    form.pack(anchor="w", fill="x")

    tk.Label(form, text="Visitor Group Name:", bg=CARD_BG, fg=TEXT_COLOR, font=FONT_SUBTITLE).pack(anchor="w", pady=(0, 5))
    name_entry = ttk.Entry(form, font=("Segoe UI", 12), width=40)
    name_entry.pack(anchor="w", ipadx=5, ipady=5) 

    def on_create():
        group_name = name_entry.get().strip()
        if not group_name:
            messagebox.showwarning("Validation", "Group Name is required.")
            return

        if not api_handler: return

        payload = {"visitorGroupName": group_name}
        res = api_handler.call_api(API_CREATE_GROUP, payload)

        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            try:
                group_list = data.get("VisitorGroupList", {}).get("VisitorGroup", [])
                if group_list:
                    new_id = str(group_list[0].get("indexCode", ""))
                    if last_created_index_code:
                        last_created_index_code.set(new_id)
                    messagebox.showinfo("Success", f"✅ Group Created! Index Code: {new_id}")
                else:
                    messagebox.showinfo("Success", f"✅ Group '{group_name}' created.")
                name_entry.delete(0, tk.END)
            except:
                messagebox.showinfo("Success", "Group created.")
        else:
             msg = res.get("msg", "Error") if res else "No response"
             messagebox.showerror("Error", f"Failed: {msg}")

    tk.Button(form, text="Create Group ➤", bg=PRIMARY_COLOR, fg="white", font=FONT_BTN, 
                    bd=0, padx=25, pady=10, cursor="hand2", command=on_create).pack(anchor="w", pady=20)


# ------------------------------------------------------
# TAB 2: GROUP INFO (Pagination + Clean Grid)
# ------------------------------------------------------
def render_group_info(parent):
    # State Variables
    current_page = 1
    page_size = 20
    total_records = 0
    
    card = tk.Frame(parent, bg=CARD_BG, padx=20, pady=20)
    card.pack(fill="both", expand=True, padx=20, pady=20)

    # --- SEARCH ---
    search_frame = tk.Frame(card, bg=CARD_BG)
    search_frame.pack(fill="x", pady=(0, 15))

    tk.Label(search_frame, text="Group Index Code:", font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
    index_entry = ttk.Entry(search_frame, width=15, font=("Segoe UI", 10), textvariable=last_created_index_code)
    index_entry.pack(side="left", padx=(5, 20))

    tk.Label(search_frame, text="Search Name (Optional):", font=FONT_BODY, bg=CARD_BG, fg=TEXT_COLOR).pack(side="left")
    name_search_entry = ttk.Entry(search_frame, width=25, font=("Segoe UI", 10))
    name_search_entry.pack(side="left", padx=(5, 15))

    def on_search_click():
        nonlocal current_page
        current_page = 1 
        fetch_data()

    btn_search = tk.Button(search_frame, text="🔍 Search", bg=PRIMARY_COLOR, fg="white", font=FONT_BTN, 
                           bd=0, padx=20, pady=2, cursor="hand2", command=on_search_click)
    btn_search.pack(side="left")

    # --- TABLE STYLE (Clean, No Hover) ---
    style = ttk.Style()
    style.configure("Blue.Treeview.Heading", 
                    background=PRIMARY_COLOR, 
                    foreground="white", 
                    font=("Segoe UI", 10, "bold"), 
                    relief="flat",
                    padding=(10, 8))
    
    style.configure("Blue.Treeview", 
                    rowheight=35, 
                    font=("Segoe UI", 10),
                    fieldbackground="white",
                    borderwidth=0)
    
    # Remove Hover: Make 'active' color same as 'selected' or white
    style.map("Blue.Treeview", 
              background=[('selected', '#EBF5FB'), ('active', 'white')], 
              foreground=[('selected', 'black'), ('active', 'black')])

    # --- TABLE CONTAINER (No Scrollbar) ---
    table_frame = tk.Frame(card, bg="white", highlightbackground="#E0E0E0", highlightthickness=1)
    table_frame.pack(fill="both", expand=True)

    columns = ("visitorId", "name")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Blue.Treeview")
    
    tree.heading("visitorId", text="Visitor ID", anchor="center")
    tree.heading("name", text="Visitor Name", anchor="w")
    
    tree.column("visitorId", width=120, anchor="center")
    tree.column("name", width=500, anchor="w") 

    tree.pack(fill="both", expand=True) # No scrollbar, just pack it

    tree.tag_configure('odd', background='white')
    tree.tag_configure('even', background='#F8F9FA')

    # --- PAGINATION ---
    footer = tk.Frame(card, bg=CARD_BG, pady=15)
    footer.pack(fill="x")

    paging_container = tk.Frame(footer, bg=CARD_BG)
    paging_container.pack(side="right")

    def change_page(delta):
        nonlocal current_page
        new_page = current_page + delta
        if new_page < 1: return
        current_page = new_page
        fetch_data()

    btn_prev = tk.Button(paging_container, text=" < Back ", bg="white", fg=TEXT_COLOR, font=("Segoe UI", 9), 
                         bd=1, relief="solid", cursor="hand2", command=lambda: change_page(-1))
    btn_prev.pack(side="left", padx=5)

    lbl_page_info = tk.Label(paging_container, text=" 1 ", font=("Segoe UI", 10, "bold"), bg=PRIMARY_COLOR, fg="white", width=4)
    lbl_page_info.pack(side="left", padx=5)

    btn_next = tk.Button(paging_container, text=" Next > ", bg="white", fg=TEXT_COLOR, font=("Segoe UI", 9), 
                         bd=1, relief="solid", cursor="hand2", command=lambda: change_page(1))
    btn_next.pack(side="left", padx=5)
    
    lbl_total_info = tk.Label(footer, text="Total: 0", font=("Segoe UI", 9), bg=CARD_BG, fg=LABEL_COLOR)
    lbl_total_info.pack(side="left", padx=10)

    # --- FETCH DATA ---
    def fetch_data():
        nonlocal total_records
        idx = index_entry.get().strip()
        search_name = name_search_entry.get().strip()

        if not idx:
            messagebox.showwarning("Validation", "Enter Group Index Code")
            return
        if not api_handler: return

        for item in tree.get_children(): tree.delete(item)

        req_data = {
            "indexCode": str(idx),
            "pageIndex": current_page,
            "pageSize": page_size
        }
        if search_name:
            req_data["searchCriteria"] = {"personName": search_name}

        payload = {"VisitorListRequest": req_data}
        res = api_handler.call_api(API_GROUP_INFO, payload)
        
        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            rows = data.get("VisitorList", {}).get("Visitor", [])
            if not rows: rows = data.get("list", []) 

            total_records = data.get("total", 0)
            total_pages = math.ceil(total_records / page_size) if total_records else 1
            
            lbl_page_info.config(text=f"{current_page}")
            lbl_total_info.config(text=f"Total: {total_records} | Pages: {total_pages}")

            btn_prev.config(state="normal" if current_page > 1 else "disabled")
            btn_next.config(state="normal" if current_page < total_pages else "disabled")

            if not rows:
                if current_page == 1: messagebox.showinfo("Result", "No visitors found.")
                return

            for i, r in enumerate(rows):
                v_id = r.get("ID", "-")
                base = r.get("BaseInfo", {})
                name = base.get("fullName") or r.get("personName", "Unknown")
                tag = 'even' if i % 2 == 0 else 'odd'
                tree.insert("", "end", values=(v_id, name), tags=(tag,))
        else:
            msg = res.get("msg", "Error") if res else "No Response"
            messagebox.showerror("Error", msg)


# ------------------------------------------------------
# TAB 3: VISITOR OUT
# ------------------------------------------------------
def render_group_out_in(parent):
    wrapper = tk.Frame(parent, bg=BG_COLOR)
    wrapper.pack(fill="both", expand=True)
    card = tk.Frame(wrapper, bg=CARD_BG, padx=40, pady=40, relief="solid", bd=1)
    card.place(relx=0.5, rely=0.3, anchor="center", width=600)

    tk.Label(card, text="Visitor Check-Out", font=FONT_TITLE, bg=CARD_BG, fg=DANGER_COLOR).pack(pady=(0, 20))
    
    row = tk.Frame(card, bg=CARD_BG)
    row.pack(fill="x", pady=10)
    tk.Label(row, text="Appoint Record ID:", font=FONT_SUBTITLE, bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w")
    id_entry = ttk.Entry(row, font=("Segoe UI", 12))
    id_entry.pack(fill="x", pady=5, ipady=3)

    def do_checkout():
        rec_id = id_entry.get().strip()
        if not rec_id: return
        if not api_handler: return
        
        payload = {"appointRecordId": rec_id}
        res = api_handler.call_api(API_VISITOR_OUT, payload)
        
        if res and str(res.get("code")) == "0":
            messagebox.showinfo("Success", "✅ Visitor Checked Out!")
            id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", res.get("msg", "Failed"))

    tk.Button(card, text="CHECK OUT", bg=DANGER_COLOR, fg="white", font=FONT_BTN, 
              bd=0, padx=30, pady=12, cursor="hand2", command=do_checkout).pack(pady=20)


# ------------------------------------------------------
# TAB 4: VISITOR STATUS (Updated with Descriptions)
# ------------------------------------------------------
def render_group_status(parent):
    wrapper = tk.Frame(parent, bg=BG_COLOR)
    wrapper.pack(fill="both", expand=True)
    card = tk.Frame(wrapper, bg=CARD_BG, padx=40, pady=40, relief="solid", bd=1)
    card.place(relx=0.5, rely=0.4, anchor="center", width=700)

    tk.Label(card, text="Check Visitor Status", font=FONT_TITLE, bg=CARD_BG, fg=PRIMARY_COLOR).pack(pady=(0, 25))
    
    form = tk.Frame(card, bg=CARD_BG)
    form.pack()
    
    tk.Label(form, text="Visitor ID:", font=FONT_BODY, bg=CARD_BG).grid(row=0, column=0, sticky="e", padx=10, pady=10)
    vis_id_entry = ttk.Entry(form, font=("Segoe UI", 11), width=25)
    vis_id_entry.grid(row=0, column=1, sticky="w", padx=10)

    tk.Label(form, text="Check Date:", font=FONT_BODY, bg=CARD_BG).grid(row=1, column=0, sticky="e", padx=10, pady=10)
    
    if DateEntry:
        date_entry = DateEntry(form, width=23, background=PRIMARY_COLOR, foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
        date_entry.grid(row=1, column=1, sticky="w", padx=10)
    else:
        date_entry = ttk.Entry(form, width=23)
        date_entry.insert(0, "YYYY-MM-DD")
        date_entry.grid(row=1, column=1, sticky="w", padx=10)

    res_label = tk.Label(card, text="Waiting for input...", font=("Segoe UI", 12), bg="#ECF0F1", fg="#7F8C8D", width=50, height=3)
    res_label.pack(pady=30)

    def check_status():
        vid = vis_id_entry.get().strip()
        if not vid: return
        if not api_handler: return
        
        if hasattr(date_entry, 'get_date'):
            d_str = date_entry.get_date().strftime('%Y-%m-%d')
        else:
            d_str = date_entry.get()

        full_time = f"{d_str}T09:00:00+05:30"
        payload = {"visitorId": vid, "visitTimePoint": full_time}
        res = api_handler.call_api(API_CHECK_STATUS, payload)
        
        if res and str(res.get("code")) == "0":
            # --- STATUS MAPPING LOGIC ---
            data_dict = res.get("data", {})
            # The API returns data like: {'visitorStatus': '1'}
            status_code = str(data_dict.get("visitorStatus", "-1"))
            
            # Get description from map
            status_desc = VISITOR_STATUS_MAP.get(status_code, "Unknown Status")
            
            res_label.config(text=f"✅ Status: {status_desc}", fg=SUCCESS_COLOR, bg="#D5F5E3")
        else:
            res_label.config(text=f"❌ Error: {res.get('msg')}", fg=DANGER_COLOR, bg="#FADBD8")

    tk.Button(card, text="Check Status", bg=PRIMARY_COLOR, fg="white", font=FONT_BTN, 
              bd=0, padx=30, pady=10, cursor="hand2", command=check_status).pack()


# ------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------
def show_visitor_group_screen(content_frame):
    global last_created_index_code
    if last_created_index_code is None: last_created_index_code = tk.StringVar(value="")

    for widget in content_frame.winfo_children(): widget.destroy()
    content_frame.config(bg=BG_COLOR)

    container = tk.Frame(content_frame, bg=BG_COLOR, padx=30, pady=30)
    container.pack(fill="both", expand=True)

    style = ttk.Style()
    style.theme_use('clam') 
    style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI", 11), background=BG_COLOR, foreground="#7F8C8D", padding=[25, 12], borderwidth=0, focuscolor=BG_COLOR)
    style.map("TNotebook.Tab", background=[("selected", BG_COLOR)], foreground=[("selected", PRIMARY_COLOR)], font=[("selected", ("Segoe UI", 11, "bold"))])

    notebook = ttk.Notebook(container, style="TNotebook")
    notebook.pack(fill="both", expand=True)

    separator = tk.Frame(container, bg=PRIMARY_COLOR, height=2)
    separator.pack(fill="x", pady=(0, 20)) 

    tab1 = tk.Frame(notebook, bg=BG_COLOR)
    tab2 = tk.Frame(notebook, bg=BG_COLOR)
    tab3 = tk.Frame(notebook, bg=BG_COLOR)
    tab4 = tk.Frame(notebook, bg=BG_COLOR)

    notebook.add(tab1, text="Create Group")
    notebook.add(tab2, text="Group Info")
    notebook.add(tab3, text="Visitor Out")
    notebook.add(tab4, text="Visitor Status")

    render_group_create(tab1)
    render_group_info(tab2)
    render_group_out_in(tab3)
    render_group_status(tab4)