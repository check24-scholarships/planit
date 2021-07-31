
from dataclasses import dataclass
import dacite
import toml
import os


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


@dataclass
class AppStyle:
    root_background: dict
    input_text: dict


@dataclass
class ToolbarStyle:
    button: dict
    button_selected: dict
    button_deselected: dict
    action_button_style: dict
    spacer_style: dict
    background_style: dict


@dataclass
class ToolStyles:
    swap_cursor: dict


@dataclass
class Theme:
    app_style: AppStyle
    toolbar_style: ToolbarStyle
    tool_styles: ToolStyles
    beet_view_style: BeetViewStyle
    beet_view_cell_style: BeetViewCellStyle


themes_folder = os.path.join(os.path.dirname(__file__), "themes")

# Load a theme
with open(os.path.join(themes_folder, "default_theme.toml"), "r") as theme_file:
    data = toml.load(theme_file)
    theme = dacite.from_dict(Theme, data)
