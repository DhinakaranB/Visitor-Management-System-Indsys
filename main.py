import os
import sys
import runpy
import shutil
# import visitorRegisterDetails
# import visitorQRconfig

# --- Base Path Setup ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
LOGIN_DIR = os.path.join(SRC_DIR, "Api", "Homepage")
PYCACHE_DIR = os.path.join(BASE_DIR, "__all_pycache__")

# --- Centralized cache path ---
sys.pycache_prefix = PYCACHE_DIR

# --- Clean pycache before running ---
def clean_pycache():
    """Deletes centralized cache folder before running."""
    if os.path.exists(PYCACHE_DIR):
        print("🧹 Cleaning old cache files...")
        shutil.rmtree(PYCACHE_DIR)
    os.makedirs(PYCACHE_DIR, exist_ok=True)
    print("✅ Cache directory ready.")

# --- Ensure import paths ---
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
if LOGIN_DIR not in sys.path:
    sys.path.insert(0, LOGIN_DIR)

# --- Start Application ---
def start_login():
    """Starts the Visitor Management System UI"""
    print("Starting Visitor Management System...")
    runpy.run_path(os.path.join(LOGIN_DIR, "Ui.py"), run_name="__main__")

# --- Main Entry Point ---
if __name__ == "__main__":
    clean_pycache()
    start_login()

    #  Cleanup after app closes
    print("Cleaning up pycache after app closes...")
    shutil.rmtree(PYCACHE_DIR, ignore_errors=True)
    print("Pycache deleted successfully.")











