import tkinter as tk
from tkinter import ttk, messagebox

def show_create_form(parent_frame, on_success_callback=None):
    # 1. Clear the frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Title
    tk.Label(parent_frame, text="Add New Person", font=("Segoe UI", 20, "bold"), bg="#D6EAF8").pack(pady=20)

    # 3. Form Container
    form_frame = tk.Frame(parent_frame, bg="white", padx=20, pady=20)
    form_frame.pack()

    # --- HELPER TO CREATE ENTRIES ---
    entries = {}
    row_counter = 0

    def add_field(label_text, key):
        nonlocal row_counter
        tk.Label(form_frame, text=label_text, bg="white", font=("Segoe UI", 10)).grid(row=row_counter, column=0, sticky="w", pady=5)
        entry = tk.Entry(form_frame, width=30, font=("Segoe UI", 10))
        entry.grid(row=row_counter, column=1, pady=5, padx=10)
        entries[key] = entry
        row_counter += 1

    # --- FORM FIELDS (Based on your JSON) ---
    add_field("Person Code (ID):", "personCode")
    add_field("First Name:", "personGivenName")
    add_field("Last Name:", "personFamilyName")
    
    # Gender (Dropdown)
    tk.Label(form_frame, text="Gender:", bg="white", font=("Segoe UI", 10)).grid(row=row_counter, column=0, sticky="w", pady=5)
    gender_var = tk.StringVar(value="1")
    gender_combo = ttk.Combobox(form_frame, textvariable=gender_var, values=["1 - Male", "2 - Female"], state="readonly", width=27)
    gender_combo.current(0)
    gender_combo.grid(row=row_counter, column=1, pady=5, padx=10)
    row_counter += 1

    add_field("Phone No:", "phoneNo")
    add_field("Email:", "email")
    add_field("Card No:", "cardNo")
    add_field("Remark:", "remark")

    # --- SAVE BUTTON ---
    def save_person():
        # Collect data
        data = {
            "personCode": entries["personCode"].get(),
            "personGivenName": entries["personGivenName"].get(),
            "personFamilyName": entries["personFamilyName"].get(),
            "gender": gender_var.get().split(" ")[0], # Gets "1" or "2"
            "phoneNo": entries["phoneNo"].get(),
            "email": entries["email"].get(),
            "cards": [{"cardNo": entries["cardNo"].get()}], # Nested list as per JSON
            "remark": entries["remark"].get(),
            "orgIndexCode": "1" # Hardcoded based on example
        }

        # Validation
        if not data["personCode"] or not data["personGivenName"]:
            messagebox.showwarning("Validation", "Person Code and Name are required!")
            return

        print("Sending Payload:", data) # DEBUG: See the JSON in console
        messagebox.showinfo("Success", "Person added successfully! (Mock)")
        
        # Go back to list if callback provided
        if on_success_callback:
            on_success_callback()

    btn_save = tk.Button(form_frame, text="Save Person", bg="#28a745", fg="white", font=("Segoe UI", 11), command=save_person)
    btn_save.grid(row=row_counter, column=1, pady=20, sticky="e")