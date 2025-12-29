import json
from tkinter import messagebox

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# API Endpoint
API_DELETE_VEHICLE = "/artemis/api/resource/v1/vehicle/single/delete"

def delete_vehicle(plate_no):
    """
    Deletes a vehicle by its Plate Number.
    """
    if not common_signature_api:
        messagebox.showerror("Error", "API Handler not found.")
        return False

    # Payload
    payload = {
        "plateNo": str(plate_no)
    }

    print(f"🗑 Deleting Vehicle: {payload}")

    try:
        if hasattr(common_signature_api, 'call_api'):
            res = common_signature_api.call_api(API_DELETE_VEHICLE, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            res = common_signature_api.send_to_api(API_DELETE_VEHICLE, payload)
        else:
            return False

        # Parse response
        if isinstance(res, str):
            res = json.loads(res)
        elif hasattr(res, 'json'):
            res = res.json()

        if str(res.get("code")) == "0":
            return True
        else:
            err = res.get("msg", "Unknown Error")
            # Log error but let UI handle user notification if needed, or show here
            print(f"Delete Error: {err}")
            messagebox.showerror("Delete Failed", f"API Error: {err}")
            return False

    except Exception as e:
        print(f"Delete Exception: {e}")
        messagebox.showerror("Error", f"Connection failed: {e}")
        return False