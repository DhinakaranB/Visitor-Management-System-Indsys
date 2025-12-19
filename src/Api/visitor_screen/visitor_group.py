import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json
import Api.Common_signature.common_signature_api as api_handler

# ===== CONFIG =====
BG_COLOR = "#F4F6F7"
CARD_BG = "white"
HEADER_TEXT = "#2C3E50"

# ===== API ENDPOINTS =====
API_CREATE_GROUP = "/artemis/api/visitor/v1/visitorgroups"
API_GROUP_INFO   = "/artemis/api/visitor/v1/visitorgroups/groupinfo"
API_VISITOR_OUT  = "/artemis/api/visitor/v1/visitor/out"
API_CHECK_STATUS = "/artemis/api/visitor/v1/appointment/getVisitorStatus"

# Global variable to share the ID between tabs
last_created_index_code = None


# ------------------------------------------------------
# TAB 1: VISITOR GROUP CREATE
# ------------------------------------------------------
def render_group_create(parent):
    frame = tk.Frame(parent, bg=CARD_BG, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Create New Visitor Group", font=("Segoe UI", 16, "bold"), bg=CARD_BG, fg=HEADER_TEXT).pack(anchor="w", pady=(0, 20))

    form = tk.Frame(frame, bg=CARD_BG)
    form.pack(anchor="w")

    tk.Label(form, text="Visitor Group Name:", bg=CARD_BG, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", padx=10, pady=10)
    name_entry = ttk.Entry(form, width=35)
    name_entry.grid(row=0, column=1, sticky="w", padx=10, pady=10)

    def on_create():
        group_name = name_entry.get().strip()
        if not group_name:
            messagebox.showwarning("Validation", "Group Name is required.")
            return

        payload = {"visitorGroupName": group_name}

        def callback(response):
            if response and response.get("code") == "0":
                data = response.get("data", {})
                try:
                    group_list = data.get("VisitorGroupList", {}).get("VisitorGroup", [])
                    if group_list:
                        new_id = str(group_list[0].get("indexCode", ""))
                        if last_created_index_code:
                            last_created_index_code.set(new_id)
                        messagebox.showinfo("Success", f"Group Created!\n\nName: {group_name}\nIndex Code: {new_id}\n\n(Copied to Group Info tab)")
                    else:
                        messagebox.showinfo("Success", f"Group '{group_name}' created (No ID returned).")
                        
                    name_entry.delete(0, tk.END)
                except Exception as e:
                    print(f"Error parsing response: {e}")
                    messagebox.showinfo("Success", "Group created, but could not parse ID.")
            else:
                 msg = response.get("msg", "Unknown Error") if response else "No response"
                 messagebox.showerror("Error", f"Failed: {msg}")

        res = api_handler.call_api(API_CREATE_GROUP, payload)
        callback(res)

    tk.Button(form, text="Create Group", bg="#3498DB", fg="white", font=("Segoe UI", 10, "bold"), command=on_create).grid(row=1, column=1, sticky="w", padx=10, pady=20)


# ------------------------------------------------------
# TAB 2: VISITOR GROUP INFO (List Visitors in Group)
# ------------------------------------------------------
def render_group_info(parent):
    frame = tk.Frame(parent, bg=CARD_BG, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Get Visitor Group Info", font=("Segoe UI", 16, "bold"), bg=CARD_BG, fg=HEADER_TEXT).pack(anchor="w", pady=(0, 10))

    search_frame = tk.Frame(frame, bg=CARD_BG)
    search_frame.pack(fill="x", pady=10)
    
    tk.Label(search_frame, text="Group Index Code:", bg=CARD_BG).pack(side="left", padx=5)
    
    index_entry = ttk.Entry(search_frame, width=15, textvariable=last_created_index_code)
    index_entry.pack(side="left", padx=5)

    columns = ("visitorId", "name", "gender", "phone")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
    tree.pack(fill="both", expand=True, pady=10)

    tree.heading("visitorId", text="Visitor ID")
    tree.heading("name", text="Name")
    tree.heading("gender", text="Gender")
    tree.heading("phone", text="Phone")
    
    # Configure column width
    tree.column("visitorId", width=100)
    tree.column("name", width=200)
    tree.column("gender", width=100)
    tree.column("phone", width=150)

    def fetch_info():
        idx = index_entry.get().strip()
        if not idx:
            messagebox.showwarning("Error", "Please enter Group Index Code (e.g., '1')")
            return

        # Clear table
        for item in tree.get_children():
            tree.delete(item)

        # UPDATED PAYLOAD: Matching Postman screenshot structure
        payload = {
            "VisitorListRequest": {
                "indexCode": str(idx),
                "pageIndex": 1,
                "pageSize": 100,
                # Some API versions require searchCriteria to be present, even if empty
                "searchCriteria": {
                    "identifiyCode": str(idx) # Based on your screenshot showing this ID repeated
                }
            }
        }

        print(f"DEBUG: Sending payload: {payload}")
        res = api_handler.call_api(API_GROUP_INFO, payload)
        
        if res and res.get("code") == "0":
            data = res.get("data", {})
            
            # Handle potential null 'list'
            raw_list = data.get("list")
            if raw_list is None:
                rows = []
            else:
                rows = raw_list
            
            if isinstance(rows, list):
                if not rows:
                    # Provide feedback if list is valid but empty
                    messagebox.showinfo("Result", f"Group {idx} exists, but contains 0 visitors.")
                    return

                for r in rows:
                    # Extract Data
                    v_id = r.get("ID", "-")
                    base_info = r.get("BaseInfo", {})
                    
                    full_name = base_info.get("fullName") or base_info.get("name") or r.get("personName", "-")
                    
                    gender_code = base_info.get("gender") or r.get("gender")
                    gender = "Male" if str(gender_code) == "1" else "Female"
                    
                    phone = base_info.get("phoneNo") or r.get("phoneNo", "-")

                    tree.insert("", "end", values=(v_id, full_name, gender, phone))
            else:
                # Debugging fallback
                messagebox.showwarning("API Warning", f"Unexpected data format received:\n{data}")
        else:
            msg = res.get("msg") if res else "Connection Failed"
            messagebox.showerror("API Error", f"Failed: {msg}")

    tk.Button(search_frame, text="🔍 Search", command=fetch_info).pack(side="left", padx=10)


# ------------------------------------------------------
# TAB 3: VISITOR OUT (Check Out)
# ------------------------------------------------------
def render_group_out_in(parent):
    frame = tk.Frame(parent, bg=CARD_BG, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Visitor Check-Out", font=("Segoe UI", 16, "bold"), bg=CARD_BG, fg=HEADER_TEXT).pack(anchor="w", pady=(0, 20))

    panel = tk.Frame(frame, bg="#ECF0F1", padx=20, pady=30)
    panel.pack(fill="x")

    tk.Label(panel, text="Appointment Record ID:", bg="#ECF0F1", font=("Segoe UI", 10)).grid(row=0, column=0, padx=10, pady=10)
    id_entry = ttk.Entry(panel, width=30)
    id_entry.grid(row=0, column=1, padx=10, pady=10)

    def do_checkout():
        rec_id = id_entry.get().strip()
        if not rec_id:
            messagebox.showwarning("Validation", "Enter Appointment Record ID")
            return

        payload = {"appointRecordId": rec_id}

        def callback(res):
            if res and res.get("code") == "0":
                messagebox.showinfo("Success", f"Visitor (AppointID: {rec_id}) Checked Out!")
                id_entry.delete(0, tk.END)
            else:
                msg = res.get("msg") if res else "Failed"
                messagebox.showerror("Error", msg)

        res = api_handler.call_api(API_VISITOR_OUT, payload)
        callback(res)

    btn = tk.Button(panel, text="Check OUT 🚪", bg="#E74C3C", fg="white", font=("Segoe UI", 10, "bold"), command=do_checkout)
    btn.grid(row=0, column=2, padx=20)


# ------------------------------------------------------
# TAB 4: VISITOR STATUS
# ------------------------------------------------------
def render_group_status(parent):
    frame = tk.Frame(parent, bg=CARD_BG, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Check Visitor Status", font=("Segoe UI", 16, "bold"), bg=CARD_BG, fg=HEADER_TEXT).pack(anchor="w", pady=(0, 20))

    input_frame = tk.Frame(frame, bg=CARD_BG)
    input_frame.pack(anchor="w", pady=10)

    tk.Label(input_frame, text="Visitor ID:", bg=CARD_BG).grid(row=0, column=0, sticky="e", padx=10, pady=5)
    vis_id_entry = ttk.Entry(input_frame, width=20)
    vis_id_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)

    tk.Label(input_frame, text="Time Point:", bg=CARD_BG).grid(row=1, column=0, sticky="e", padx=10, pady=5)
    
    date_entry = DateEntry(input_frame, width=18, date_pattern="yyyy-mm-dd")
    date_entry.grid(row=1, column=1, sticky="w", padx=10, pady=5)

    result_var = tk.StringVar(value="Status: Waiting for input...")
    res_label = tk.Label(frame, textvariable=result_var, font=("Segoe UI", 12), bg="#ECF0F1", width=50, height=3, relief="sunken")
    res_label.pack(pady=30)

    def check_status():
        vid = vis_id_entry.get().strip()
        d_str = date_entry.get_date().strftime("%Y-%m-%d")
        full_time = f"{d_str}T09:00:00+05:30" 

        if not vid:
            messagebox.showwarning("Error", "Visitor ID required")
            return

        payload = {"visitorId": vid, "visitTimePoint": full_time}

        res = api_handler.call_api(API_CHECK_STATUS, payload)
        
        if res and res.get("code") == "0":
            raw_data = res.get("data")
            result_var.set(f"✅ Status: {raw_data}")
            res_label.config(fg="green")
        else:
            err = res.get("msg") if res else "Unknown"
            result_var.set(f"❌ Error: {err}")
            res_label.config(fg="red")

    tk.Button(input_frame, text="Check Status", bg="#3498DB", fg="white", command=check_status).grid(row=2, column=1, sticky="w", padx=10, pady=15)


# ------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------
def show_visitor_group_screen(content_frame):
    global last_created_index_code
    
    if last_created_index_code is None:
        last_created_index_code = tk.StringVar(value="1")

    for widget in content_frame.winfo_children():
        widget.destroy()

    content_frame.config(bg=BG_COLOR)

    container = tk.Frame(content_frame, bg=BG_COLOR, padx=20, pady=20)
    container.pack(fill="both", expand=True)

    style = ttk.Style()
    style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 5])
    
    notebook = ttk.Notebook(container)
    notebook.pack(fill="both", expand=True)

    tab1 = tk.Frame(notebook, bg=CARD_BG)
    tab2 = tk.Frame(notebook, bg=CARD_BG)
    tab3 = tk.Frame(notebook, bg=CARD_BG)
    tab4 = tk.Frame(notebook, bg=CARD_BG)

    notebook.add(tab1, text="Visitor Group Create")
    notebook.add(tab2, text="Visitor Group Info")
    notebook.add(tab3, text="Visitor Out")
    notebook.add(tab4, text="Visitor Status")

    render_group_create(tab1)
    render_group_info(tab2)
    render_group_out_in(tab3)
    render_group_status(tab4)