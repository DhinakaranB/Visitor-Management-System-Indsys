import tkinter as tk
from tkinter import ttk, messagebox
import Api.Common_signature.common_signature_api as api_handler
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURATION
# ==========================================
BG_COLOR = "#F4F6F7"
CARD_BG = "#FFFFFF"
PRIMARY_COLOR = "#3498DB"  # Blue
SUCCESS_COLOR = "#27AE60"  # Green
LABEL_COLOR = "#7F8C8D"

# API Endpoint for Booking Appointment
# Standard Artemis Path:
API_APPOINTMENT_PATH = "/artemis/api/visitor/v1/appointment"

ui_elements = {}
current_visitor_id = None

# ==========================================
# 2. LOGIC HANDLERS
# ==========================================

def handle_booking(root_instance):
    """ Collects data and sends to API """
    
    # 1. Get Data
    vis_id = ui_elements["id_entry"].get()
    start_time = ui_elements["start_entry"].get()
    end_time = ui_elements["end_entry"].get()
    purpose = ui_elements["purpose_entry"].get()
    
    if not vis_id:
        messagebox.showwarning("Required", "Visitor ID is missing.")
        return

    # 2. Prepare Payload
    # Artemis requires ISO 8601 format (e.g., 2023-10-25T14:00:00+05:30)
    # This code assumes the user entered the default format YYYY-MM-DD HH:MM:SS
    # We replace the space with 'T' and add a timezone offset if your server needs it.
    # For simplicity, we send standard format:
    
    fmt_start = start_time.replace(" ", "T")
    fmt_end = end_time.replace(" ", "T")

    # Add Timezone offset if needed (e.g., +05:30 for India). 
    # If your server is local, usually simple ISO works. 
    # Let's try adding a generic Z or local offset if you face date format errors.
    # For now, we will assume the server accepts the standard ISO string.

    payload = {
        "visitorId": vis_id,
        "appointStartTime": fmt_start,
        "appointEndTime": fmt_end,
        "visitPurpose": purpose,
        "privilegeGroup": "" # Optional
    }

    ui_elements["status_lbl"].config(text="BOOKING...", fg=PRIMARY_COLOR)
    root_instance.update()

    # 3. Call API
    response = api_handler.call_api(API_APPOINTMENT_PATH, payload)

    # 4. Handle Response
    if response and response.get("code") == "0":
        data = response.get("data", {})
        
        # Get the Critical ID for Check-In
        appoint_id = data.get("appointRecordId") or data.get("orderId")
        
        if appoint_id:
            messagebox.showinfo("✅ Success", 
                f"Appointment Booked Successfully!\n\n"
                f"Appointment Record ID: {appoint_id}\n"
                f"(Use this ID for Check-In/Out)"
            )
            ui_elements["status_lbl"].config(text=f"BOOKED! ID: {appoint_id}", fg=SUCCESS_COLOR)
        else:
            messagebox.showwarning("Warning", "Booking successful, but No Appointment ID returned.")
    else:
        msg = response.get('msg') if response else "Unknown Error"
        messagebox.showerror("Booking Failed", f"Error: {msg}")
        ui_elements["status_lbl"].config(text="FAILED", fg="red")


def set_default_times():
    """ Fills time fields with Now and Now + 2 Hours """
    now = datetime.now()
    later = now + timedelta(hours=2)
    
    # Format: YYYY-MM-DD HH:MM:SS
    time_fmt = "%Y-%m-%d %H:%M:%S"
    
    ui_elements["start_entry"].delete(0, tk.END)
    ui_elements["start_entry"].insert(0, now.strftime(time_fmt))
    
    ui_elements["end_entry"].delete(0, tk.END)
    ui_elements["end_entry"].insert(0, later.strftime(time_fmt))


# ==========================================
# 3. UI LAYOUT
# ==========================================

def show_appointment_screen(root_instance, show_main_menu, prefill_visitor_id=None):
    global ui_elements, current_visitor_id
    current_visitor_id = prefill_visitor_id
    
    # Clear Screen
    for widget in root_instance.winfo_children():
        widget.destroy()
    root_instance.config(bg=BG_COLOR)

    # Main Container
    main_frame = tk.Frame(root_instance, bg=BG_COLOR)
    main_frame.pack(fill="both", expand=True, padx=40, pady=20)

    # Header
    header_frame = tk.Frame(main_frame, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(0, 20))
    
    # Back button goes back to Main Menu (or you could pass show_register_screen to go back there)
    tk.Button(header_frame, text="← Main Menu", command=show_main_menu, bg=BG_COLOR, bd=0, fg=LABEL_COLOR, cursor="hand2").pack(side="left")
    tk.Label(header_frame, text="Book Appointment (Step 2)", font=("Segoe UI", 20, "bold"), bg=BG_COLOR, fg="#2C3E50").pack(side="left", padx=20)

    # Form Card
    form_card = tk.Frame(main_frame, bg=CARD_BG, padx=30, pady=30)
    form_card.pack(fill="both", expand=True)
    form_card.columnconfigure(1, weight=1)

    def add_field(row, label, var_name, readonly=False):
        tk.Label(form_card, text=label, bg=CARD_BG, fg=LABEL_COLOR, font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w", pady=(15, 5))
        entry = ttk.Entry(form_card, font=("Segoe UI", 11))
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        if readonly:
            entry.config(state="readonly")
        ui_elements[var_name] = entry

    # 1. Visitor ID (Auto-filled)
    add_field(0, "VISITOR ID", "id_entry")
    if prefill_visitor_id:
        ui_elements["id_entry"].insert(0, str(prefill_visitor_id))
        # Optional: Make it read-only so they don't change it by mistake
        # ui_elements["id_entry"].config(state="readonly")

    # 2. Time Fields
    add_field(1, "START TIME (YYYY-MM-DD HH:MM:SS)", "start_entry")
    add_field(2, "END TIME (YYYY-MM-DD HH:MM:SS)", "end_entry")
    
    # 3. Purpose
    add_field(3, "PURPOSE OF VISIT", "purpose_entry")
    ui_elements["purpose_entry"].insert(0, "Business Meeting") # Default

    # Set Defaults immediately
    set_default_times()

    # Action Area
    action_frame = tk.Frame(main_frame, bg=BG_COLOR)
    action_frame.pack(fill="x", pady=20)

    btn_book = tk.Button(
        action_frame, text="CONFIRM BOOKING", bg=PRIMARY_COLOR, fg="white",
        font=("Segoe UI", 12, "bold"), padx=20, pady=10, bd=0, cursor="hand2",
        command=lambda: handle_booking(root_instance)
    )
    btn_book.pack(side="left")
    
    ui_elements["status_lbl"] = tk.Label(action_frame, text="", bg=BG_COLOR, font=("Segoe UI", 10, "bold"))
    ui_elements["status_lbl"].pack(side="left", padx=20)