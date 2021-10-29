
"""
A simple resource manager that returns the true path to a local resource file
that is located in the resources folder.

This is meant to avoid any file-mapping problems that may occur when building planit to an executable application.
"""

import os


def get(local_path: str) -> str:
    return os.path.join("./resources", local_path)
