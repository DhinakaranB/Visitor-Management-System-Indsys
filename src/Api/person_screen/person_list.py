import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# Import our Modules
from src.Api.person_screen import person_form
from src.Api.person_screen import person_delete

LIST_API_URL = "/artemis/api/resource/v1/person/personList"

# --- GLOBAL DATA STORE (To hold full objects for Edit) ---
current_person_data = []

def fetch_and_update_list(tree):
    global current_person_data
    if not common_signature_api: return

    payload = {"pageNo": 1, "pageSize": 50}
    
    try:
        # Call API
        if hasattr(common_signature_api, 'call_api'):
            response = common_signature_api.call_api(LIST_API_URL, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            response = common_signature_api.send_to_api(LIST_API_URL, payload)
        else:
            return

        # Handle Dict vs String
        if isinstance(response, str): data = json.loads(response)
        else: data = response if isinstance(response, dict) else response.json()

        if data.get("code") == "0":
            api_list = data.get("data", {}).get("list", [])
            current_person_data = api_list # Store for Editing
            tree.after(0, update_treeview, tree, api_list)
        else:
            print(f"API Error: {data.get('msg')}")

    except Exception as e:
        print("List Fetch Error:", e)

def update_treeview(tree, person_list):
    for item in tree.get_children(): tree.delete(item)

    for p in person_list:
        code = p.get("personCode", "-")
        name = p.get("personName", "Unknown")
        gender = "Male" if str(p.get("gender")) == "1" else "Female"
        phone = p.get("phoneNo", "-")
        email = p.get("email", "-")
        card = p.get("cards", [{}])[0].get("cardNo", "-") if p.get("cards") else "-"
        
        # Insert Row
        tree.insert("", "end", values=(code, name, gender, phone, email, card))

def on_edit_click(tree, parent_frame):
    """Finds the full person object and opens Edit Form"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a person to edit.")
        return

    # Get the Person Code from the selected row
    item = tree.item(selected[0])
    code_in_row = item['values'][0] # Column 0 is Code

    # Find the full object from our global list 'current_person_data'
    # We need the full object because the Treeview doesn't show hidden fields like 'remark'
    person_obj = next((p for p in current_person_data if p["personCode"] == str(code_in_row)), None)

    if person_obj:
        # Open Form in Edit Mode
        person_form.show_create_form(parent_frame, on_success_callback=lambda: show_list(parent_frame), edit_data=person_obj)
    else:
        messagebox.showerror("Error", "Could not find person details.")

def on_delete_click(tree):
    """Calls Delete Module"""
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a person to delete.")
        return

    item = tree.item(selected[0])
    code = str(item['values'][0])

    if messagebox.askyesno("Confirm", f"Are you sure you want to delete {code}?"):
        # Call our new Delete File
        success = person_delete.delete_by_code(code)
        if success:
            messagebox.showinfo("Deleted", "Person deleted successfully.")
            fetch_and_update_list(tree) # Refresh

def show_list(parent_frame):
    for widget in parent_frame.winfo_children(): widget.destroy()

    # Title & Buttons
    header = tk.Frame(parent_frame, bg="#D6EAF8", pady=10)
    header.pack(fill="x", padx=20)
    tk.Label(header, text="Person List", font=("Segoe UI", 20, "bold"), bg="#D6EAF8").pack(side="left")

    btn_frame = tk.Frame(header, bg="#D6EAF8")
    btn_frame.pack(side="right")
    
    # Refresh
    tk.Button(btn_frame, text="🔄 Refresh", bg="#17a2b8", fg="white", 
              command=lambda: fetch_and_update_list(tree)).pack(side="left", padx=2)
    
    # Edit Button (Yellow)
    tk.Button(btn_frame, text="✎ Edit", bg="#ffc107", 
              command=lambda: on_edit_click(tree, parent_frame)).pack(side="left", padx=2)

    # Delete Button (Red)
    tk.Button(btn_frame, text="🗑 Delete", bg="#dc3545", fg="white", 
              command=lambda: on_delete_click(tree)).pack(side="left", padx=2)

    # Treeview
    cols = ("Code", "Name", "Gender", "Phone", "Email", "Card")
    tree = ttk.Treeview(parent_frame, columns=cols, show="headings", height=15)
    
    tree.heading("Code", text="Person Code")
    tree.heading("Name", text="Full Name")
    tree.heading("Gender", text="Gender")
    tree.heading("Phone", text="Phone")
    tree.heading("Email", text="Email")
    tree.heading("Card", text="Card No")
    
    tree.column("Code", width=120); tree.column("Name", width=150); tree.column("Gender", width=80)
    tree.column("Phone", width=100); tree.column("Email", width=180); tree.column("Card", width=100)

    scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # Load Data
    threading.Thread(target=fetch_and_update_list, args=(tree,), daemon=True).start()