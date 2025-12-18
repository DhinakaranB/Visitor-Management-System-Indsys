import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))


import tkinter as tk
from tkinter import ttk
from src.Api.visitor_screen import visitor_registerment as visitor_form
from src.Api.visitor_screen import visitor_list_Info as visitor_list
from src.Api.Common_signature import common_signature_api

