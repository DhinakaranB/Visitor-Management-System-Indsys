import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import base64
from io import BytesIO
import threading

# Try to import your API handler
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None

# ================= CONFIGURATION =================
BG_COLOR = "#F4F6F7"        # Light Gray Background
CARD_BG = "#FFFFFF"         # White Card Background
PRIMARY_COLOR = "#3498DB"   # Blue
TEXT_COLOR = "#2C3E50"      # Dark Text
LABEL_COLOR = "#7F8C8D"     # Gray Labels

API_QR_GET = "/artemis/api/visitor/v1/visitor/qr/get"

# ================= MAIN SCREEN UI =================
def show_qr_screen(root_instance, show_main_menu_callback=None):
    """
    Renders the 'Get Visitor QR Code' screen with a Professional Side-by-Side Layout.
    """
    # 1. Reset Screen
    for widget in root_instance.winfo_children():
        widget.destroy()
    root_instance.configure(bg=BG_COLOR)

    # 2. Header Bar
    header_frame = tk.Frame(root_instance, bg="white", pady=15, padx=20)
    header_frame.pack(fill="x")

    def on_back():
        if show_main_menu_callback:
            show_main_menu_callback()
        else:
            messagebox.showinfo("Navigation", "Back button pressed (Callback missing)")

    btn_back = tk.Button(header_frame, text="← Back to Home", 
                         command=on_back, 
                         bg="white", fg=PRIMARY_COLOR, bd=0, 
                         font=("Segoe UI", 10, "bold"), cursor="hand2")
    btn_back.pack(side="left")
    
    tk.Label(header_frame, text="  |  Get Visitor QR Code", font=("Segoe UI", 18, "bold"), 
             bg="white", fg=TEXT_COLOR).pack(side="left")

    # 3. Main Content Container
    content_frame = tk.Frame(root_instance, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True)

    # --- CARD CONTAINER ---
    # Fixed Width (900px) - Looks professional, not stretched.
    # Height automatic based on content.
    card = tk.Frame(content_frame, bg=CARD_BG, padx=30, pady=30, bd=1, relief="solid")
    card.place(relx=0.5, rely=0.5, anchor="center", width=900, height=500)

    # --- TITLE ---
    tk.Label(card, text="Generate QR Pass", font=("Segoe UI", 18, "bold"), 
             bg=CARD_BG, fg=PRIMARY_COLOR).pack(pady=(0, 30))

    # --- SPLIT LAYOUT CONTAINER ---
    split_frame = tk.Frame(card, bg=CARD_BG)
    split_frame.pack(fill="both", expand=True)
    
    # Configure 2 Columns: Left (Input) - Separator - Right (Output)
    split_frame.columnconfigure(0, weight=1) # Left
    split_frame.columnconfigure(1, weight=0) # Line
    split_frame.columnconfigure(2, weight=1) # Right

    # ================= LEFT SIDE: INPUTS =================
    left_panel = tk.Frame(split_frame, bg=CARD_BG, padx=20)
    left_panel.grid(row=0, column=0, sticky="nsew")

    tk.Label(left_panel, text="Step 1: Enter Details", font=("Segoe UI", 12, "bold"), 
             bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 20))

    tk.Label(left_panel, text="Visitor ID:", font=("Segoe UI", 10, "bold"), 
             bg=CARD_BG, fg=LABEL_COLOR).pack(anchor="w", pady=(0, 5))

    entry_id = ttk.Entry(left_panel, font=("Segoe UI", 12))
    entry_id.pack(fill="x", ipady=8, pady=(0, 20)) # Taller input box
    
    btn_gen = tk.Button(left_panel, text="GENERATE QR CODE ➤", bg=PRIMARY_COLOR, fg="white", 
                        font=("Segoe UI", 11, "bold"), bd=0, cursor="hand2", pady=10,
                        command=lambda: fetch_qr_logic(entry_id.get(), qr_label, status_lbl, btn_download))
    btn_gen.pack(fill="x")
    
    # Status Message (Left Side)
    status_lbl = tk.Label(left_panel, text="", font=("Segoe UI", 10), bg=CARD_BG, fg=TEXT_COLOR, wraplength=300)
    status_lbl.pack(pady=(20, 0))

    # ================= CENTER: SEPARATOR =================
    ttk.Separator(split_frame, orient="vertical").grid(row=0, column=1, sticky="ns", padx=20)

    # ================= RIGHT SIDE: OUTPUT =================
    right_panel = tk.Frame(split_frame, bg=CARD_BG, padx=20)
    right_panel.grid(row=0, column=2, sticky="nsew")

    tk.Label(right_panel, text="Step 2: Preview & Download", font=("Segoe UI", 12, "bold"), 
             bg=CARD_BG, fg=TEXT_COLOR).pack(anchor="center", pady=(0, 20))

    # QR Box
    qr_border = tk.Frame(right_panel, bg="#F0F0F0", bd=1, relief="solid", width=220, height=220)
    qr_border.pack(anchor="center")
    qr_border.pack_propagate(False)

    qr_label = tk.Label(qr_border, text="[ QR Code Preview ]", bg="#FAFAFA", fg="#AAA", font=("Segoe UI", 10))
    qr_label.place(relx=0.5, rely=0.5, anchor="center")

    # Download Button (Hidden initially or disabled)
    btn_download = tk.Button(right_panel, text="⬇ Download Image", bg="white", fg=PRIMARY_COLOR, 
                             font=("Segoe UI", 10, "bold"), bd=1, relief="solid", cursor="hand2",
                             state="disabled", # Disabled until generated
                             command=lambda: download_qr(qr_label))
    btn_download.pack(pady=(20, 0), ipadx=20, ipady=5)

    entry_id.focus()

