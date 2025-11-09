# common_api.py

import requests
import hmac
import hashlib
import base64
import json
import urllib3
from tkinter import messagebox
import tkinter as tk

# Suppress InsecureRequestWarning for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Artemis API Details (Constants) ---
APP_KEY = "11566257"
APP_SECRET = "DBntId5f4LZPfW1Ik5Yh"
HOST = "127.0.0.1"
BASE_URL = f"https://{HOST}" 

def create_signature(method, body, api_path):
    """Creates the necessary HMAC-SHA256 signature and headers for the API request."""
    accept = "application/json"
    content_type = "application/json;charset=UTF-8"

    # Use the JSON body directly for MD5 hash
    content_md5 = base64.b64encode(hashlib.md5(body.encode('utf-8')).digest()).decode('utf-8')
    signature_headers = "x-ca-key"
    headers_to_sign = f"x-ca-key:{APP_KEY}\n"

    string_to_sign = (
        f"{method}\n"
        f"{accept}\n"
        f"{content_md5}\n"
        f"{content_type}\n"
        f"{headers_to_sign}"
        f"{api_path}" # Use the dynamic path here
    )

    hmac_sha256 = hmac.new(APP_SECRET.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha256)
    signature = base64.b64encode(hmac_sha256.digest()).decode('utf-8')

    headers = {
        "Accept": accept,
        "Content-MD5": content_md5,
        "Content-Type": content_type,
        "X-Ca-Key": APP_KEY,
        "X-Ca-Signature-Headers": signature_headers,
        "X-Ca-Signature": signature
    }
    return headers

def send_to_api(data_payload, api_path, clear_callback):
    """
    Sends the data payload to the API using the specified path and handles responses.
    
    Args:
        data_payload (dict): The structured data ready for JSON conversion.
        api_path (str): The specific endpoint path (e.g., /artemis/api/visitor/...).
        clear_callback (function): Function to clear the form entries on success.
    """
    try:
        body = json.dumps(data_payload)
        headers = create_signature("POST", body, api_path)
        
        URL = f"{BASE_URL}{api_path}" # Construct the full URL
        
        # Note: verify=False is used due to the self-signed certificate on localhost (127.0.0.1)
        response = requests.post(URL, headers=headers, data=body, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                res = response.json()
            except json.JSONDecodeError:
                messagebox.showerror("Response Error", f"Failed to parse JSON response. Text: {response.text}")
                return

            api_code = res.get("code")
            api_msg = res.get("msg", "Unknown error")
            api_data = res.get("data", "")
            
            # --- SUCCESS CHECK (API Code "0") ---
            if api_code == "0":
                data = res["data"]
                appoint_id = data["appointRecordId"]
                visitor_id = data["visitorId"]
                qr_data = data.get("qrCodeImage")

                qr_message = "No QR code received."
                if qr_data:
                    try:
                        file_name = f"visitor_qr_{appoint_id}.png"
                        # NOTE: Ensure the environment allows file writing.
                        with open(file_name, "wb") as img:
                            img.write(base64.b64decode(qr_data))
                        qr_message = f"QR saved as {file_name}"
                    except Exception as qr_e:
                        qr_message = f"Failed to save QR code: {qr_e}"

                messagebox.showinfo("✅ Success",
                    f"Registered!\n\n"
                    f"Appointment ID: {appoint_id}\n"
                    f"Visitor ID: {visitor_id}\n"
                    f"{qr_message}")
                
                clear_callback() 
                
            # --- SPECIFIC ERROR CHECK (API Code "131" - Resource Already Exists) ---
            elif api_code == "131":
                # This handles the "The request resource already exists. [visitor already regist]" error
                messagebox.showerror(
                    "🛑 Duplicate Visitor Error", 
                    f"Code {api_code}: {api_msg}\n\n"
                    f"This visitor is already registered. Please check the Certificate No. or contact the administrator."
                )
            
            # --- GENERAL API ERROR ---
            else:
                messagebox.showerror("API Error", f"Code: {api_code}\nMsg: {api_msg}\nDetail: {api_data}")

        else:
            messagebox.showerror("HTTP Error", f"Status = {response.status_code}\nResponse: {response.text}")

    except requests.exceptions.ConnectionError:
         messagebox.showerror("Connection Error", f"Could not connect to API host: {HOST}. Ensure the service is running and accessible.")
    except Exception as e:
        messagebox.showerror("Unhandled Error", str(e))