

"""
Widget that lets the user select and search for plants.
"""

import tkinter as tk
from fuzzyset import FuzzySet
import planit.plant_data.dummy as plant_data
from .widgets import CallbackEntry, FancyListBox, SegmentedControl
from .theme import theme


class PlantSearchSession:
    """
    The PlantSearchSession is the fuzzy search engine for finding plants.

    It should be used for an entire session ( = as long as the app is open). You can only reap the performance
    benefits of the underlying FuzzySet if you initialise the session once and then reuse it for every search.
    """
    def __init__(self):
        self.plants_by_common_name = plant_data.get_all_plants()
        self.common_names = FuzzySet(
            self.plants_by_common_name.keys(),
            # This means that .get() will only return additional results that are
            # at least 50% as good as the best result.
            rel_sim_cutoff=0.5
        )

    def find(self, search_term) -> dict:
        results = self.common_names.get(search_term)

        matched_common_names = [
            common_name
            for match_quality, common_name in (results if results is not None else [])
        ]

        matched_plants_by_common_name = {
            common_name: self.plants_by_common_name[common_name]
            for common_name in matched_common_names
        }

        return matched_plants_by_common_name

    def get_all(self) -> dict:
        return self.plants_by_common_name


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

        # Mimics user input, shows all plants when the app starts, as if the user had cleared the search query.
        self.on_keystroke("")

    @property
    def selected_plant(self):
        return self.selected_widgets_manager.selected_button

    def on_keystroke(self, new_text):
        search_term = new_text
        results = self.search_engine.find(search_term)

        previous_selection = self.selected_widgets_manager.selected_button
        self.search_results.clear()
        self.selected_widgets_manager.remove_all_buttons()

        already_selected = False

        if len(search_term) == 0:
            results = self.search_engine.get_all()

        for name in results:
            self.add_result(name)
            if name.lower() == search_term.lower():
                self.selected_widgets_manager.select(name)
                already_selected = True

        if len(results) == 1:
            identifier = next(iter(results.values()))
            self.selected_widgets_manager.select(identifier)

        if not already_selected:
            self.selected_widgets_manager.select(previous_selection)

    def add_result(self, name: str):
        style = {"bd": 0, **theme.search.result}
        plant_button = tk.Button(self.search_results.container, text=name.title(), **style)

        self.selected_widgets_manager.add_button(name, plant_button)
        self.search_results.add_element(plant_button)


if __name__ == '__main__':
    root = tk.Tk()
    search = PlantSearchFrame(root)
    search.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
