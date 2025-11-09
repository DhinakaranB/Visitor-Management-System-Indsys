# Ui.py

import tkinter as tk
from tkinter import ttk
import add_visitor as visitor_form 
import datetime 

# --- Custom Color Palette ---
BG_COLOR = "#F7F8FA"       
PRIMARY_COLOR = "#3498DB"  
SUCCESS_COLOR = "#2ecc71"  
DANGER_COLOR = "#e74c3c"   
TEXT_COLOR = "#333333"

# --- Global Window Variable ---
root = None 

def get_current_datetime():
    """Returns current time formatted for the API."""
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

def clear_screen(root_instance):
    """Clears all widgets from the main window."""
    for w in root_instance.winfo_children():
        w.destroy()

def close_application():
    """Function to close the main Tkinter window."""
    global root
    if root:
        root.quit()
        root.destroy()

def show_main_screen():
    """Displays the main menu screen."""
    global root
    if not root: return
    
    clear_screen(root)
    
    tk.Label(root, text="Visitor Management System", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=40)
    
    button_frame = tk.Frame(root, bg=BG_COLOR)
    button_frame.pack(fill='x', padx=30, pady=15)
    
    # Button to launch the Visitor Registration form
    ttk.Button(button_frame, 
               text="➕ Add Visitor Appointment", 
               style="TPrimary.TButton", 
               command=lambda: visitor_form.show_create_form(root, show_main_screen, close_application)
               ).pack(side=tk.LEFT, ipadx=10, ipady=5)


def setup_styles(style):
    """Configures the custom ttk styles."""
    style.theme_use('clam')
    
    style.configure("TPrimary.TButton", font=("Segoe UI", 12, "bold"), foreground='white', background=PRIMARY_COLOR, borderwidth=0, relief="flat")
    style.map("TPrimary.TButton", background=[('active', '#5DADE2')])

    style.configure("TSuccess.TButton", font=("Segoe UI", 12, "bold"), foreground='white', background=SUCCESS_COLOR, borderwidth=0, relief="flat")
    style.map("TSuccess.TButton", background=[('active', '#27AE60')])

    style.configure("TDanger.TButton", font=("Segoe UI", 10), foreground='white', background=DANGER_COLOR, borderwidth=0, relief="flat")
    style.map("TDanger.TButton", background=[('active', '#C0392B')])
    
    style.configure("TSecondary.TButton", font=("Segoe UI", 10), foreground=TEXT_COLOR, background=BG_COLOR, borderwidth=1, relief="raised")
    style.map("TSecondary.TButton", background=[('active', '#EEEEEE')])

# ---------------------- Main Window Execution ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Visitor Management System")
    root.configure(bg=BG_COLOR)
    root.geometry("500x700") 
    
    setup_styles(ttk.Style(root))
        
    show_main_screen()
    root.mainloop()