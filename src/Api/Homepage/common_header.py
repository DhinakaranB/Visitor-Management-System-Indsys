import tkinter as tk

def render_global_header(root, home_fn, visitor_fn, person_fn, vehicle_fn, door_fn, access_fn):
    """
    Renders the blue navigation bar with ALL buttons visible.
    """
    
    # 1. Main Header Frame (Blue Background)
    header_frame = tk.Frame(root, bg="#007bff", height=60)
    header_frame.pack(side="top", fill="x")
    
    # 2. Title Label ("VisitorMS")
    title_label = tk.Label(
        header_frame, 
        text="VisitorMS", 
        font=("Arial", 16, "bold"), 
        bg="#007bff", 
        fg="white"
    )
    title_label.pack(side="left", padx=20, pady=10)

    # 3. Helper Function to create buttons consistently
    def nav_button(text, index, command_func):
        btn = tk.Button(
            header_frame,
            text=text,
            bg="#007bff",
            fg="white",
            activebackground="#0056b3",
            activeforeground="white",
            font=("Arial", 12),
            bd=0,
            relief="flat",
            padx=15,
            # We wrap the command so it passes the button widget 'w' if needed
            command=lambda: command_func(btn) 
        )
        btn.pack(side="left", fill="y", padx=2)
        return btn

    # 4. Create ALL Buttons (No IF statements, so they MUST show up)
    # Note: We expect command_func to accept 1 argument (the widget 'w')
    
    nav_button("Home",             1, lambda w: home_fn())
    nav_button("Visitor ▼",        2, lambda w: visitor_fn(w))
    nav_button("Person ▼",         3, lambda w: person_fn(w))   # <-- Forced to show
    nav_button("Vehicle ▼",        4, lambda w: vehicle_fn(w))  # <-- Forced to show
    nav_button("Door ▼",           5, lambda w: door_fn(w))
    nav_button("Access Control",   6, lambda w: access_fn())

    return header_frame