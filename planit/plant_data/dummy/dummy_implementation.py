
import json

from standard_types import Plant
from planit import resources


def get_symbiosis_score(plant_a: Plant, plant_b: Plant) -> int:
    if plant_a in symbiosis_table:
        return symbiosis_table[plant_a].get(plant_b, 0)
    return 0


def get_all_plants() -> list:
    return all_plants


# Load in the plant names from the ./plants.txt file

all_plants = []
symbiosis_table = {}

with open(resources.get("plantdata/plants.txt"), "r") as file:
    for line in file.readlines():
        line = line.strip()

        is_comment = line.startswith("#")
        if is_comment or not line:
            continue

        all_plants.append(line)

with open(resources.get("plantdata/symbiosis_data.json"), "r") as file:
    symbiosis_table = json.load(file)
