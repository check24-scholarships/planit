
import tkinter as tk
import math

from .scrollable_canvas import ScrollableCanvas
from ..standard_types import *

import typing


class Cell:
    def __init__(self):
        self.plant: Plant = None
        self.is_joker = False
        self.is_movable = True

        self.background = None

    def draw(self, bbox: BBox, canvas: tk.Canvas):
        self.background = canvas.create_rectangle(*bbox, fill="grey50")

    def clear(self, canvas: tk.Canvas):
        canvas.delete(self.background)


class BeetView (ScrollableCanvas):
    def __init__(self, root):
        super(BeetView, self).__init__(root, scroll_start_event="<ButtonPress-2>", scroll_move_event="<B2-Motion>")

        self.cells_by_pos: typing.Dict[Position, Cell] = {}

        self.canvas.create_oval(-10, -10, 10, 10, fill="grey90", width=0)

        self.cell_size = 100
        self.padding = 200

    def _redraw_cell(self, cell: Cell, pos: Position):
        cell.clear(self.canvas)
        cell.draw(self.get_cell_bbox(pos), self.canvas)

    def add_empty_cell(self, pos: Position, resize=True):
        if pos in self.cells_by_pos:
            return

        cell = Cell()
        cell.draw(self.get_cell_bbox(pos), self.canvas)
        self.cells_by_pos[pos] = cell

        if resize:
            self.on_resize(None)

    def delete_cell(self, pos: Position, resize=True):
        if pos not in self.cells_by_pos:
            return

        self.cells_by_pos[pos].clear(self.canvas)
        del self.cells_by_pos[pos]

        if resize:
            self.on_resize(None)

    def get_cell(self, pos: Position) -> Cell:
        return self.cells_by_pos[pos]

    # Cell coordinate helper methods

    def get_cells_by_pos(self) -> typing.Dict[Position, Cell]:
        return self.cells_by_pos

    def get_cell_bbox(self, pos: Position) -> BBox:
        return BBox(
            *self.cell_pos_to_xy(pos),
            *self.cell_pos_to_xy((pos[0]+1, pos[1]+1)))

    def cell_pos_to_xy(self, pos: Position):
        return pos[0] * self.cell_size, -pos[1] * self.cell_size

    def xy_to_cell_pos(self, x: int, y: int) -> Position:
        return math.floor(x / self.cell_size), math.floor(- y / self.cell_size)

    def screen_xy_to_cell_pos(self, x: int, y: int) -> Position:
        return self.xy_to_cell_pos(self.canvas.canvasx(x), self.canvas.canvasy(y))

    # Methods for setting a cell's data

    def set_plant(self, pos: Position, plant: Plant, redraw=True):
        cell = self.get_cell(pos)
        cell.plant = plant
        if redraw:
            self._redraw_cell(cell, pos)

    def set_joker(self, pos: Position, is_joker: bool, redraw=True):
        cell = self.get_cell(pos)
        cell.is_joker = is_joker
        if redraw:
            self._redraw_cell(cell, pos)

    def set_movable(self, pos: Position, is_movable: bool, redraw=True):
        cell = self.get_cell(pos)
        cell.is_movable = is_movable
        if redraw:
            self._redraw_cell(cell, pos)
