import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class ActionGrid(tk.Frame):
    def __init__(self, parent, columns, edit_command=None, delete_command=None):
        super().__init__(parent, bg="white")
        self.columns = columns  # Format: (key, title, weight_int)
        self.edit_cmd = edit_command
        self.delete_cmd = delete_command
        self.hover_color = "#EBF5FB"
        self.row_widgets = {}

        # --- IMAGE LOADING ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../../../")) 
        assets_dir = os.path.join(project_root, "assets")

        self.icon_edit = self.load_icon(os.path.join(assets_dir, "edit.png"))
        self.icon_delete = self.load_icon(os.path.join(assets_dir, "delete.png"))

        # --- HEADER FRAME ---
        self.header_frame = tk.Frame(self, bg="#EAECEE", height=40, pady=0)
        self.header_frame.pack(fill="x")
        
        # --- BODY (SCROLLABLE) ---
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        self.body_frame = tk.Frame(self.canvas, bg="white")
        
        self.body_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.frame_id = self.canvas.create_window((0, 0), window=self.body_frame, anchor="nw")
        
        # FORCE FULL WIDTH
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.frame_id, width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # ============================================================
        # ALIGNMENT ENGINE (The Fix)
        # We apply the EXACT SAME grid configuration to Header & Body
        # ============================================================
        
        # 1. Setup Data Columns
        for i, (_, col_title, weight) in enumerate(self.columns):
            # Calculate a minimum width based on weight to prevent crushing
            # Weight 1 -> 80px, Weight 3 -> 240px
            min_w = weight * 80 
            
            # Configure Header
            self.header_frame.grid_columnconfigure(i, weight=weight, minsize=min_w)
            lbl = tk.Label(self.header_frame, text=col_title, font=("Segoe UI", 10, "bold"), 
                           bg="#EAECEE", fg="#333", anchor="w")
            lbl.grid(row=0, column=i, sticky="ew", padx=5)

            # Configure Body (Identical Settings)
            self.body_frame.grid_columnconfigure(i, weight=weight, minsize=min_w)

        # 2. Setup Action Column (Fixed Width)
        action_col_idx = len(self.columns)
        self.header_frame.grid_columnconfigure(action_col_idx, weight=0, minsize=100)
        self.body_frame.grid_columnconfigure(action_col_idx, weight=0, minsize=100)
        
        tk.Label(self.header_frame, text="Actions", font=("Segoe UI", 10, "bold"), 
                 bg="#EAECEE", fg="#333", anchor="center").grid(row=0, column=action_col_idx, sticky="ew", padx=9)

    def load_icon(self, path):
        if not os.path.exists(path): return None
        try:
            img = Image.open(path).resize((18, 18), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except: return None

    def render_data(self, data_list):
        for widget in self.body_frame.winfo_children(): widget.destroy()
        self.row_widgets = {}

        if not data_list:
            tk.Label(self.body_frame, text="No records found", bg="white", pady=20).grid(row=0, column=0, columnspan=len(self.columns)+1)
            return

        colors = ["white", "#F8F9F9"]

        for row_idx, row_data in enumerate(data_list):
            bg_color = colors[row_idx % 2]
            current_widgets = [] 

            # --- RENDER COLUMNS ---
            for col_idx, (col_key, _, _) in enumerate(self.columns):
                val = str(row_data.get(col_key, "-"))
                if len(val) > 40: val = val[:37] + "..."
                
                # CRITICAL FIX: 
                # padx=10 IS INSIDE THE LABEL constructor.
                # grid(padx=0) ensures cells touch each other.
                lbl = tk.Label(self.body_frame, text=val, font=("Segoe UI", 10), 
                               bg=bg_color, fg="#555", anchor="w", 
                               pady=12, padx=10) 
                
                # sticky="nsew" forces the background to fill the grid cell completely
                lbl.grid(row=row_idx, column=col_idx, sticky="nsew", padx=0, pady=0)
                
                current_widgets.append(lbl)

            # --- ACTION COLUMN ---
            action_frame = tk.Frame(self.body_frame, bg=bg_color)
            action_frame.grid(row=row_idx, column=len(self.columns), sticky="nsew", padx=0, pady=0)
            current_widgets.append(action_frame)

            # Center container for buttons
            btn_container = tk.Frame(action_frame, bg=bg_color)
            btn_container.pack(expand=True) # Centers vertically/horizontally
            current_widgets.append(btn_container)

            # Buttons
            if self.icon_edit:
                btn_edit = tk.Button(btn_container, image=self.icon_edit, bg=bg_color, bd=0, cursor="hand2",
                                     activebackground=bg_color, command=lambda d=row_data: self.edit_cmd(d))
                btn_edit.image = self.icon_edit
                btn_edit.pack(side="left", padx=5)
                current_widgets.append(btn_edit)

            if self.icon_delete:
                btn_del = tk.Button(btn_container, image=self.icon_delete, bg=bg_color, bd=0, cursor="hand2",
                                    activebackground=bg_color, command=lambda d=row_data: self.delete_cmd(d))
                btn_del.image = self.icon_delete
                btn_del.pack(side="left", padx=5)
                current_widgets.append(btn_del)

            # --- HOVER LOGIC ---
            self.row_widgets[row_idx] = (current_widgets, bg_color)
            for w in current_widgets:
                w.bind("<Enter>", lambda e, r=row_idx: self.on_enter(r))
                w.bind("<Leave>", lambda e, r=row_idx: self.on_leave(r))

    def on_enter(self, row_idx):
        if row_idx in self.row_widgets:
            widgets, _ = self.row_widgets[row_idx]
            for w in widgets:
                try: w.configure(bg=self.hover_color)
                except: pass

    def on_leave(self, row_idx):
        if row_idx in self.row_widgets:
            widgets, original_bg = self.row_widgets[row_idx]
            for w in widgets:
                try: w.configure(bg=original_bg)
                except: pass