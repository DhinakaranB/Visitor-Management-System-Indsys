import tkinter as tk
from tkinter import ttk, messagebox
import Api.Common_signature.common_signature_api as api_handler

# ===== CONFIG =====
DELETE_API_PATH = "/artemis/api/visitor/v1/appointment/single/delete"
BG_COLOR = "#F4F6F7"
CARD_BG = "white"

# ------------------------------------------------------
# SHARED DELETE LOGIC (Call this from anywhere)
# ------------------------------------------------------
def delete_appointment_logic(appoint_id):
    """
    Sends the delete request to Artemis API.
    Returns True if successful, False otherwise.
    """
    if not appoint_id:
        return False

    payload = {"appointRecordId": str(appoint_id)}
    
    # Use the common signature API to send request
    response = api_handler.call_api(DELETE_API_PATH, payload)

    if response and response.get("code") == "0":
        return True
    else:
        # If there is an error message, show it
        msg = response.get("msg", "Unknown Error") if response else "No response"
        print(f"Delete failed: {msg}")
        return False


# ------------------------------------------------------
# DELETE UI SCREEN (For manual deletion by ID)
# ------------------------------------------------------
def show_visitor_delete(content_frame):
    """
    Renders a simple UI to manually delete a visitor by ID.
    """
    # Clear previous content
    for widget in content_frame.winfo_children():
        widget.destroy()
        
    content_frame.config(bg=BG_COLOR)
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    # --- Central Card ---
    card = tk.Frame(content_frame, bg=CARD_BG, padx=40, pady=40)
    card.place(relx=0.5, rely=0.4, anchor="center")

    tk.Label(
        card, 
        text="Delete Appointment", 
        font=("Segoe UI", 18, "bold"), 
        bg=CARD_BG, 
        fg="#E74C3C"
    ).pack(pady=(0, 20))

    tk.Label(
        card, 
        text="Enter Appointment ID:", 
        font=("Segoe UI", 10), 
        bg=CARD_BG
    ).pack(anchor="w")

    id_entry = ttk.Entry(card, width=35, font=("Segoe UI", 11))
    id_entry.pack(pady=(5, 20))

    def on_delete_click():
        appoint_id = id_entry.get().strip()
        if not appoint_id:
            messagebox.showwarning("Warning", "Please enter an ID.")
            return

        if messagebox.askyesno("Confirm", f"Permanently delete ID: {appoint_id}?"):
            success = delete_appointment_logic(appoint_id)
            if success:
                messagebox.showinfo("Success", "Appointment deleted successfully.")
                id_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to delete. Check console/logs.")

    # Delete Button
    btn = tk.Button(
        card, 
        text="🗑 Delete Forever", 
        bg="#E74C3C", 
        fg="white", 
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        command=on_delete_click
    )
    btn.pack(fill="x", pady=5)