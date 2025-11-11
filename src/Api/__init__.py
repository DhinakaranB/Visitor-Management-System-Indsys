import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from Api import visitor_registerment as visitor_form
from Api import visitor_list_Info as visitor_list
import Api.common_signature_api
