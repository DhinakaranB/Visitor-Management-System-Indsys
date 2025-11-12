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


# ------------------------------------------------------------
# SIGNATURE CREATION
# ------------------------------------------------------------
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
        f"{api_path}"
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


# ------------------------------------------------------------
# SEND DATA TO API (used by add_visitor)
# ------------------------------------------------------------
def send_to_api(data_payload, api_path, clear_callback):
    """
    Sends the data payload to the API using the specified path and handles responses.
    Used in add_visitor.py
    """
    try:
        body = json.dumps(data_payload)
        headers = create_signature("POST", body, api_path)
        URL = f"{BASE_URL}{api_path}"

        response = requests.post(URL, headers=headers, data=body, verify=False, timeout=10)

        if response.status_code == 200:
            try:
                res = response.json()
            except json.JSONDecodeError:
                messagebox.showerror("Response Error", f"Failed to parse JSON response.\n\nText: {response.text}")
                return

            api_code = res.get("code")
            api_msg = res.get("msg", "Unknown error")
            api_data = res.get("data", "")

            if api_code == "0":
                data = res["data"]
                appoint_id = data.get("appointRecordId", "-")
                visitor_id = data.get("visitorId", "-")
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
                    f"Registered!\n\nAppointment ID: {appoint_id}\nVisitor ID: {visitor_id}\n{qr_message}")
                clear_callback()

            elif api_code == "131":
                messagebox.showerror("🛑 Duplicate Visitor Error",
                    f"Code {api_code}: {api_msg}\n\nThis visitor already exists. Please check the Certificate No.")
            else:
                messagebox.showerror("API Error", f"Code: {api_code}\nMsg: {api_msg}\nDetail: {api_data}")

        else:
            messagebox.showerror("HTTP Error", f"Status = {response.status_code}\nResponse: {response.text}")

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", f"Could not connect to API host: {HOST}")
    except Exception as e:
        messagebox.showerror("Unhandled Error", str(e))

def get_visitor_list():
    try:
        api_path = "/artemis/api/visitor/v1/visitor/visitorInfo"
        body = json.dumps({
            "pageNo": 1,
            "pageSize": 100,
            "searchCriteria": {}
        })

        headers = create_signature("POST", body, api_path)
        url = f"{BASE_URL}{api_path}"

        response = requests.post(url, headers=headers, data=body, verify=False, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("DEBUG Raw API Response:", data)

            if data.get("code") == "0":
                visitor_data = data.get("data", {}).get("VisitorInfo", [])
                print("DEBUG Visitor count:", len(visitor_data))
                return visitor_data
            else:
                messagebox.showerror("API Error", data.get("msg", "Unknown error"))
                return []
        else:
            messagebox.showerror("HTTP Error", f"Status: {response.status_code}\n{response.text}")
            return []
    except Exception as e:
        messagebox.showerror("Unhandled Error", f"Visitor list fetch failed:\n{e}")
        return []


# def validate_hikvision_connection():
#     """
#     Quick test to confirm Hikvision OpenAPI connectivity.
#     """
#     api_path = "/artemis/api/common/v1/version"
#     import json, requests
#     body = json.dumps({})
#     headers = create_signature("POST", body, api_path)
#     url = f"{BASE_URL}{api_path}"

#     try:
#         res = requests.post(url, headers=headers, data=body, verify=False, timeout=10)
#         if res.status_code == 200:
#             data = res.json()
#             if str(data.get("code")) == "0":
#                 return True, data.get("data", {}).get("version", "Unknown")
#             else:
#                 return False, data.get("msg", "Error from Hikvision")
#         else:
#             return False, f"HTTP {res.status_code}: {res.text}"
#     except Exception as e:
#         return False, str(e)



# ------------------------------------------------------------
# UNIVERSAL CALL FUNCTION (used by visitor_list_single)
# ------------------------------------------------------------
def call_api(api_path, payload_dict=None, method="POST", timeout=10):
    """
    Universal reusable API caller (for GET or POST).
    Used in visitor_list_single.py
    """
    try:
        body = json.dumps(payload_dict or {})
        headers = create_signature(method, body, api_path)
        URL = f"{BASE_URL}{api_path}"

        print(f"📡 Calling API: {URL}")  # Debug log
        response = requests.request(method, URL, headers=headers, data=body, verify=False, timeout=timeout)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                messagebox.showerror("Response Error", f"Invalid JSON Response:\n\n{response.text}")
                return None
        else:
            messagebox.showerror("HTTP Error", f"Status = {response.status_code}\nResponse: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", f"Cannot connect to API host: {HOST}")
    except Exception as e:
        messagebox.showerror("API Error", str(e))
        return None
    
    
