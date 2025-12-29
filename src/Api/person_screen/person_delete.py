import json
from tkinter import messagebox

# --- IMPORT SIGNATURE API ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# ✅ CORRECT API URL (Single Delete)
DELETE_API_URL = "/artemis/api/resource/v1/person/single/delete"

def delete_by_code(person_code):
    """
    Calls the Delete API for a specific person Code (e.g., 'DK009').
    """
    if not common_signature_api:
        messagebox.showerror("Error", "Signature Module not found!")
        return False

    # ✅ PAYLOAD MUST USE 'personCode'
    payload = {
        "personCode": str(person_code)
    }

    try:
        print(f"🗑 Deleting Person Code: {person_code}")
        
        # Call API
        if hasattr(common_signature_api, 'call_api'):
            response = common_signature_api.call_api(DELETE_API_URL, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            response = common_signature_api.send_to_api(DELETE_API_URL, payload)
        elif hasattr(common_signature_api, 'post'):
            response = common_signature_api.post(DELETE_API_URL, payload)
        else:
            messagebox.showerror("Error", "No valid API function found.")
            return False

        # --- Handle Response Types ---
        if isinstance(response, dict):
            data = response
        elif isinstance(response, str):
            try:
                data = json.loads(response)
            except:
                data = {}
        else:
            try:
                data = response.json()
            except:
                data = {}

        # Check Result
        if data.get("code") == "0":
            return True
        else:
            err_msg = data.get("msg", "Unknown Error")
            print(f"❌ API Error: {err_msg}")
            messagebox.showerror("Delete Failed", f"API Error: {err_msg}")
            return False

    except Exception as e:
        print("❌ Delete Exception:", e)
        messagebox.showerror("Connection Error", str(e))
        return False