
import tkinter as tk
import math
import re
from itertools import zip_longest

from standard_types import *
from .scrollable_canvas import ScrollableCanvas
from .syntax_highlighted_text import SyntaxHighlightedText

from genetic import plan_optimizer


class Cell:
    def __init__(self, bbox: BBox, canvas: tk.Canvas):
        self.background = canvas.create_rectangle(*bbox, fill="grey50")

    def delete(self, canvas: tk.Canvas):
        canvas.delete(self.background)


class BeetView (ScrollableCanvas):
    def __init__(self, root):
        super(BeetView, self).__init__(root, scroll_start_event="<ButtonPress-2>", scroll_move_event="<B2-Motion>")

        self.cells_by_pos = {}

        self.canvas.create_oval(-10, -10, 10, 10, fill="grey90", width=0)

        self.cell_size = 100
        self.padding = 200

    def add_cell(self, pos, resize=True):
        if pos in self.cells_by_pos:
            return

        self.cells_by_pos[pos] = Cell(self.get_cell_bbox(pos), self.canvas)
        if resize:
            self.on_resize(None)

    def delete_cell(self, pos, resize=True):
        if pos not in self.cells_by_pos:
            return

        self.cells_by_pos[pos].delete(self.canvas)
        del self.cells_by_pos[pos]
        if resize:
            self.on_resize(None)

    def get_cell(self, pos):
        return self.cells_by_pos[pos]

    def get_cells_by_pos(self):
        return self.cells_by_pos

    def get_cell_bbox(self, pos):
        return BBox(
            *self.cell_pos_to_xy(pos),
            *self.cell_pos_to_xy((pos[0]+1, pos[1]+1)))

    def cell_pos_to_xy(self, pos):
        return pos[0] * self.cell_size, -pos[1] * self.cell_size

    def xy_to_cell_pos(self, x, y):
        return math.floor(x / self.cell_size), math.floor(- y / self.cell_size)

    def screen_xy_to_cell_pos(self, x, y):
        return self.xy_to_cell_pos(self.canvas.canvasx(x), self.canvas.canvasy(y))


class App:
    def __init__(self):
        self.root = tk.Tk()

        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        optimize_button = tk.Button(self.toolbar, text="Optimize", command=self.parse_input)
        optimize_button.pack(side=tk.LEFT)

        self.plant_list = SyntaxHighlightedText(self.root, width=20, font="Arial 12")
        self.plant_list.pack(side=tk.LEFT, fill=tk.Y)

        self.plant_list.highlight(r"\d+(?=x)", underline=True, font="Monospace 12 bold")
        self.plant_list.highlight(r"(?<=\d)x", font="Monospace 10", foreground="#aaa")

        beet = BeetView(self.root)
        beet.pack(expand=True, fill=tk.BOTH)
        self.beet = beet

        cursor = beet.canvas.create_rectangle(0, 0, 0, 0)

        def show_cursor(event):
            beet.canvas.coords(cursor, *beet.get_cell_bbox(beet.screen_xy_to_cell_pos(event.x, event.y)))

        def add_cell(event):
            beet.add_cell(beet.screen_xy_to_cell_pos(event.x, event.y), False)

        def remove_cell(event):
            beet.delete_cell(beet.screen_xy_to_cell_pos(event.x, event.y), False)

        beet.canvas.bind("<Motion>", show_cursor)

        beet.canvas.bind("<ButtonPress-1>", add_cell)
        beet.canvas.bind("<ButtonRelease-1>", lambda e: beet.on_resize(None))
        beet.canvas.bind("<ButtonPress-3>", remove_cell)
        beet.canvas.bind("<ButtonRelease-3>", lambda e: beet.on_resize(None))
        beet.canvas.bind("<B1-Motion>", add_cell)
        beet.canvas.bind("<B3-Motion>", remove_cell)

    def parse_input(self):
        text = self.plant_list.get_text()
        lines = filter(None, (line.strip() for line in text.split("\n")))

        plants = []

        for line in lines:
            match = re.match(r"(?P<count>\d+)x\s+(?P<name>.+)", line)
            if not match: continue

            count = int(match.group("count"))
            name = match.group("name")

            plants.extend([name] * count)

        positions = list(self.beet.get_cells_by_pos().keys())
        plants_by_pos = {pos: plant for pos, plant in zip_longest(positions, plants, fillvalue=None)}

        plan = plan_optimizer.Plan(plants_by_pos, positions)
        plan = plan_optimizer.optimize(plan)
        print(plan)


def run_app():
    app = App()
    app.root.mainloop()


if __name__ == '__main__':
    run_app()
