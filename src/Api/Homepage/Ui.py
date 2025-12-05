import tkinter as tk
from tkinter import ttk, messagebox
import os, sys
from PIL import Image, ImageTk
# -----------------------------------------
# SAFE IMPORT HANDLING
# -----------------------------------------
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

try:
    from src.Api.visitor_screen import visitor_registerment as visitor_form
    from src.Api.visitor_screen import visitor_list_Info as visitor_list
    from src.Api.Common_signature import common_signature_api
    from src.Api.Door_screen import door_list_Info as door_list
    from src.Api.Door_screen import linked_door_info as linked_doors
    from src.Api.Homepage.home_screen import load_home_screen
except Exception as e:
    print("IMPORT ERROR:", e)

    class MockAPI:
        def show_create_form(*a): print("Mock: show_create_form")
        def show_single_visitor_list(*a): print("Mock: show_single_visitor_list")
        def show_door_list(*a): print("Mock: show_door_list")
        def show_linked_doors(*a): print("Mock: show_linked_doors")

    visitor_form = MockAPI()
    visitor_list = MockAPI()
    door_list = MockAPI()
    linked_doors = MockAPI()

    # IMPORTANT FALLBACK (missing earlier)
    def load_home_screen(*args, **kwargs):
        print("Mock: load_home_screen (Home screen import failed!)")



# -----------------------------------------
# COLORS
# -----------------------------------------
BG_COLOR = "#D6EAF8"
NAVBAR_BLUE = "#0A74FF"
WHITE = "#FFFFFF"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#2C3EFA"

GRADIENT_START = (99, 66, 255)
GRADIENT_END   = (255, 102, 178)

root = None
content_frame = None
nav = None
login_frame = None

username_entry = None
password_entry = None


# -----------------------------------------
# GRADIENT ENGINE
# -----------------------------------------
def rgb_to_hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"

def lerp(a, b, t):
    return int(a + (b - a) * t)

def draw_vertical_gradient(c, x, y, w, h, start_rgb, end_rgb, steps=200):
    for i in range(steps):
        t = i / (steps - 1)
        r = lerp(start_rgb[0], end_rgb[0], t)
        g = lerp(start_rgb[1], end_rgb[1], t)
        b = lerp(start_rgb[2], end_rgb[2], t)
        color = rgb_to_hex(r, g, b)
        y0 = y + int(i * (h / steps))
        y1 = y + int((i + 1) * (h / steps))
        c.create_rectangle(x, y0, x + w, y1, outline=color, fill=color)


# -----------------------------------------
# MAIN CONTENT SCREENS
# -----------------------------------------
def clear_content():
    if content_frame:
        for w in content_frame.winfo_children():
            w.destroy()

def close_application():
    root.destroy()

def show_home():
    load_home_screen(content_frame)    

def show_add_visitor():
    clear_content()
    visitor_form.show_create_form(content_frame, show_home, close_application)

def show_single_visitor_list_external():
    clear_content()
    visitor_list.show_single_visitor_list(content_frame)

def show_door_list():
    clear_content()
    door_list.show_door_list(content_frame)

def show_linked_doors():
    clear_content()
    linked_doors.show_linked_doors(content_frame)


