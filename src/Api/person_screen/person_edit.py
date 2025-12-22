import json
from tkinter import messagebox

# --- IMPORT SIGNATURE API ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# API URL from your screenshot
UPDATE_API_URL = "/artemis/api/resource/v1/person/single/update"

def update_person_api(payload):
    """
    Sends the modified person data to the Update API.
    Returns True if successful.
    """
    if not common_signature_api:
        messagebox.showerror("Error", "Signature Module not found!")
        return False

    try:
        print(f"📝 Updating Person: {payload.get('personCode')}")
        
        # Call API
        if hasattr(common_signature_api, 'call_api'):
            response = common_signature_api.call_api(UPDATE_API_URL, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            response = common_signature_api.send_to_api(UPDATE_API_URL, payload)
        elif hasattr(common_signature_api, 'post'):
            response = common_signature_api.post(UPDATE_API_URL, payload)
        else:
            messagebox.showerror("Error", "No valid API function found.")
            return False

        # --- FIX: Handle Response Types Correctly ---
        if isinstance(response, dict):
            data = response
        elif isinstance(response, str):
            data = json.loads(response)
        else:
            try:
                data = response.json()
            except:
                data = {}

        # Check Result
        if data.get("code") == "0":
            return True
        else:
            messagebox.showerror("Update Failed", f"API Error: {data.get('msg')}")
            return False

    except Exception as e:
        print("❌ Update Exception:", e)
        messagebox.showerror("Connection Error", str(e))
        return False