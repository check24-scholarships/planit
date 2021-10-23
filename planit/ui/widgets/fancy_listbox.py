

"""
A better ListBox implementation for tkinter that lets you use custom widgets as elements.
"""

import tkinter as tk
from .vertically_scrollable_frame import VerticallyScrollableFrame


class FancyListBox (tk.Frame):
    def __init__(self, master, width=10, spacing=10, **kwargs):
        super(FancyListBox, self).__init__(master, **kwargs)
        self.spacing = spacing

        scrollable_frame = VerticallyScrollableFrame(self, width=width)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)
        scrollable_frame.container.grid_columnconfigure(0, weight=1)
        self.container = scrollable_frame.container
        self._item_count = 0

    def add_element(self, widget):
        widget.grid(column=0, row=self._item_count, sticky="ew")
        self._item_count += 1

    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()


if __name__ == '__main__':
    root = tk.Tk()

    box = FancyListBox(root, width=100, height=100)

    for i in range(10):
        button = tk.Button(box.container, text=i)
        box.add_element(button)

    box.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
