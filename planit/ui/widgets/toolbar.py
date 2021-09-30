
"""
Custom tkinter widgets and systems for handling toolbar-like systems.
"""

import tkinter as tk
import typing

from ..theme import theme


T = typing.TypeVar("T")


class SegmentedControl (typing.Generic[T]):
    def __init__(
            self,
            change_action: typing.Callable[[str, str], None] = None,
            selected_style: dict = None,
            deselected_style: dict = None):

        if selected_style is None:
            selected_style = {"background": "0af", "foreground": "white"}

        if deselected_style is None:
            deselected_style = {"background": "eee", "foreground": "black"}

        self.buttons_by_name: typing.Dict[T, tk.Button] = {}
        self.selected_button: typing.Union[T, None] = None
        self.change_action = change_action

        self.selected_style = selected_style
        self.deselected_style = deselected_style

    def add_button(self, name: T, button: tk.Button):
        button.config(command=lambda: self.select(name))
        self.buttons_by_name[name] = button

    def select(self, name: T):
        self.deselect(self.selected_button)
        button = self.buttons_by_name[name]
        button.config(**self.selected_style)

        if name != self.selected_button and self.change_action is not None:
            self.change_action(self.selected_button, name)
        self.selected_button = name

    def deselect(self, name: T):
        if not name:
            return

        button = self.buttons_by_name[name]
        button.config(**self.deselected_style)
        self.selected_button = None

    def clear_selection(self):
        self.deselect(self.selected_button)


class Toolbar (tk.Frame, SegmentedControl[str]):
    def __init__(self, root, change_action=None, **kwargs):
        tk.Frame.__init__(self, root, **kwargs, **theme.toolbar.background)

        SegmentedControl.__init__(
            self,
            change_action=change_action,
            selected_style=theme.toolbar.button_selected,
            deselected_style=theme.toolbar.button_deselected)

    def add_button(self, name: str, text: str):
        button = tk.Button(self, text=text, **{**theme.toolbar.button, **theme.toolbar.button_deselected})
        button.pack(side=tk.LEFT, ipadx=5, ipady=2, padx=(10, 0), pady=5)

        SegmentedControl.add_button(self, name, button)

        if len(self.buttons_by_name) == 1:
            self.select(name)

    def add_action(self, text: str, action: typing.Callable[[], None]):
        """
        Actions are buttons that appear on the right hand side of the toolbar and can
        only be clicked, not permanently selected.
        """
        button = tk.Button(self, text=text, command=action,
                           **{**theme.toolbar.button, **theme.toolbar.action_button})
        button.pack(side=tk.RIGHT, ipadx=5, ipady=2, padx=(0, 10), pady=5)

    def add_spacer(self):
        spacer = tk.Label(self, width=2, **theme.toolbar.spacer)
        spacer.pack(side=tk.LEFT)

    @property
    def tool(self) -> str:
        return self.selected_button


if __name__ == '__main__':
    root = tk.Tk()
    toolbar = Toolbar(root)
    toolbar.pack()

    toolbar.add_button("Add", "Add +")
    toolbar.add_button("Subtract", "Subtract -")
    toolbar.add_button("Multiply", "Multiply *")
    root.mainloop()
