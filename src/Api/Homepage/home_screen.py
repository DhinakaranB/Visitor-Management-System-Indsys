import os
import tkinter as tk
from PIL import Image, ImageTk

BG_COLOR = "#D6EAF8"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#2C3EFA"


def load_home_screen(content_frame):
    """Render the Home Page with background image."""
    for w in content_frame.winfo_children():
        w.destroy()

    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    container = tk.Frame(content_frame, bg=BG_COLOR)
    container.grid(row=0, column=0, sticky="nsew")

    canvas = tk.Canvas(container, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)

    # 🔥 Correct path (image in same folder)
    img_path = os.path.join(os.path.dirname(__file__), "bg_png.jpg")
    canvas._store = {"pil": None, "tk": None, "path": img_path}

    def redraw(event=None):
        try:
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 10 or h < 10:
                return

            canvas.delete("all")

            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                
                # ---------------------------------------------------------
                # FIX: Resize to full width (w) AND full height (h)
                # ---------------------------------------------------------
                pil_img = pil_img.resize((w, h), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil_img)

                canvas._store["pil"] = pil_img
                canvas._store["tk"] = tk_img

                # Draw image starting at top-left
                canvas.create_image(0, 0, anchor="nw", image=tk_img)

                # ---------------------------------------------------------
                # TEXT POSITIONING (Centered on full screen)
                # ---------------------------------------------------------
                canvas.create_text(
                    w // 2,
                    h * 0.45,  # Slightly above center
                    text="Welcome to Visitor Management System",
                    font=("Segoe UI", 28, "bold"),
                    fill=PRIMARY_COLOR
                )

                canvas.create_text(
                    w // 2,
                    h * 0.55,  # Slightly below center
                    text="Use the navigation bar above to manage visitor appointments and access control.",
                    font=("Segoe UI", 12),
                    fill=TEXT_COLOR
                )

            else:
                # Fallback if image is missing
                canvas.create_text(
                    w // 2, h // 3,
                    text="Welcome to Visitor Management System",
                    font=("Segoe UI", 28, "bold"),
                    fill=PRIMARY_COLOR
                )

        except Exception as e:
            print("Home bg error:", e)

    canvas.bind("<Configure>", redraw)
    # Trigger redraw immediately to load image
    canvas.after(50, redraw)