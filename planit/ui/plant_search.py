

"""
Widget that lets the user select and search for plants.
"""

import tkinter as tk
from fuzzyset import FuzzySet
from .. import plant_data
from .widgets import CallbackEntry


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

        self.search_bar = CallbackEntry(self, command=self.on_keystroke)
        self.search_results = tk.Listbox(self)
        self.search_engine = PlantSearchSession()

        self.selected_plant = None

        self.search_bar.pack(fill=tk.X)
        self.search_results.pack(expand=True, fill=tk.BOTH)
        self.search_results.bind("<<ListboxSelect>>", self.on_select_plant)

    def on_keystroke(self, new_text):
        search_term = new_text

        results = self.search_engine.find(search_term)
        self.search_results.delete(0, tk.END)
        for res in results:
            self.search_results.insert(tk.END, res)

    def on_select_plant(self, event):
        selection = event.widget.curselection()

        if not selection:
            self.selected_plant = None
            return

        row = selection[0]
        plant = event.widget.get(row)
        self.selected_plant = plant


if __name__ == '__main__':
    root = tk.Tk()
    search = PlantSearchFrame(root)
    search.pack(expand=True, fill=tk.BOTH)
    root.mainloop()
