
import tkinter as tk

from .plant_search import PlantSearchFrame
from .beet_view import BeetView
from .widgets.toolbar import Toolbar
from .theme import theme

from ..genetic import plan_optimizer
from ..standard_types import *


class Tool:
    """
    The base class of a tool that can be selected by the user.
    It receives events for the left and right mouse buttons as well as for activation / deactivation.
    """
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
    """
    Tool for swapping two cells.
    """

    def __init__(self, app: "App"):
        self.from_cursor = None
        self.from_pos = None
        self.app = app
        self.beet_view = app.beet

    def deactivate(self):
        if self.from_cursor is not None:
            self.beet_view.canvas.delete(self.from_cursor)

    def on_lmb_press(self, event):
        self.from_pos = self.beet_view.screen_xy_to_cell_pos(event.x, event.y)
        self.from_cursor = self.beet_view.canvas.create_rectangle(
            *self.beet_view.get_cell_bbox(self.from_pos), **theme.tools.swap_cursor)

    def on_lmb_release(self, event):
        self.beet_view.canvas.delete(self.from_cursor)
        self.from_cursor = None

        to_pos = self.beet_view.screen_xy_to_cell_pos(event.x, event.y)
        self.beet_view.swap_cells(self.from_pos, to_pos)
        self.app.update_cell_quality(self.from_pos)
        self.app.update_cell_quality(to_pos)


class BrushTool (Tool):
    """
    Base class of all "brush-like" tools that let the user draw on the grid as if it was a pixel image.
    """

    def __init__(self, app: "App"):
        self.app = app
        self.beet_view = app.beet

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
        self.app.update_cell_quality(pos)


class MarkAsJokerTool (BrushTool):
    def _lmb_cell_action(self, pos: Position):
        self.beet_view.set_joker(pos, True)
        self.app.update_cell_quality(pos)

    def _rmb_cell_action(self, pos: Position):
        self.beet_view.set_joker(pos, False)
        self.app.update_cell_quality(pos)


class MarkAsMovableTool (BrushTool):
    def _lmb_cell_action(self, pos: Position):
        self.beet_view.set_movable(pos, True)

    def _rmb_cell_action(self, pos: Position):
        self.beet_view.set_movable(pos, False)


class DrawPlantTool (BrushTool):
    def _lmb_cell_action(self, pos: Position):
        plant = self.app.plant_search.selected_plant
        if not plant:
            return
        self.beet_view.set_plant(pos, plant)
        self.app.update_cell_quality(pos)

    def _rmb_cell_action(self, pos: Position):
        self.beet_view.set_plant(pos, None)
        self.app.update_cell_quality(pos)


class Tools:
    """
    Collection of all tool names.
    """

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
        self.root.config(**theme.app.root_background)

        self.toolbar = Toolbar(self.root, change_action=self.on_change_tool)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, ipady=5)
        self.tools_by_name: typing.Dict[str, Tool] = {}

        self.plant_search = PlantSearchFrame(self.root)
        self.plant_search.pack(side=tk.LEFT, fill=tk.Y)

        beet = BeetView(self.root)
        beet.pack(expand=True, fill=tk.BOTH)
        self.beet = beet

        self.cursor = beet.canvas.create_rectangle(0, 0, 0, 0, **theme.beet_view.cursor)

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
        add_tool(Tools.SWAP, "Swap", SwapTool(self))

        self.toolbar.add_spacer()
        add_tool(Tools.ADD_CELL, "Add Cell", AddCellTool(self))
        add_tool(Tools.ADD_PLANT, "Add Plant", DrawPlantTool(self))

        self.toolbar.add_spacer()
        add_tool(Tools.MARK_AS_MOVABLE, "Movable", MarkAsMovableTool(self))
        add_tool(Tools.MARK_AS_JOKER, "Joker", MarkAsJokerTool(self))

        self.toolbar.add_action("Optimise", self.optimize_input)

    def on_change_tool(self, from_name, to_name):
        previous_tool = self.tools_by_name.get(from_name, None)

        if previous_tool is not None:
            previous_tool.deactivate()

        self.tools_by_name[to_name].activate()

    def _run_tool_action(self, method_name):
        """
        Returns a function that, when called, runs the "method_name" method of the active tool.
        """
        def call_method_on_event(event):
            tool = self.tools_by_name[self.toolbar.selected_button]
            getattr(tool, method_name)(event)

            self.beet.canvas.tag_raise(self.cursor)
            self.move_cursor_in_beet(event)

        return call_method_on_event

    def update_cell_quality(self, pos):
        """
        Only updates the quality field of the affected cell and its neighbours instead of the entire plan.
        """

        # As the partial updater has to (normally) update a total 5x5 square around the affected cell, it is more
        # efficient to just update the entire plan when less cells are involved.
        if len(self.beet.cells_by_pos) < 25:
            self.update_full_plan_quality()

        def add_pos(pos_a, pos_b):
            return pos_a[0] + pos_b[0], pos_a[1] + pos_b[1]

        affected_tiles = {
            add_pos(start, relative_pos)
            for relative_pos in plan_optimizer.AFFECTED_TILES
            # The partial plan also has to include the neighbouring cells of each neighbour of the actual
            # cell to update.
            for start in [pos, *plan_optimizer.AFFECTED_TILES]
        }

        affected_tiles.add(pos)
        positions_to_update = list(affected_tiles)

        plan = self.beet.export_partial_plan(positions_to_update, include_movable=False)
        evaluator = plan_optimizer.MAIN_EVALUATOR
        for pos in positions_to_update:
            self.beet.set_quality(pos, evaluator.evaluate_cell(plan, pos))

    def update_full_plan_quality(self, plan=None):
        """
        Updates the quality field of every cell in the plan
        """
        if plan is None:
            plan = self.beet.export_plan()

        evaluator = plan_optimizer.MAIN_EVALUATOR
        for pos in plan.plants_by_pos:
            self.beet.set_quality(pos, evaluator.evaluate_cell(plan, pos))

    def move_cursor_in_beet(self, event):
        """ Moves the square cursor that indicates which cell is currently under the mouse. """
        self.beet.canvas.coords(
            self.cursor,
            *self.beet.get_cell_bbox(self.beet.screen_xy_to_cell_pos(event.x, event.y)))

    def optimize_input(self):
        # Create the inputs for the optimizer
        plan = self.beet.export_plan()

        # Optimize
        plan = plan_optimizer.optimize(plan, 500)
        print(plan.fitness)
        print(plan)

        # Show the optimized version on screen
        for pos, plant in plan.plants_by_pos.items():
            self.beet.set_plant(pos, plant)

        # Visualize the quality score of each cell
        self.update_full_plan_quality(plan)


def run_app():
    app = App()
    app.root.mainloop()


if __name__ == '__main__':
    run_app()
