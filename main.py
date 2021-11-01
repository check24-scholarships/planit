
# Use lazy imports to reduce the startup time of the app
import lazy_import
for module in ["spacy", "fuzzyset2", "dacite", "planit.plant_data", "planit.plant_data.dummy", "toml",
               "beautifulsoup4", "bs4", "requests", "tabulate", "planit.genetic", "planit.crawler"]:
    lazy_import.lazy_module(module)


from planit.ui.ui import run_app


run_app()
