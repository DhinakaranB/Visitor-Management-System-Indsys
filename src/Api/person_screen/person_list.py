import tkinter as tk
from tkinter import ttk, messagebox

def show_list(parent_frame):
    # 1. Clear the frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Title & Header
    header_frame = tk.Frame(parent_frame, bg="#D6EAF8")
    header_frame.pack(fill="x", pady=10, padx=20)
    
    tk.Label(header_frame, text="Person List", font=("Segoe UI", 20, "bold"), bg="#D6EAF8").pack(side="left")

    # 3. Action Buttons (Edit/Delete)
    def edit_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a person to edit")
            return
        item = tree.item(selected[0])['values']
        messagebox.showinfo("Edit", f"Editing Person: {item[1]}") # Placeholder

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a person to delete")
            return
        # Remove from UI
        tree.delete(selected[0])
        messagebox.showinfo("Deleted", "Person deleted successfully")

    btn_frame = tk.Frame(header_frame, bg="#D6EAF8")
    btn_frame.pack(side="right")
    
    tk.Button(btn_frame, text="Edit", bg="#ffc107", command=edit_selected).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Delete", bg="#dc3545", fg="white", command=delete_selected).pack(side="left", padx=5)

    # 4. Treeview (The List)
    cols = ("Code", "Name", "Gender", "Phone", "Email", "Card")
    tree = ttk.Treeview(parent_frame, columns=cols, show="headings", height=15)
    
    # Define Headings
    tree.heading("Code", text="Person Code")
    tree.heading("Name", text="Full Name")
    tree.heading("Gender", text="Gender")
    tree.heading("Phone", text="Phone")
    tree.heading("Email", text="Email")
    tree.heading("Card", text="Card No")

    # Define Column Widths
    tree.column("Code", width=100)
    tree.column("Name", width=150)
    tree.column("Gender", width=80)
    tree.column("Phone", width=120)
    tree.column("Email", width=180)
    tree.column("Card", width=100)

    tree.pack(fill="both", expand=True, padx=20, pady=10)

    # 5. Insert Mock Data (Based on your image)
    # Data: Code, Name, Gender, Phone, Email, Card
    mock_data = [
        ("DK0121", "Dhinakaran AG", "Male", "638208282", "dina@gmail.com", "2212423"),
        ("DK0122", "Test User", "Female", "987654321", "test@demo.com", "1122334"),
    ]

    for person in mock_data:
        tree.insert("", "end", values=person)