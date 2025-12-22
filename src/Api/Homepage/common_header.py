import tkinter as tk

# --- CONFIGURATION ---
# COLOR: Dark Krishna Blue (Deep Royal Navy)
NAV_BG_COLOR = "#0D1E4C"    
NAV_HOVER_COLOR = "#2A3E75" # Lighter shade for hover interaction
TEXT_COLOR = "#FFFFFF"      # Pure White

FONT_LOGO = ("Segoe UI", 18, "bold")
FONT_ITEM = ("Segoe UI", 11)

def render_global_header(root, home_fn, visitor_fn, person_fn, vehicle_fn, door_fn, access_fn):
    """
    Renders the top navigation bar with a professional Dark Krishna Blue theme.
    """
    # 1. Main Header Frame
    header_frame = tk.Frame(root, bg=NAV_BG_COLOR, height=60) # Slightly taller for elegance
    header_frame.pack(fill="x", side="top")
    header_frame.pack_propagate(False)

    # 2. Logo (Left Side)
    # Using a frame for alignment
    logo_frame = tk.Frame(header_frame, bg=NAV_BG_COLOR)
    logo_frame.pack(side="left", padx=(20, 50))
    
    logo_lbl = tk.Label(logo_frame, text="VisitorMS", bg=NAV_BG_COLOR, fg=TEXT_COLOR, font=FONT_LOGO)
    logo_lbl.pack(side="left")
    
    # Click logo to go home
    logo_lbl.bind("<Button-1>", lambda e: home_fn())
    logo_lbl.bind("<Enter>", lambda e: logo_lbl.config(cursor="hand2"))

    # 3. Navigation Items Container
    nav_container = tk.Frame(header_frame, bg=NAV_BG_COLOR)
    nav_container.pack(side="left", fill="y")

    # --- HELPER: Create Menu Buttons ---
    def create_nav_item(text, command_fn, has_dropdown=False):
        item_frame = tk.Frame(nav_container, bg=NAV_BG_COLOR, padx=18)
        item_frame.pack(side="left", fill="y")
        
        full_text = f"{text}  ▼" if has_dropdown else text
        lbl = tk.Label(item_frame, text=full_text, bg=NAV_BG_COLOR, fg=TEXT_COLOR, font=FONT_ITEM)
        lbl.pack(side="left", fill="y", expand=True)

        def on_enter(e):
            item_frame.config(bg=NAV_HOVER_COLOR)
            lbl.config(bg=NAV_HOVER_COLOR, cursor="hand2")

        def on_leave(e):
            item_frame.config(bg=NAV_BG_COLOR)
            lbl.config(bg=NAV_BG_COLOR)

        def on_click(e):
            if has_dropdown:
                command_fn(item_frame) 
            else:
                command_fn()

        for w in (item_frame, lbl):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

    # 4. Create Items
    create_nav_item("Home", home_fn)
    create_nav_item("Visitor", visitor_fn, True)
    create_nav_item("Person", person_fn, True)
    create_nav_item("Vehicle", vehicle_fn, True)
    create_nav_item("Door", door_fn, True)
    create_nav_item("Access Control", access_fn, False)

    # 5. Right Side: User Profile
    user_frame = tk.Frame(header_frame, bg=NAV_BG_COLOR)
    user_frame.pack(side="right", padx=20)
    
    # Circle for user icon simulation
    tk.Label(user_frame, text="👤 Admin", bg=NAV_BG_COLOR, fg="#AAB7D1", font=("Segoe UI", 10)).pack(side="right")