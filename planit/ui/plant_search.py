

"""
Widget that lets the user select and search for plants.
"""

import tkinter as tk
from fuzzyset import FuzzySet
from .. import plant_data
from .widgets import CallbackEntry, FancyListBox, SegmentedControl


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


class PlantSearchFrame (tk.Frame):
    def __init__(self, *args, **kwargs):
        super(PlantSearchFrame, self).__init__(*args, **kwargs)

        self.search_bar = CallbackEntry(self, command=self.on_keystroke, width=25)
        self.search_results = FancyListBox(self, width=20)
        self.search_engine = PlantSearchSession()

        self.search_bar.pack(fill=tk.X)
        self.search_results.pack(expand=True, fill=tk.BOTH)

        self.selected_widgets_manager = SegmentedControl[str]()

    @property
    def selected_plant(self):
        return self.selected_widgets_manager.selected_button

    def on_keystroke(self, new_text):
        search_term = new_text
        results = self.search_engine.find(search_term)

        previous_selection = self.selected_widgets_manager.selected_button
        self.search_results.clear()
        self.selected_widgets_manager.remove_all_buttons()

        for res in results:
            self.add_result(res)

        self.selected_widgets_manager.select(previous_selection)

    def add_result(self, name: str):
        style = {"bd": 0}
        plant_button = tk.Button(self.search_results.container, text=name, **style)
        self.selected_widgets_manager.add_button(name, plant_button)
        self.search_results.add_element(plant_button)


if __name__ == '__main__':
    root = tk.Tk()
    search = PlantSearchFrame(root)
    search.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
