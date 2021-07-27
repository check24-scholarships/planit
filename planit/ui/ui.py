
import tkinter as tk
import re
from itertools import zip_longest

from .syntax_highlighted_text import SyntaxHighlightedText
from .beet_view import BeetView
from .toolbar import Toolbar

from ..genetic import plan_optimizer


class App:
    def __init__(self):
        self.root = tk.Tk()

        self.toolbar = Toolbar(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.toolbar.add_action("Optimise", self.optimize_input)

        self.plant_list = SyntaxHighlightedText(self.root, width=20, font="Arial 12")
        self.plant_list.pack(side=tk.LEFT, fill=tk.Y)

        self.plant_list.highlight(r"\d+(?=x)", underline=True, font="Monospace 12 bold")
        self.plant_list.highlight(r"(?<=\d)x", font="Monospace 10", foreground="#aaa")

        beet = BeetView(self.root)
        beet.pack(expand=True, fill=tk.BOTH)
        self.beet = beet

        self.cursor = beet.canvas.create_rectangle(0, 0, 0, 0)

        beet.canvas.bind("<Motion>", self.move_cursor_in_beet)
        beet.canvas.bind("<ButtonPress-1>", self.add_cell)
        beet.canvas.bind("<ButtonRelease-1>", lambda e: beet.on_resize(None))
        beet.canvas.bind("<ButtonPress-3>", self.remove_cell)
        beet.canvas.bind("<ButtonRelease-3>", lambda e: beet.on_resize(None))
        beet.canvas.bind("<B1-Motion>", self.add_cell)
        beet.canvas.bind("<B3-Motion>", self.remove_cell)

    def add_cell(self, event):
        self.beet.add_empty_cell(self.beet.screen_xy_to_cell_pos(event.x, event.y), False)

    def remove_cell(self, event):
        self.beet.delete_cell(self.beet.screen_xy_to_cell_pos(event.x, event.y), False)

    def move_cursor_in_beet(self, event):
        # Move the cursor rectangle
        self.beet.canvas.coords(
            self.cursor,
            *self.beet.get_cell_bbox(self.beet.screen_xy_to_cell_pos(event.x, event.y)))

    def optimize_input(self):
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
