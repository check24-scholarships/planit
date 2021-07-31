import tkinter as tk
import math

from .theme import theme
from .scrollable_canvas import ScrollableCanvas
from ..standard_types import *

import typing


class Cell:
    def __init__(self):
        self.plant: Plant = None
        self.is_joker = False
        self.is_movable = True

        self.background = None
        self.movable_pattern = None
        self.text = None

    def draw(self, bbox: BBox, canvas: tk.Canvas):
        self.background = canvas.create_rectangle(*bbox, **theme.beet_view.cell.background)

        cx = bbox.x0 + (bbox.x1 - bbox.x0) / 2
        cy = bbox.y0 + (bbox.y1 - bbox.y0) / 2

        if self.plant is not None and not self.is_joker:
            self.text = canvas.create_text(cx, cy, text=str(self.plant), justify=tk.CENTER,
                                           **theme.beet_view.cell.plant_text)

        if self.is_joker:
            self.text = canvas.create_text(cx, cy, text="?", justify=tk.CENTER,
                                           **theme.beet_view.cell.joker_text)

        if self.is_movable:
            self.movable_pattern = canvas.create_rectangle(bbox.x0 + 5, bbox.y0 - 5, bbox.x1 - 5, bbox.y1 + 5,
                                                           **theme.beet_view.cell.movable_pattern)

    def clear(self, canvas: tk.Canvas):
        def safe_delete(tag):
            if tag is None:
                return
            canvas.delete(tag)

        safe_delete(self.background)
        safe_delete(self.text)
        safe_delete(self.movable_pattern)

        self.background = self.text = self.movable_pattern = None

    def to_dict(self) -> dict:
        return {
            "plant": self.plant,
            "is_movable": self.is_movable,
            "is_joker": self.is_joker
        }

    @classmethod
    def from_dict(cls, d) -> "Cell":
        cell = cls()
        cell.plant = d["plant"]
        cell.is_movable = d["is_movable"]
        cell.is_joker = d["is_joker"]
        return cell

    def __repr__(self):
        return f"Cell({self.plant})"


class BeetView(ScrollableCanvas):
    def __init__(self, root):
        super(BeetView, self).__init__(root, scroll_start_event="<ButtonPress-2>", scroll_move_event="<B2-Motion>",
                                       **theme.beet_view.canvas)

        self.cells_by_pos: typing.Dict[Position, Cell] = {}

        self.canvas.create_oval(-10, -10, 10, 10, **theme.beet_view.center_circle)

        self.cell_size = 100
        self.padding = 200

    # Cell methods

    def _draw_cell(self, cell: Cell, pos: Position):
        cell.draw(self.get_cell_bbox(pos), self.canvas)

    def _redraw_cell(self, cell: Cell, pos: Position):
        cell.clear(self.canvas)
        cell.draw(self.get_cell_bbox(pos), self.canvas)

    def add_empty_cell(self, pos: Position, resize=True):
        if pos in self.cells_by_pos:
            return

        cell = Cell()
        self._draw_cell(cell, pos)
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

    def swap_cells(self, pos_a: Position, pos_b: Position):
        if pos_a == pos_b:
            return

        cell_a = self.cells_by_pos.get(pos_a, None)
        cell_b = self.cells_by_pos.get(pos_b, None)

        # When swapping with an empty cell, the empty cell is a None and therefore won't overwrite
        # the other cell's origin location => Overwrite (delete) it here for the None cell
        if cell_a is not None:
            del self.cells_by_pos[pos_a]
        if cell_b is not None:
            del self.cells_by_pos[pos_b]

        if cell_a is not None:
            self.cells_by_pos[pos_b] = cell_a
            self._redraw_cell(cell_a, pos_b)

        if cell_b is not None:
            self.cells_by_pos[pos_a] = cell_b
            self._redraw_cell(cell_b, pos_a)

    def get_cell(self, pos: Position) -> Cell:
        return self.cells_by_pos[pos]

    def has_cell(self, pos: Position) -> bool:
        return pos in self.cells_by_pos

    def delete_all_cells(self):
        for cell in self.cells_by_pos.values():
            cell.clear(self.canvas)

        self.cells_by_pos.clear()

    # Cell coordinate helper methods

    def get_cells_by_pos(self) -> typing.Dict[Position, Cell]:
        return self.cells_by_pos

    def get_cell_bbox(self, pos: Position) -> BBox:
        return BBox(
            *self.cell_pos_to_xy(pos),
            *self.cell_pos_to_xy((pos[0] + 1, pos[1] + 1)))

    def cell_pos_to_xy(self, pos: Position):
        return pos[0] * self.cell_size, -pos[1] * self.cell_size

    def xy_to_cell_pos(self, x: int, y: int) -> Position:
        return math.floor(x / self.cell_size), math.floor(- y / self.cell_size)

    def screen_xy_to_cell_pos(self, x: int, y: int) -> Position:
        return self.xy_to_cell_pos(self.canvas.canvasx(x), self.canvas.canvasy(y))

    # Methods for setting a cell's data

    def set_plant(self, pos: Position, plant: Plant, redraw=True):
        cell = self.cells_by_pos.get(pos, None)
        if cell is None:
            return

        cell.plant = plant
        if redraw:
            self._redraw_cell(cell, pos)

    def set_joker(self, pos: Position, is_joker: bool, redraw=True):
        cell = self.cells_by_pos.get(pos, None)
        if cell is None:
            return

        cell.is_joker = is_joker
        if redraw:
            self._redraw_cell(cell, pos)

    def set_movable(self, pos: Position, is_movable: bool, redraw=True):
        cell = self.cells_by_pos.get(pos, None)
        if cell is None:
            return

        cell.is_movable = is_movable
        if redraw:
            self._redraw_cell(cell, pos)

    # Save / load

    def save_to_dict(self) -> dict:
        cells = []

        for pos, cell in self.cells_by_pos.items():
            cell_data = cell.to_dict()
            cell_data["pos"] = pos
            cells.append(cell_data)

        return {
            "cells": cells
        }

    def load_from_dict(self, d: dict):
        self.delete_all_cells()

        for cell_data in d["cells"]:
            cell = Cell.from_dict(cell_data)
            pos = cell_data["pos"]
            self._draw_cell(cell, pos)
            self.cells_by_pos[pos] = cell
