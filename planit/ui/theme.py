
"""
Theme system for the UI.

Each "block" of the UI has a dataclass that stores the tkinter styling options for it.
The first time this file is imported, it will read in the theme from the .toml file.
"""

from dataclasses import dataclass
import dacite
import toml
import os

from .. import resources


@dataclass
class BeetViewCellStyle:
    movable_pattern: dict
    plant_text: dict
    joker_text: dict
    background: dict


@dataclass
class BeetViewStyle:
    canvas: dict
    center_circle: dict
    cursor: dict
    cell: BeetViewCellStyle


@dataclass
class AppStyle:
    root_background: dict
    input_text: dict


@dataclass
class SearchStyle:
    search_bar: dict
    result: dict
    result_deselected: dict
    result_selected: dict
    background: dict


@dataclass
class ToolbarStyle:
    button: dict
    button_selected: dict
    button_deselected: dict
    action_button: dict
    spacer: dict
    background: dict


@dataclass
class ToolStyles:
    swap_cursor: dict


@dataclass
class Theme:
    app: AppStyle
    toolbar: ToolbarStyle
    tools: ToolStyles
    beet_view: BeetViewStyle
    search: SearchStyle


theme: Theme
themes_folder = os.path.join(os.path.dirname(__file__), "themes")

# Load a theme
with open(resources.get("themes/default_theme.toml"), "r") as theme_file:
    data = toml.load(theme_file)
    theme = dacite.from_dict(Theme, data)
