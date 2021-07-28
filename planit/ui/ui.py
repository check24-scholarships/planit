
import tkinter as tk
import re
import typing
from itertools import zip_longest

from .syntax_highlighted_text import SyntaxHighlightedText
from .beet_view import BeetView
from .toolbar import Toolbar
from .theme import theme

from ..genetic import plan_optimizer


class Tools:
    MOVE = "Move"

    # Left click for the first option and right click to quickly access the second option
    ADD_CELL = "AddCell"
    ADD_PLANT = "DrawPlant"

    MARK_AS_JOKER = "MarkAsJoker"
    MARK_AS_MOVABLE = "MarkAsMovable"


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Planit")

        self.toolbar = Toolbar(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.toolbar.add_button(Tools.MOVE, "Move")
        self.toolbar.add_spacer()
        self.toolbar.add_button(Tools.ADD_CELL, "Add Cell")
        self.toolbar.add_button(Tools.ADD_PLANT, "Add Plant")
        self.toolbar.add_spacer()
        self.toolbar.add_button(Tools.MARK_AS_MOVABLE, "Movable")
        self.toolbar.add_button(Tools.MARK_AS_JOKER, "Joker")

        self.toolbar.add_action("Optimise", self.optimize_input)

        self.plant_list = SyntaxHighlightedText(
            self.root, width=20, bd=0, highlightthickness=0, **theme.app_style.input_text)
        self.plant_list.pack(side=tk.LEFT, fill=tk.Y)

        # Highlight the 2 in "2x Carrot"
        self.plant_list.highlight(r"\d+(?=x)", underline=True, font="Monospace 12 bold")
        # Highlight the x in "2x Carrot"
        self.plant_list.highlight(r"(?<=\d)x", font="Monospace 10", foreground="#aaa")

        beet = BeetView(self.root)
        beet.pack(expand=True, fill=tk.BOTH)
        self.beet = beet

        self.cursor = beet.canvas.create_rectangle(0, 0, 0, 0, **theme.beet_view_style.cursor)

        beet.canvas.bind("<Motion>", self.move_cursor_in_beet)

        beet.canvas.bind("<ButtonPress-1>", self.on_lmb_action)
        beet.canvas.bind("<B1-Motion>", self.on_lmb_action)
        beet.canvas.bind("<ButtonRelease-1>", lambda e: beet.on_resize(None))

        beet.canvas.bind("<ButtonPress-3>", self.on_rmb_action)
        beet.canvas.bind("<B3-Motion>", self.on_rmb_action)
        beet.canvas.bind("<ButtonRelease-3>", lambda e: beet.on_resize(None))

    def add_cell(self, event):
        self.beet.add_empty_cell(self.beet.screen_xy_to_cell_pos(event.x, event.y), False)
        self.beet.canvas.tag_raise(self.cursor)

    def remove_cell(self, event):
        self.beet.delete_cell(self.beet.screen_xy_to_cell_pos(event.x, event.y), False)

    def mark_as_joker(self, event, is_joker):
        pos = self.beet.screen_xy_to_cell_pos(event.x, event.y)
        self.beet.set_joker(pos, is_joker)

    def mark_as_movable(self, event, is_movable):
        pos = self.beet.screen_xy_to_cell_pos(event.x, event.y)
        self.beet.set_movable(pos, is_movable)

    def move_cursor_in_beet(self, event):
        # Move the cursor rectangle
        self.beet.canvas.coords(
            self.cursor,
            *self.beet.get_cell_bbox(self.beet.screen_xy_to_cell_pos(event.x, event.y)))

    def _run_tool_action(self, event, actions_by_tool: typing.Dict[str, typing.Callable[[], None]]):
        tool = self.toolbar.tool
        action = actions_by_tool.get(tool, None)

        if action is None:
            return

        action(event)

    def on_lmb_action(self, event):
        self.move_cursor_in_beet(event)

        actions_by_tool = {
            Tools.MOVE: None,
            Tools.ADD_CELL: self.add_cell,
            Tools.MARK_AS_JOKER: lambda e: self.mark_as_joker(e, True),
            Tools.MARK_AS_MOVABLE: lambda e: self.mark_as_movable(e, True)
        }

        self._run_tool_action(event, actions_by_tool)

    def on_rmb_action(self, event):
        self.move_cursor_in_beet(event)

        actions_by_tool = {
            Tools.ADD_CELL: self.remove_cell,
            Tools.MARK_AS_JOKER: lambda e: self.mark_as_joker(e, False),
            Tools.MARK_AS_MOVABLE: lambda e: self.mark_as_movable(e, False)
        }

        self._run_tool_action(event, actions_by_tool)

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
