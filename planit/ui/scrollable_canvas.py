
import tkinter as tk


class ScrollableCanvas(tk.Frame):
    def __init__(self, root, scroll_start_event="<ButtonPress-1>", scroll_move_event="<B1-Motion>"):
        super(ScrollableCanvas, self).__init__(root)

        self.canvas = tk.Canvas(self)
        self.scrollbar_x = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.config(xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x.grid(row=1, column=0, sticky="EW")
        self.scrollbar_y.grid(row=0, column=1, sticky="NS")
        self.canvas.grid(row=0, column=0, sticky="NSEW")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.bind(scroll_start_event, self.on_scroll_start)
        self.canvas.bind(scroll_move_event, self.on_scroll_move)
        self.canvas.bind("<Configure>", self.on_resize)

        self.padding = 100

    def on_scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_resize(self, event):
        bbox = self.canvas.bbox(tk.ALL)

        p = self.padding
        padded_bbox = (bbox[0] - p, bbox[1] - p, bbox[2] + p, bbox[3] + p)

        self.canvas.config(scrollregion=padded_bbox)