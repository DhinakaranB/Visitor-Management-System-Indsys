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
    Sends the data payload to the API using the specified path.
    
    Args:
        data_payload (dict): The structured data ready for JSON conversion.
        api_path (str): The specific endpoint path (e.g., /artemis/api/visitor/...).
        clear_callback (function): Function to clear the form entries on success.
    """
    try:
        body = json.dumps(data_payload)
        headers = create_signature("POST", body, api_path)
        
        URL = f"{BASE_URL}{api_path}" # Construct the full URL using BASE_URL and the dynamic path
        
        response = requests.post(URL, headers=headers, data=body, verify=False, timeout=10)

        if response.status_code == 200:
            res = response.json()
            if res.get("code") == "0":
                data = res["data"]
                appoint_id = data["appointRecordId"]
                visitor_id = data["visitorId"]
                qr_data = data.get("qrCodeImage")

                qr_message = "No QR code received."
                if qr_data:
                    try:
                        file_name = f"visitor_qr_{appoint_id}.png"
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
                
            else:
                messagebox.showerror("API Error", f"Code: {res.get('code')}\nMsg: {res.get('msg', 'Unknown error')}\nDetail: {res.get('data', '')}")
        else:
            messagebox.showerror("HTTP Error", f"Status = {response.status_code}\nResponse: {response.text}")

    except requests.exceptions.ConnectionError:
         messagebox.showerror("Connection Error", f"Could not connect to API host: {HOST}. Ensure the service is running and accessible.")
    except Exception as e:
        messagebox.showerror("Unhandled Error", str(e))