# -----------------------------------------
# DROPDOWN
# -----------------------------------------
def open_door_dropdown(widget):
    menu = tk.Toplevel(root)
    menu.overrideredirect(True)
    menu.config(bg="white")

    x = widget.winfo_rootx()
    y = widget.winfo_rooty() + widget.winfo_height()
    menu.geometry(f"180x120+{x}+{y}")

    def item(txt, cmd):
        lbl = tk.Label(menu, text=txt, bg="white", fg="#1F2D3D",
                       font=("Segoe UI",10), padx=10, pady=7, anchor="w")
        lbl.pack(fill="x")
        lbl.bind("<Enter>", lambda e: lbl.config(bg="#EEF3FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(bg="white"))
        lbl.bind("<Button-1>", lambda e: (menu.destroy(), cmd()))

    item("🚪 Door List", show_door_list)
    item("🔗 Linked Doors", show_linked_doors)

    menu.bind("<FocusOut>", lambda e: menu.destroy())


# -----------------------------------------
# NAVBAR
# -----------------------------------------
def setup_navbar():
    global nav

    nav = tk.Frame(root, bg=NAVBAR_BLUE, height=55)
    nav.grid_propagate(False)

    left = tk.Frame(nav, bg=NAVBAR_BLUE)
    left.pack(side="left", fill="y")

    tk.Label(left, text="VisitorMS", bg=NAVBAR_BLUE, fg=WHITE,
             font=("Segoe UI",15,"bold"), padx=18).pack(side="left")

    def menu(text, cmd=None):
        lbl = tk.Label(left, text=text, bg=NAVBAR_BLUE, fg=WHITE,
                       font=("Segoe UI",11), padx=15, cursor="hand2")
        lbl.pack(side="left")
        lbl.bind("<Enter>", lambda e: lbl.config(fg="#DCE6FF"))
        lbl.bind("<Leave>", lambda e: lbl.config(fg=WHITE))
        if cmd:
            lbl.bind("<Button-1>", lambda e: cmd())
        return lbl

    menu("Home", show_home)
    menu("Add Visitor", show_add_visitor)
    menu("Visitor List", show_single_visitor_list_external)

    d = menu("Door ▼")
    d.bind("<Button-1>", lambda e: open_door_dropdown(d))

    menu("Access Control", lambda: None)

    return nav


# -----------------------------------------
# LOGIN VALIDATION
# -----------------------------------------
def validate_login():
    global nav

    user = username_entry.get().strip()
    pwd  = password_entry.get().strip()

    if user == "admin" and pwd == "1234":
        login_frame.destroy()

        nav.grid(row=0, column=0, sticky="ew")
        content_frame.grid(row=1, column=0, sticky="nsew")
        show_home()

        footer = root.grid_slaves(row=2)
        if footer:
            footer[0].grid()

    else:
        messagebox.showerror("Error", "Invalid Login! Use admin / 1234")



# -----------------------------------------
# MODERN LOGIN SCREEN (FINAL FIXED VERSION)
# -----------------------------------------
def show_login_screen():
    global login_frame, username_entry, password_entry

    try:
        login_frame.destroy()
    except:
        pass

    login_frame = tk.Frame(root, bg=BG_COLOR)
    login_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")

    login_frame.grid_columnconfigure(0, weight=6)
    login_frame.grid_columnconfigure(1, weight=4)
    login_frame.grid_rowconfigure(0, weight=1)

    # -----------------------
    # LEFT GRADIENT PANEL
    # -----------------------
    left_canvas = tk.Canvas(login_frame, highlightthickness=0, bd=0)
    left_canvas.grid(row=0, column=0, sticky="nsew")

    def draw_left(event=None):
        left_canvas.delete("all")
        w = left_canvas.winfo_width()
        h = left_canvas.winfo_height()

        if w < 60 or h < 60:
            return

        draw_vertical_gradient(left_canvas, 0, 0, w, h,
                               GRADIENT_START, GRADIENT_END, steps=220)

        left_canvas.create_text(
            int(w*0.08), int(h*0.25),
            anchor="w",
            text="Welcome to Visitor Management System",
            font=("Segoe UI",28,"bold"),
            fill="white"
        )

        left_canvas.create_text(
            int(w*0.08), int(h*0.34),
            anchor="w",
            text="Manage visitors & access control\nwith a clean modern UI.",
            font=("Segoe UI",12),
            fill="#FFEFFF"
        )

    left_canvas.bind("<Configure>", draw_left)

    # -----------------------
    # RIGHT LOGIN CARD
    # -----------------------
    right = tk.Frame(login_frame, bg=BG_COLOR)
    right.grid(row=0, column=1, sticky="nsew")

    card = tk.Frame(right, bg="white")
    card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=360)

    tk.Label(card, text="USER LOGIN", bg="white",
             fg="#777", font=("Segoe UI",9,"bold")).pack(pady=(16,6))
    tk.Label(card, text="Welcome Back 👋", bg="white",
             fg=TEXT_COLOR, font=("Segoe UI",18,"bold")).pack()
    tk.Label(card, text="Sign in to continue", bg="white",
             fg="#888", font=("Segoe UI",10)).pack(pady=(4,20))

    # Username
    f1 = tk.Frame(card, bg="white")
    f1.pack(padx=25, fill="x")
    tk.Label(f1, text="👤", bg="white").pack(side="left")
    username_entry = tk.Entry(f1, bd=0, font=("Segoe UI",11))
    username_entry.pack(side="left", fill="x", expand=True, ipady=7)
    tk.Frame(card, height=1, bg="#E1E1E1").pack(fill="x", padx=25, pady=(4,12))

    # Password
    f2 = tk.Frame(card, bg="white")
    f2.pack(padx=25, fill="x")
    tk.Label(f2, text="🔒", bg="white").pack(side="left")
    password_entry = tk.Entry(f2, show="*", bd=0, font=("Segoe UI",11))
    password_entry.pack(side="left", fill="x", expand=True, ipady=7)
    tk.Frame(card, height=1, bg="#E1E1E1").pack(fill="x", padx=25, pady=(4,16))

    tk.Button(card, text="LOGIN", bg=PRIMARY_COLOR, fg="white",
              font=("Segoe UI",11,"bold"),
              command=validate_login,
              relief="flat").pack(ipadx=12, ipady=6)

    username_entry.focus()


# -----------------------------------------
# MAIN UI INIT
# -----------------------------------------
def init_ui():
    global root, content_frame, nav

    root.title("Visitor Management System")
    root.geometry("1100x750")
    root.configure(bg=BG_COLOR)

    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=0)
    root.grid_columnconfigure(0, weight=1)

    nav = setup_navbar()
    nav.grid_remove()

    content_frame = tk.Frame(root, bg=BG_COLOR)

    footer = tk.Label(root, text="© 2025 Indsys Holdings - All rights reserved.",
                      font=("Segoe UI",9), bg=BG_COLOR, fg="#777")
    footer.grid(row=2, column=0, pady=8)
    footer.grid_remove()

    show_login_screen()


# -----------------------------------------
# BOOT
# -----------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    init_ui()
    root.mainloop()
