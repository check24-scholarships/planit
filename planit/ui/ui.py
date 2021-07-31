
import tkinter as tk
import re
import typing
from itertools import zip_longest

from .syntax_highlighted_text import SyntaxHighlightedText
from .beet_view import BeetView
from .toolbar import Toolbar
from .theme import theme

from ..genetic import plan_optimizer
from ..standard_types import *


class Tool:
    def activate(self):
        pass

    def deactivate(self):
        pass

    def _lmb_action(self, event):
        pass

    def _rmb_action(self, event):
        pass

    def on_lmb_press(self, event):
        self._lmb_action(event)

    def on_lmb_move(self, event):
        self._lmb_action(event)

    def on_lmb_release(self, event):
        pass

    def on_rmb_press(self, event):
        self._rmb_action(event)

    def on_rmb_move(self, event):
        self._rmb_action(event)

    def on_rmb_release(self, event):
        pass


class SwapTool (Tool):
    def __init__(self, beet_view: BeetView):
        self.from_cursor = None
        self.from_pos = None
        self.beet_view = beet_view

    def deactivate(self):
        if self.from_cursor is not None:
            self.beet_view.canvas.delete(self.from_cursor)

    def on_lmb_press(self, event):
        self.from_pos = self.beet_view.screen_xy_to_cell_pos(event.x, event.y)
        self.from_cursor = self.beet_view.canvas.create_rectangle(
            *self.beet_view.get_cell_bbox(self.from_pos), outline="white", width=3, dash=(5, 2))

    def on_lmb_release(self, event):
        self.beet_view.canvas.delete(self.from_cursor)
        self.from_cursor = None

        to_pos = self.beet_view.screen_xy_to_cell_pos(event.x, event.y)
        self.beet_view.swap_cells(self.from_pos, to_pos)


class BrushTool (Tool):
    """
    Base class of all "brush-like" tools that let the user draw on the grid as if it was a pixel image.
    """

    def __init__(self, beet_view: BeetView):
        self.beet_view = beet_view

    def on_lmb_release(self, event):
        self.beet_view.on_resize(None)

    def on_rmb_release(self, event):
        self.beet_view.on_resize(None)

    def _lmb_action(self, event):
        pos = self.beet_view.screen_xy_to_cell_pos(event.x, event.y)
        self._lmb_cell_action(pos)

    def _rmb_action(self, event):
        pos = self.beet_view.screen_xy_to_cell_pos(event.x, event.y)
        self._rmb_cell_action(pos)

    def _lmb_cell_action(self, pos: Position):
        pass

    def _rmb_cell_action(self, pos: Position):
        pass


class AddCellTool (BrushTool):
    def _lmb_cell_action(self, pos: Position):
        self.beet_view.add_empty_cell(pos, False)

    def _rmb_cell_action(self, pos: Position):
        self.beet_view.delete_cell(pos, False)


class MarkAsJokerTool (BrushTool):
    def _lmb_cell_action(self, pos: Position):
        self.beet_view.set_joker(pos, True)

    def _rmb_cell_action(self, pos: Position):
        self.beet_view.set_joker(pos, False)


class MarkAsMovableTool (BrushTool):
    def _lmb_cell_action(self, pos: Position):
        self.beet_view.set_movable(pos, True)

    def _rmb_cell_action(self, pos: Position):
        self.beet_view.set_movable(pos, False)


class Tools:
    MOVE = "Move"
    SWAP = "Swap"

    # Left click for the first option and right click to quickly access the second option
    ADD_CELL = "AddCell"
    ADD_PLANT = "DrawPlant"

    MARK_AS_JOKER = "MarkAsJoker"
    MARK_AS_MOVABLE = "MarkAsMovable"


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Planit")

        self.toolbar = Toolbar(self.root, change_action=self.on_change_tool)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.tools_by_name: typing.Dict[str, Tool] = {}

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

        beet.canvas.bind("<ButtonPress-1>", self._run_tool_action("on_lmb_press"))
        beet.canvas.bind("<B1-Motion>", self._run_tool_action("on_lmb_move"))
        beet.canvas.bind("<ButtonRelease-1>", self._run_tool_action("on_lmb_release"))

        beet.canvas.bind("<ButtonPress-3>", self._run_tool_action("on_rmb_press"))
        beet.canvas.bind("<B3-Motion>", self._run_tool_action("on_rmb_move"))
        beet.canvas.bind("<ButtonRelease-3>", self._run_tool_action("on_rmb_release"))

        def add_tool(name, text, tool: Tool):
            self.tools_by_name[name] = tool
            self.toolbar.add_button(name, text)

        add_tool(Tools.MOVE, "Move", Tool())
        add_tool(Tools.SWAP, "Swap", SwapTool(self.beet))
        self.toolbar.add_spacer()
        add_tool(Tools.ADD_CELL, "Add Cell", AddCellTool(self.beet))
        add_tool(Tools.ADD_PLANT, "Add Plant", Tool())
        self.toolbar.add_spacer()
        add_tool(Tools.MARK_AS_MOVABLE, "Movable", MarkAsMovableTool(self.beet))
        add_tool(Tools.MARK_AS_JOKER, "Joker", MarkAsJokerTool(self.beet))

        self.toolbar.add_action("Optimise", self.optimize_input)

    def on_change_tool(self, from_name, to_name):
        previous_tool = self.tools_by_name.get(from_name, None)

        if previous_tool is not None:
            previous_tool.deactivate()

        self.tools_by_name[to_name].activate()

    def _run_tool_action(self, method_name):
        def call_method_on_event(event):
            tool = self.tools_by_name[self.toolbar.selected_button]
            getattr(tool, method_name)(event)

            self.beet.canvas.tag_raise(self.cursor)
            self.move_cursor_in_beet(event)

        return call_method_on_event

    def move_cursor_in_beet(self, event):
        # Move the cursor rectangle
        self.beet.canvas.coords(
            self.cursor,
            *self.beet.get_cell_bbox(self.beet.screen_xy_to_cell_pos(event.x, event.y)))

    def optimize_input(self):
        # Extract the plants from the input string

        text = self.plant_list.get_text()
        lines = filter(None, (line.strip() for line in text.split("\n")))

        plants = []

        for line in lines:
            # E.g. "3x Carrot" => count = "3", name = "Carrot"
            match = re.match(r"(?P<count>\d+)x\s+(?P<name>.+)", line)
            if not match: continue

            count = int(match.group("count"))
            name = match.group("name")

            plants.extend([name] * count)

        # Create the inputs for the optimizer
        positions = list(self.beet.get_cells_by_pos().keys())
        movable_positions = [pos for (pos, cell) in self.beet.get_cells_by_pos().items() if cell.is_movable]
        plants_by_pos = {pos: plant for pos, plant in zip_longest(positions, plants, fillvalue=None)}

        print(plants_by_pos)
        print(positions)
        plan = plan_optimizer.Plan(plants_by_pos, movable_positions)
        plan = plan_optimizer.optimize(plan, 500)
        print(plan.fitness)
        print(plan)

        for pos, plant in plan.plants_by_pos.items():
            self.beet.set_plant(pos, plant)


def run_app():
    app = App()
    app.root.mainloop()


if __name__ == '__main__':
    run_app()
