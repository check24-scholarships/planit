
import tkinter as tk
import typing


T = typing.TypeVar("T")


class SegmentedControl (typing.Generic[T]):
    def __init__(self, change_action: typing.Callable[[], None] = None):
        self.buttons_by_name: typing.Dict[T, tk.Button] = {}
        self.selected_button: typing.Union[T, None] = None
        self.change_action = change_action

    def add_button(self, name: T, button: tk.Button):
        button.config(command=lambda: self.select(name))
        self.buttons_by_name[name] = button

    def select(self, name: T):
        self.deselect(self.selected_button)
        button = self.buttons_by_name[name]
        button.config(background="#0af", foreground="white")

        if name != self.selected_button and self.change_action is not None:
            self.change_action()
        self.selected_button = name

    def deselect(self, name: T):
        if not name:
            return

        button = self.buttons_by_name[name]
        button.config(background="#eee", foreground="black")
        self.selected_button = None

    def clear_selection(self):
        self.deselect(self.selected_button)


class Toolbar (tk.Frame, SegmentedControl[str]):
    def __init__(self, root, **kwargs):
        tk.Frame.__init__(self, root, **kwargs)
        SegmentedControl.__init__(self)

    def add_button(self, name: str, text: str):
        button = tk.Button(self, text=text)
        button.pack(side=tk.LEFT)

        SegmentedControl.add_button(self, name, button)

        if len(self.buttons_by_name) == 1:
            self.select(name)

    def add_action(self, text: str, action: typing.Callable[[], None]):
        button = tk.Button(self, text=text, command=action)
        button.pack(side=tk.RIGHT)


if __name__ == '__main__':
    root = tk.Tk()
    toolbar = Toolbar(root)
    toolbar.pack()

    toolbar.add_button("Add", "Add +")
    toolbar.add_button("Subtract", "Subtract -")
    toolbar.add_button("Multiply", "Multiply *")
    root.mainloop()
