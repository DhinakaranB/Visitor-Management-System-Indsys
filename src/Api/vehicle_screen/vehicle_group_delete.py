import json
from tkinter import messagebox

# --- IMPORTS ---
try:
    from src.Api.Common_signature import common_signature_api
except ImportError:
    common_signature_api = None

# API Endpoint
API_DELETE_GROUP = "/artemis/api/resource/v1/vehicleGroup/single/delete"

def delete_group(index_code):
    """
    Deletes a vehicle group by its indexCode.
    """
    if not common_signature_api:
        messagebox.showerror("Error", "API Handler not found.")
        return False

    # Payload
    payload = {
        "vehicleGroupIndexCode": str(index_code)
    }

    print(f"🗑 Deleting Group: {payload}")

    try:
        if hasattr(common_signature_api, 'call_api'):
            res = common_signature_api.call_api(API_DELETE_GROUP, payload)
        elif hasattr(common_signature_api, 'send_to_api'):
            res = common_signature_api.send_to_api(API_DELETE_GROUP, payload)
        else:
            return False

        # Parse response if string
        if isinstance(res, str):
            res = json.loads(res)
        elif hasattr(res, 'json'):
            res = res.json()

        if str(res.get("code")) == "0":
            return True
        else:
            err = res.get("msg", "Unknown Error")
            messagebox.showerror("Delete Failed", f"API Error: {err}")
            return False

    except Exception as e:
        print(f"Delete Exception: {e}")
        messagebox.showerror("Error", f"Connection failed: {e}")
        return False