# ================= LOGIC HANDLERS =================
def fetch_qr_logic(visitor_id, image_label, status_label, download_btn):
    visitor_id = visitor_id.strip()
    if not visitor_id:
        messagebox.showwarning("Validation", "Please enter a Visitor ID.")
        return

    status_label.config(text="Contacting Server...", fg=PRIMARY_COLOR)
    image_label.config(image="", text="Loading...")
    download_btn.config(state="disabled", bg="#f0f0f0")
    
    def api_thread():
        if not api_handler:
            update_ui_error(status_label, image_label, "API Handler not connected.")
            return

        payload = {"visitorId": visitor_id, "validDuration": 300} # 5 Mins
        res = api_handler.call_api(API_QR_GET, payload)

        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            qr_info = data.get("qrCodeInfo") or data.get("qRCodeInfo") or {}
            qr_base64 = qr_info.get("qrCodeImage") or data.get("qrCodeImage") or data.get("qrCode")

            if qr_base64:
                try:
                    qr_base64 = qr_base64.replace("\n", "").strip()
                    image_data = base64.b64decode(qr_base64)
                    pil_image = Image.open(BytesIO(image_data))
                    pil_image = pil_image.resize((200, 200), Image.Resampling.LANCZOS)
                    
                    image_label.after(0, lambda: update_ui_success(image_label, status_label, pil_image, visitor_id, download_btn))
                except Exception as e:
                    image_label.after(0, lambda: update_ui_error(status_label, image_label, f"Image Error: {e}"))
            else:
                image_label.after(0, lambda: update_ui_error(status_label, image_label, "No QR Image found"))
        else:
            msg = res.get("msg", "Unknown Error") if res else "Connection Failed"
            image_label.after(0, lambda: update_ui_error(status_label, image_label, msg))

    threading.Thread(target=api_thread, daemon=True).start()

def update_ui_success(img_lbl, stat_lbl, pil_image, vid, dl_btn):
    try:
        photo = ImageTk.PhotoImage(pil_image)
        img_lbl.config(image=photo, text="", width=220, height=220)
        img_lbl.image = photo 
        img_lbl.current_pil_image = pil_image 
        
        stat_lbl.config(text=f"✅ Success!\nQR Generated for ID: {vid}", fg="#27AE60")
        dl_btn.config(state="normal", bg="white") # Enable Download
    except Exception as e:
        stat_lbl.config(text=f"Display Error: {e}", fg="red")

def update_ui_error(stat_lbl, img_lbl, msg):
    stat_lbl.config(text=msg, fg="red")
    img_lbl.config(text="[ Error ]", image="")

# ================= DOWNLOAD FUNCTION =================
def download_qr(img_lbl):
    if not hasattr(img_lbl, 'current_pil_image'): return
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")], title="Save QR")
    if file_path:
        try:
            img_lbl.current_pil_image.save(file_path)
            messagebox.showinfo("Success", "Saved Successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# ================= WRAPPER =================
def render_qr_config(parent, back_callback=None):
    show_qr_screen(parent, back_callback)