

"""
Widget that lets the user select and search for plants.
"""

import tkinter as tk
from fuzzyset import FuzzySet
import planit.plant_data as plant_data
from .widgets import CallbackEntry, FancyListBox, SegmentedControl
from .theme import theme


class PlantSearchSession:
    """
    The PlantSearchSession is the fuzzy search engine for finding plants.

    It should be used for an entire session ( = as long as the app is open). You can only reap the performance
    benefits of the underlying FuzzySet if you initialise the session once and then reuse it for every search.
    """
    def __init__(self):
        self.all_plants = plant_data.get_all_plants()
        self.common_names = FuzzySet(
            self.all_plants,
            # This means that .get() will only return additional results that are
            # at least 50% as good as the best result.
            rel_sim_cutoff=0.5
        )

    def find(self, search_term) -> list:
        results = self.common_names.get(search_term)

        matched_common_names = [
            common_name
            for match_quality, common_name in (results if results is not None else [])
        ]

        return matched_common_names

    def get_all(self) -> list:
        return self.all_plants


class PlantSearchFrame (tk.Frame):
    def __init__(self, *args, **kwargs):
        super(PlantSearchFrame, self).__init__(*args, **kwargs, **theme.search.background)

        self.search_bar = CallbackEntry(self, command=self.on_keystroke, **theme.search.search_bar)
        self.search_results = FancyListBox(self, width=20, **theme.search.background)
        self.search_engine = PlantSearchSession()

        self.search_bar.pack(fill=tk.X, padx=20, ipady=5, pady=10)
        self.search_results.pack(expand=True, fill=tk.BOTH)

        self.selected_widgets_manager = SegmentedControl[str](
            selected_style=theme.search.result_selected,
            deselected_style=theme.search.result_deselected
        )

        self.plant_buttons = dict()
        self.visible_plants = set()
        self.all_plants = set(self.search_engine.get_all())

        # Show every plant when the app starts
        for plant in self.all_plants:
            self.add_result(plant.lower())

    @property
    def selected_plant(self):
        return self.selected_widgets_manager.selected_button

    def on_keystroke(self, new_text):
        search_term = new_text.strip()
        results = self.search_engine.find(search_term)

        previous_selection = self.selected_widgets_manager.selected_button

        if len(search_term) == 0:
            results = self.search_engine.get_all()

        results = [name.lower() for name in results]

        if search_term.lower() in results:
            self.selected_widgets_manager.select(search_term.lower())
        else:
            self.selected_widgets_manager.select(previous_selection)

        if len(results) == 1:
            identifier = results[0]
            self.selected_widgets_manager.select(identifier)

        self.show_plants(results)

    def add_result(self, name: str):
        style = {"bd": 0, **theme.search.result}
        plant_button = tk.Button(self.search_results.container, text=name.title(), **style)

        self.selected_widgets_manager.add_button(name, plant_button)
        self.search_results.add_element(plant_button)

        self.visible_plants.add(name)
        self.plant_buttons[name] = plant_button

    def show_plants(self, plants: list):
        plants = set(plants)
        plants_to_show = plants - self.visible_plants
        plants_to_hide = self.visible_plants - plants

        for plant in plants_to_show:
            self.search_results.show_element(self.plant_buttons[plant])

        for plant in plants_to_hide:
            self.search_results.hide_element(self.plant_buttons[plant])

        self.visible_plants = plants


if __name__ == '__main__':
    root = tk.Tk()
    search = PlantSearchFrame(root)
    search.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
