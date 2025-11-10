# ui.py

import tkinter as tk
from tkinter import ttk
import add_visitor as visitor_form
import common_api 


# Colors
BG_COLOR = "#F4F6F7"
NAV_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#3498DB"
TEXT_COLOR = "#2C3E50"
SUCCESS_COLOR = "#2ECC71"  
DANGER_COLOR = "#E74C3C"  
SECONDARY_COLOR = "#95A5A6" 

root = None
content_frame = None # Dynamic area

def clear_content():
    """
    Clears all widgets from the central content frame.
    """
    if content_frame:
        for widget in content_frame.winfo_children():
            widget.destroy()

def close_application():
    """Closes the main Tkinter application."""
    if root:
        root.quit()
        root.destroy()

def show_home():
    """
    Displays the default home welcome screen.
    FIXED: Uses if content_frame: to prevent 'NoneType' error on startup/callback.
    """
    clear_content()
    
    # CRITICAL FIX: Ensure content_frame is initialized
    if content_frame:
        # Configure content_frame's grid weights to allow centering
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
    
        # Center the home content within the content_frame
        home_center = tk.Frame(content_frame, bg=BG_COLOR)
        
        # Use grid() instead of pack() to place home_center inside content_frame
        home_center.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid inside home_center for centered content
        home_center.grid_rowconfigure(0, weight=1)
        home_center.grid_rowconfigure(2, weight=1)
        home_center.grid_columnconfigure(0, weight=1)
        
        text_frame = tk.Frame(home_center, bg=BG_COLOR)
        text_frame.grid(row=1, column=0, padx=20, pady=20)
        
        tk.Label(text_frame, text="Welcome to Visitor Management System",
                 font=("Segoe UI", 22, "bold"), bg=BG_COLOR, fg=PRIMARY_COLOR).pack(pady=(20, 10))
        tk.Label(text_frame,
                 text="Use the navigation bar above to manage visitor appointments and access control.",
                 font=("Segoe UI", 12), bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(0, 20))


def show_add_visitor():
    """Clears the screen and loads the responsive visitor registration form."""
    clear_content()
    # Note: close_application is passed to allow closing the app from the form, if needed later
    visitor_form.show_create_form(content_frame, show_home, close_application)

def show_visitor_list():
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        lbl = tk.Label(content_frame, text="👥 Visitor List (Coming Soon)",
                       font=("Segoe UI", 14), bg=BG_COLOR, fg=TEXT_COLOR)
        lbl.grid(row=0, column=0, padx=20, pady=40)

def show_door_list():
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        lbl = tk.Label(content_frame, text="🚪 Door List (Coming Soon)",
                       font=("Segoe UI", 14), bg=BG_COLOR, fg=TEXT_COLOR)
        lbl.grid(row=0, column=0, padx=20, pady=40)

def show_access_control():
    clear_content()
    if content_frame:
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        lbl = tk.Label(content_frame, text="🛂 Access Control (Coming Soon)",
                       font=("Segoe UI", 14), bg=BG_COLOR, fg=TEXT_COLOR)
        lbl.grid(row=0, column=0, padx=20, pady=40)

def setup_navbar():
    """Creates and returns the navigation bar frame."""
    nav = tk.Frame(root, bg=NAV_COLOR, relief="raised", bd=1)

    buttons = [
        ("➕ Add Visitor", show_add_visitor),
        ("👥 Visitor List", show_visitor_list),
        ("🚪 Door List", show_door_list),
        ("🛂 Access Control", show_access_control),
        ("❌ Exit", close_application)
    ]

    for text, cmd in buttons:
        ttk.Button(nav, text=text, style="Nav.TButton", command=cmd).pack(side="left", padx=8, pady=5)
        
    return nav

def setup_styles(style):
    """Configures the custom ttk styles used application-wide."""
    style.theme_use("clam")
    
    # --- Navigation Styles ---
    style.configure("Nav.TButton", font=("Segoe UI", 10, "bold"),
                    foreground="white", background=PRIMARY_COLOR, padding=6, borderwidth=0)
    style.map("Nav.TButton", background=[("active", "#2E86C1")])
    
    # --- Form Styles (Used by add_visitor.py) ---
    style.configure("TEntry", fieldbackground="white", foreground=TEXT_COLOR, bordercolor=SECONDARY_COLOR, borderwidth=1)
    style.configure("TRadiobutton", background=BG_COLOR, foreground=TEXT_COLOR)
    
    # Reduced padding for smaller button appearance
    style.configure("TSuccess.TButton", foreground='white', background=SUCCESS_COLOR, font=("Segoe UI", 11, "bold"), padding=(10, 5), relief="flat")
    style.map("TSuccess.TButton", background=[('active', '#27AE60')])
    
    style.configure("TSecondary.TButton", foreground='white', background=SECONDARY_COLOR, font=("Segoe UI", 10), padding=(10, 5), relief="flat")
    style.map("TSecondary.TButton", background=[('active', '#7F8C8D')])
    
    style.configure("TInfo.TButton", font=("Segoe UI", 10, "bold"), background=PRIMARY_COLOR, foreground="white", relief="flat", padding=(5, 5)) 
    style.map("TInfo.TButton", background=[('active', '#2980B9')])


def init_ui():
    """Initializes the main window and layout using grid for responsiveness."""
    global root, content_frame
    root.title("Visitor Management System")
    root.geometry("1000x650")
    root.configure(bg=BG_COLOR)

    # --- 1. Configure Grid on the main 'root' window for responsiveness ---
    root.grid_rowconfigure(0, weight=0) # Header (Fixed)
    root.grid_rowconfigure(1, weight=0) # Navbar (Fixed)
    root.grid_rowconfigure(2, weight=1) # CONTENT FRAME (Gets all vertical expansion)
    root.grid_rowconfigure(3, weight=0) # Footer (Fixed)
    root.grid_columnconfigure(0, weight=1) # Horizontal expansion

    # --- 2. Place Header (Row 0) ---
    header = tk.Label(root, text="Visitor Management System", font=("Segoe UI", 20, "bold"),
                      bg=BG_COLOR, fg=TEXT_COLOR)
    header.grid(row=0, column=0, sticky="ew", pady=(15, 5))

    # --- 3. Setup Navbar (Row 1) ---
    nav = setup_navbar() 
    nav.grid(row=1, column=0, sticky="ew")

    # --- 4. Content Frame (Row 2, the responsive area) ---
    # CRITICAL: This line initializes and assigns content_frame
    content_frame = tk.Frame(root, bg=BG_COLOR)
    content_frame.grid(row=2, column=0, sticky="nsew") # Fills the expanded cell

    # --- 5. Footer (Row 3) ---
    footer = tk.Frame(root, bg=BG_COLOR)
    footer.grid(row=3, column=0, sticky="ew", pady=10)
    tk.Label(footer, text="© 2025 Copyright by Indsys Holdings - All rights reserved.",
             font=("Segoe UI", 9), bg=BG_COLOR, fg="#7F8C8D").pack(side="left", padx=15)

    # This call is now safe because content_frame is defined above
    show_home()

if __name__ == "__main__":
    root = tk.Tk()
    setup_styles(ttk.Style(root))
    init_ui()
    root.mainloop()