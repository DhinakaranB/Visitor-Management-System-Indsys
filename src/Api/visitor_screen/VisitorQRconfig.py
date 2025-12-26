import tkinter as tk
from tkinter import ttk, messagebox
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
BG_COLOR = "#F4F6F7"        # Light Gray App Background
CARD_BG = "#FFFFFF"         # White Card Background
PRIMARY_COLOR = "#3498DB"   # Blue Button
TEXT_COLOR = "#2C3E50"      # Dark Text
LABEL_COLOR = "#7F8C8D"     # Gray Labels

API_QR_GET = "/artemis/api/visitor/v1/visitor/qr/get"

# ================= MAIN SCREEN UI =================
def show_qr_screen(root_instance, show_main_menu_callback=None):
    """
    Renders the 'Get Visitor QR Code' screen.
    """
    # 1. Reset Screen
    for widget in root_instance.winfo_children():
        widget.destroy()
    root_instance.configure(bg=BG_COLOR)

    # 2. Header Bar
    header_frame = tk.Frame(root_instance, bg="white", pady=15, padx=20)
    header_frame.pack(fill="x")

    if show_main_menu_callback:
        tk.Button(header_frame, text="← Back", command=show_main_menu_callback, 
                  bg="white", fg=LABEL_COLOR, bd=0, font=("Segoe UI", 10), cursor="hand2").pack(side="left")
    
    tk.Label(header_frame, text="  |  Get Visitor QR Code", font=("Segoe UI", 18, "bold"), 
             bg="white", fg=TEXT_COLOR).pack(side="left")

    # 3. Main Content Container
    content_frame = tk.Frame(root_instance, bg=BG_COLOR)
    content_frame.pack(fill="both", expand=True)

    # --- CARD CONTAINER ---
    card = tk.Frame(content_frame, bg=CARD_BG, padx=40, pady=40, bd=1, relief="solid")
    card.place(relx=0.5, rely=0.45, anchor="center", width=600, height=600)

    # Title
    tk.Label(card, text="Generate QR Pass", font=("Segoe UI", 16, "bold"), 
             bg=CARD_BG, fg=PRIMARY_COLOR).pack(pady=(0, 25))

    # --- INPUT SECTION ---
    input_frame = tk.Frame(card, bg=CARD_BG)
    input_frame.pack(fill="x", padx=10)
    input_frame.columnconfigure(0, weight=1)

    tk.Label(input_frame, text="Enter Visitor ID:", font=("Segoe UI", 10, "bold"), 
             bg=CARD_BG, fg=TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=(0, 5))

    entry_id = ttk.Entry(input_frame, font=("Segoe UI", 11))
    entry_id.grid(row=1, column=0, sticky="ew", padx=(0, 10), ipady=5) 
    
    # Generate Button
    btn_gen = tk.Button(input_frame, text="GENERATE", bg=PRIMARY_COLOR, fg="white", 
                        font=("Segoe UI", 10, "bold"), bd=0, cursor="hand2", padx=20,
                        command=lambda: fetch_qr_logic(entry_id.get(), qr_label, status_lbl))
    btn_gen.grid(row=1, column=1, sticky="ns") 

    ttk.Separator(card, orient="horizontal").pack(fill="x", pady=30)

    # --- OUTPUT SECTION (IMAGE BOX) ---
    tk.Label(card, text="QR Code Preview", font=("Segoe UI", 10, "bold"), 
             bg=CARD_BG, fg=LABEL_COLOR).pack(anchor="center", pady=(0, 10))

    qr_border = tk.Frame(card, bg="#F0F0F0", bd=1, relief="solid", width=250, height=250)
    qr_border.pack()
    qr_border.pack_propagate(False)

    qr_label = tk.Label(qr_border, text="[ QR Code ]", bg="#FAFAFA", fg="#AAA", font=("Segoe UI", 10))
    qr_label.place(relx=0.5, rely=0.5, anchor="center")

    status_lbl = tk.Label(card, text="", font=("Segoe UI", 9), bg=CARD_BG, fg=TEXT_COLOR)
    status_lbl.pack(pady=(15, 0))
    
    entry_id.focus()


# ================= LOGIC HANDLERS =================
def fetch_qr_logic(visitor_id, image_label, status_label):
    visitor_id = visitor_id.strip()
    if not visitor_id:
        messagebox.showwarning("Validation", "Please enter a Visitor ID.")
        return

    # Update UI to Loading
    status_label.config(text="Fetching QR Code...", fg=PRIMARY_COLOR)
    image_label.config(image="", text="Loading...")
    
    def api_thread():
        if not api_handler:
            update_ui_error(status_label, image_label, "API Handler not connected.")
            return

        payload = {"visitorId": visitor_id}
        
        # 1. Call API
        res = api_handler.call_api(API_QR_GET, payload)

        if res and str(res.get("code")) == "0":
            data = res.get("data", {})
            
            # 2. Extract Base64 String
            # Try finding it inside 'qrCodeInfo' first
            qr_info = data.get("qrCodeInfo") or data.get("qRCodeInfo") or {}
            qr_base64 = qr_info.get("qrCodeImage")
            
            # Fallback
            if not qr_base64:
                qr_base64 = data.get("qrCodeImage") or data.get("qrCode")

            if qr_base64:
                try:
                    # 3. CONVERT STRING TO IMAGE
                    qr_base64 = qr_base64.replace("\n", "").strip()
                    image_data = base64.b64decode(qr_base64)
                    
                    # Create PIL Image
                    pil_image = Image.open(BytesIO(image_data))
                    pil_image = pil_image.resize((230, 230), Image.Resampling.LANCZOS)
                    
                    # 4. SEND TO MAIN THREAD FOR DISPLAY
                    # We send the PIL object, NOT the PhotoImage (to avoid thread crash)
                    image_label.after(0, lambda: update_ui_success(image_label, status_label, pil_image, visitor_id))
                    
                except Exception as e:
                    image_label.after(0, lambda: update_ui_error(status_label, image_label, f"Image Error: {e}"))
            else:
                image_label.after(0, lambda: update_ui_error(status_label, image_label, "No QR Image found in response"))
        else:
            msg = res.get("msg", "Unknown Error") if res else "Connection Failed"
            image_label.after(0, lambda: update_ui_error(status_label, image_label, msg))

    threading.Thread(target=api_thread, daemon=True).start()

def update_ui_success(img_lbl, stat_lbl, pil_image, vid):
    """
    Called on Main Thread. Converts PIL image to Tkinter PhotoImage.
    """
    try:
        # Convert PIL -> Tkinter
        photo = ImageTk.PhotoImage(pil_image)
        
        img_lbl.config(image=photo, text="", width=250, height=250)
        img_lbl.image = photo # Keep Reference!
        stat_lbl.config(text=f"✅ QR Generated for ID: {vid}", fg="#27AE60")
    except Exception as e:
        stat_lbl.config(text=f"Display Error: {e}", fg="red")

def update_ui_error(stat_lbl, img_lbl, msg):
    stat_lbl.config(text=msg, fg="red")
    img_lbl.config(text="[ Error ]", image="")

# ================= COMPATIBILITY WRAPPER =================
def render_qr_config(parent):
    def dummy_back(): pass
    show_qr_screen(parent, dummy_back)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x700")
    render_qr_config(root)
    root.mainloop()