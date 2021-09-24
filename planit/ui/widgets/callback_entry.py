
"""
A tk Entry widget that lets you add an "on change" command.
"""

import tkinter as tk


def CallbackEntry(root, command=lambda text: None, **kwargs):
    sv = tk.StringVar()
    sv.trace_add("write", lambda *args: command(sv.get()))
    entry = tk.Entry(root, textvariable=sv, **kwargs)
    return entry
