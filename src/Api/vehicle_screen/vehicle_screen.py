import tkinter as tk

def show_placeholder(parent_frame, title):
    """
    Displays a 'Under Construction' message for menus that act as placeholders.
    """
    # 1. Clear the frame
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 2. Header
    header = tk.Frame(parent_frame, bg="#D6EAF8", pady=10)
    header.pack(fill="x", padx=20, pady=10)
    tk.Label(header, text=title, font=("Segoe UI", 20, "bold"), bg="#D6EAF8").pack()

    # 3. Message
    content = tk.Frame(parent_frame, bg="white")
    content.pack(fill="both", expand=True, padx=20, pady=10)
    
    tk.Label(content, text=f"🚧 {title}", font=("Segoe UI", 16, "bold"), fg="#333", bg="white").pack(pady=(50, 10))
    tk.Label(content, text="This module is currently under development.", font=("Segoe UI", 12), fg="#777", bg="white").pack()

# --- Wrapper Functions for Menu Items ---

def show_parking_list(parent): 
    show_placeholder(parent, "Vehicle Parking List")

def show_floor_list(parent): 
    show_placeholder(parent, "Floor List")

def show_floor_overview(parent): 
    show_placeholder(parent, "Floor Overview")

def show_passageway_record(parent): 
    show_placeholder(parent, "Parking Lot Passageway Record")

def show_fee_calc(parent): 
    show_placeholder(parent, "Parking Fee Calculation")

def show_fee_confirm(parent): 
    show_placeholder(parent, "Parking Fees Confirm")