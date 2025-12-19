import tkinter as tk
from tkinter import ttk, messagebox
import base64
from io import BytesIO
from PIL import Image, ImageTk  # Requires: pip install pillow

# Try to import your API handler
try:
    import Api.Common_signature.common_signature_api as api_handler
except ImportError:
    api_handler = None
    print("⚠️ Warning: api_handler not found. Make sure the 'Api' folder is in the same directory.")

# --- CONFIG ---
BG_COLOR = "#F4F6F7"
HEADER_TEXT = "#2C3E50"
API_QR_GET = "/artemis/api/visitor/v1/visitor/qr/get"

def render_qr_config(parent):
    """
    Renders the Visitor QR Config tab inside the parent frame.
    """
    frame = tk.Frame(parent, bg=BG_COLOR, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    # Title
    tk.Label(frame, text="Get Visitor QR Code", font=("Segoe UI", 16, "bold"), 
             bg=BG_COLOR, fg=HEADER_TEXT).pack(anchor="w", pady=(0, 20))

    # --- Input Area ---
    input_frame = tk.Frame(frame, bg=BG_COLOR)
    input_frame.pack(anchor="w")

    tk.Label(input_frame, text="Visitor ID:", bg=BG_COLOR, font=("Segoe UI", 10)).grid(row=0, column=0, padx=5, pady=5)
    vid_entry = ttk.Entry(input_frame, width=25)
    vid_entry.grid(row=0, column=1, padx=5, pady=5)

    # --- Image Display Area ---
    # Placeholder label
    qr_label = tk.Label(frame, bg="white", text="[ QR Code will appear here ]", 
                        relief="sunken", width=30, height=15)
    qr_label.pack(pady=30)

    def get_qr():
        vid = vid_entry.get().strip()
        if not vid:
            messagebox.showwarning("Input", "Please enter a Visitor ID")
            return

        payload = {"visitorId": vid}
        
        if api_handler:
            res = api_handler.call_api(API_QR_GET, payload)
            
            if res and res.get("code") == "0":
                data = res.get("data", {})
                # API might return 'qrCode' or 'qrCodeImage' depending on version
                qr_base64 = data.get("qrCode") or data.get("qrCodeImage")
                
                if qr_base64:
                    try:
                        # Decode Base64 string to Image
                        image_data = base64.b64decode(qr_base64)
                        image = Image.open(BytesIO(image_data))
                        
                        # Resize for better display
                        image = image.resize((250, 250), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        
                        # Update Label
                        qr_label.config(image=photo, text="", width=250, height=250)
                        qr_label.image = photo  # Keep a reference to prevent garbage collection!
                    except Exception as e:
                        qr_label.config(text="Error decoding image")
                        print(f"Image Error: {e}")
                else:
                    messagebox.showinfo("Info", "No QR Code data found for this user.")
            else:
                # Handle specific error codes if needed
                err_msg = res.get("msg", "Unknown Error")
                if "60151" in str(res):
                    err_msg += "\n\nHint: Check if the Visitor ID is correct and has 'Pass' permissions."
                messagebox.showerror("API Error", err_msg)
        else:
            messagebox.showerror("Error", "API Handler not connected.")

    # Generate Button
    tk.Button(input_frame, text="Generate QR", command=get_qr, bg="#2ECC71", fg="white", 
              font=("Segoe UI", 9, "bold")).grid(row=0, column=2, padx=15)

# Self-test block
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x500")
    render_qr_config(root)
    root.mainloop()