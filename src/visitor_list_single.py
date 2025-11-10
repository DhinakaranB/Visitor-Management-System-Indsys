# visitor_list_single.py

import tkinter as tk
from tkinter import ttk, messagebox
from common_api import call_api

BG_COLOR = "#F4F6F7"
TEXT_COLOR = "#2C3E50"
PRIMARY_COLOR = "#3498DB"


def show_single_visitor_list(content_frame):
    """
    Screen for searching a single visitor by visitorId and showing details.
    """
    # Clear existing content
    for widget in content_frame.winfo_children():
        widget.destroy()

    # Configure layout
    content_frame.grid_rowconfigure(0, weight=0)
    content_frame.grid_rowconfigure(1, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    # -----------------------------
    # Header
    # -----------------------------
    header_frame = tk.Frame(content_frame, bg=BG_COLOR)
    header_frame.grid(row=0, column=0, pady=10, padx=20, sticky="ew")

    tk.Label(
        header_frame,
        text="🔍 Search Visitor by ID",
        font=("Segoe UI", 16, "bold"),
        bg=BG_COLOR,
        fg=PRIMARY_COLOR,
    ).pack(side="left", padx=(5, 10))

    # -----------------------------
    # Search input
    # -----------------------------
    search_frame = tk.Frame(content_frame, bg=BG_COLOR)
    search_frame.grid(row=1, column=0, pady=(10, 5), padx=20, sticky="ew")

    tk.Label(
        search_frame, text="Visitor ID:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Segoe UI", 11)
    ).grid(row=0, column=0, padx=(0, 10), sticky="w")

    visitor_id_entry = ttk.Entry(search_frame, width=30)
    visitor_id_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="w")

    def perform_search():
        visitor_id = visitor_id_entry.get().strip()
        if not visitor_id:
            messagebox.showwarning("Input Error", "Please enter a Visitor ID to search.")
            return

        api_path = "/artemis/api/visitor/v1/visitor/single/visitorinfo"
        payload = {"visitorId": visitor_id}
        res = call_api(api_path, payload)

        # Clear any previous results
        for widget in result_frame.winfo_children():
            widget.destroy()

        if not res:
            messagebox.showerror("Error", "No response received from API.")
            return

        if "data" not in res:
            messagebox.showwarning("No Data", "No visitor found for the given ID.")
            return

        data = res.get("data", {})

        # Display results as key-value pairs
        row_index = 0
        for key, value in data.items():
            tk.Label(
                result_frame,
                text=f"{key}:",
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            ).grid(row=row_index, column=0, sticky="w", padx=10, pady=4)

            tk.Label(
                result_frame,
                text=value if value else "-",
                bg=BG_COLOR,
                fg=TEXT_COLOR,
                font=("Segoe UI", 10),
                anchor="w",
            ).grid(row=row_index, column=1, sticky="w", padx=10, pady=4)

            row_index += 1

    ttk.Button(
        search_frame,
        text="Search",
        style="TInfo.TButton",
        command=perform_search,
    ).grid(row=0, column=2, padx=10, pady=5)

    # -----------------------------
    # Results Section
    # -----------------------------
    result_frame = tk.Frame(content_frame, bg=BG_COLOR, relief="solid", bd=1)
    result_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

    # Give space for expansion
    content_frame.grid_rowconfigure(2, weight=1)
