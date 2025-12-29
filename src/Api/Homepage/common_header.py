import tkinter as tk

# --- CONFIGURATION ---
# GRADIENT COLORS (Deep Purple -> Bright Blue)
COLOR_LEFT = "#667eea"   # Soft Blue
COLOR_RIGHT = "#764ba2"  # Deep Purple
TEXT_COLOR = "#FFFFFF"   # White
HOVER_COLOR = "#FFD700"  # Gold color on hover

FONT_LOGO = ("Segoe UI", 20, "bold")
FONT_ITEM = ("Segoe UI", 11, "bold")

class GradientHeader(tk.Canvas):
    """
    A Custom Navbar that draws a gradient and handles transparent text buttons.
    """
    def __init__(self, parent, height=70, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, **kwargs)
        self.pack(fill="x", side="top")
        
        # Bind resize event to redraw gradient
        self.bind("<Configure>", self._draw_gradient)
        self.items = [] # Store nav items to manage clicks

    def _draw_gradient(self, event=None):
        """ Draws the horizontal gradient background """
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Don't draw if width is too small (startup)
        if width < 1: return

        (r1, g1, b1) = self.winfo_rgb(COLOR_LEFT)
        (r2, g2, b2) = self.winfo_rgb(COLOR_RIGHT)
        
        # Draw vertical lines to create gradient
        limit = width
        r_ratio = (r2 - r1) / limit
        g_ratio = (g2 - g1) / limit
        b_ratio = (b2 - b1) / limit

        # Optimization: Draw every 2nd pixel to improve resize performance
        for i in range(0, limit, 2): 
            nr = int((r1 + (r_ratio * i)) / 256)
            ng = int((g1 + (g_ratio * i)) / 256)
            nb = int((b1 + (b_ratio * i)) / 256)
            color = "#%4.4x%4.4x%4.4x" % (nr, ng, nb)
            self.create_line(i, 0, i, height, tags=("gradient",), fill=color, width=3)
        
        self.tag_lower("gradient") # Keep gradient behind text

    def add_logo(self, text, cmd):
        """ Adds the Logo text on the left """
        tag = "logo"
        self.create_text(30, 35, text=text, fill=TEXT_COLOR, font=FONT_LOGO, anchor="w", tags=(tag,))
        self.tag_bind(tag, "<Button-1>", lambda e: cmd())
        self.tag_bind(tag, "<Enter>", lambda e: self.config(cursor="hand2"))
        self.tag_bind(tag, "<Leave>", lambda e: self.config(cursor=""))

    def add_nav_items(self, items):
        """ Adds navigation buttons dynamically """
        start_x = 200 # Position where buttons start
        gap = 100     # Space between buttons

        for i, (text, cmd, has_dropdown) in enumerate(items):
            display_text = f"{text} ▼" if has_dropdown else text
            x_pos = start_x + (i * gap)
            tag = f"nav_{i}"
            
            # Draw Text
            self.create_text(x_pos, 35, text=display_text, fill=TEXT_COLOR, font=FONT_ITEM, anchor="w", tags=(tag,))
            
            # --- CRITICAL FIX IS HERE ---
            # We must pass 'is_dropdown=has_dropdown' as a default argument.
            # This 'freezes' the value so it doesn't get overwritten by the next loop iteration.
            def on_click(event, command=cmd, widget_ref=self, is_dropdown=has_dropdown):
                if is_dropdown:
                    command(widget_ref) 
                else:
                    command()

            def on_enter(event, t=tag):
                self.itemconfig(t, fill=HOVER_COLOR)
                self.config(cursor="hand2")

            def on_leave(event, t=tag):
                self.itemconfig(t, fill=TEXT_COLOR)
                self.config(cursor="")

            self.tag_bind(tag, "<Button-1>", on_click)
            self.tag_bind(tag, "<Enter>", on_enter)
            self.tag_bind(tag, "<Leave>", on_leave)

    def add_profile(self):
        """ Adds the Admin Profile on the right """

def render_global_header(root, home_fn, visitor_fn, person_fn, vehicle_fn, door_fn, access_fn):
    """
    Renders the new Gradient Navbar
    """
    # 1. Create the Gradient Canvas
    header = GradientHeader(root)

    # 2. Add Logo
    header.add_logo("VisitorMS", home_fn)

    # 3. Add Navigation Items
    # Format: ("Name", Function, HasDropdown)
    nav_items = [
        ("Home", home_fn, False),
        ("Visitor", visitor_fn, True),
        ("Person", person_fn, True),
        ("Vehicle", vehicle_fn, True),
        ("Door", door_fn, True),
        ("Access", access_fn, False)
    ]
    
    header.add_nav_items(nav_items)

    # 4. Add Profile
    header.add_profile()