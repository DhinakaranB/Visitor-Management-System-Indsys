import json
from tkinter import messagebox

# --- IMPORT SIGNATURE API ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# API URL from your screenshot
DELETE_API_URL = "/artemis/api/resource/v1/person/single/delete"

def delete_by_code(person_code):
    """
    Calls the Delete API for a specific person code.
    Returns True if successful, False otherwise.
    """
    if not common_signature_api:
        messagebox.showerror("Error", "Signature Module not found!")
        return False

    # Payload
    payload = {
        "personCode": person_code
    }

    try:
        print(f"🗑 Deleting Person: {person_code}")
        
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

        # --- FIX: Handle Response Types Correctly ---
        if isinstance(response, dict):
            # It is already a dictionary, use it directly
            data = response
        elif isinstance(response, str):
            # It is a string, parse it
            data = json.loads(response)
        else:
            # It is a Requests object (fallback)
            try:
                data = response.json()
            except:
                data = {}

        # Check Result
        if data.get("code") == "0":
            return True
        else:
            messagebox.showerror("Delete Failed", f"API Error: {data.get('msg')}")
            return False

    except Exception as e:
        print("❌ Delete Exception:", e)
        messagebox.showerror("Connection Error", str(e))
        return False