
import tkinter as tk


class VerticallyScrollableFrame (tk.Frame):
    def __init__(self, master, **kwargs):
        super(VerticallyScrollableFrame, self).__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.grid(row=0, column=1, sticky="ns")

        styling_options = {"bd": 0, "highlightthickness": 0, **kwargs}

        self.canvas = tk.Canvas(self, yscrollcommand=vscrollbar.set, **styling_options)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscrollbar.config(command=self.canvas.yview)

        self.container = tk.Frame(self.canvas, **styling_options)
        self._container_id = self.canvas.create_window(0, 0, window=self.container, anchor=tk.NW)
        self.container.bind("<Configure>", self._on_container_resize)
        self.canvas.bind("<Configure>", self._on_container_resize)

        self._is_resizing = False

    def _on_container_resize(self, event=None):
        if self._is_resizing:
            return

        self._is_resizing = True

        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.container.config(width=self.canvas.winfo_width())
        self.canvas.itemconfig(self._container_id, width=self.canvas.winfo_width())
        self.container.update_idletasks()

        self._is_resizing = False


class VerticallyScrollableFrame (tk.Frame):
    def __init__(self, master, **kwargs):
        super(VerticallyScrollableFrame, self).__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.grid(row=0, column=1, sticky="ns")

        styling_options = {"bd": 0, "highlightthickness": 0, **kwargs}

        self.canvas = tk.Canvas(self, yscrollcommand=vscrollbar.set, **styling_options)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscrollbar.config(command=self.canvas.yview)

        self.container = tk.Frame(self.canvas, **styling_options)
        self._container_id = self.canvas.create_window(0, 0, window=self.container, anchor=tk.NW)
        self.container.bind("<Configure>", lambda event: self._update_scrollregion())
        self.canvas.bind("<Configure>", self._on_container_resize)

    def _update_scrollregion(self):
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def _on_container_resize(self, event=None):
        self.container.config(width=self.canvas.winfo_width())
        self.canvas.itemconfig(self._container_id, width=self.canvas.winfo_width())


if __name__ == '__main__':
    root = tk.Tk()
    frame = VerticallyScrollableFrame(root, bg="#0ac")
    frame.pack(expand=True, fill=tk.BOTH)

    frame.container.grid_columnconfigure(0, weight=1)
    for i in range(10):
        tk.Label(frame.container, text=i, bg="green").grid(row=i, sticky="EW")

    root.mainloop()