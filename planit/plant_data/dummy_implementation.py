
from ..standard_types import Plant
from typing import Dict
import os
from functools import lru_cache
from .. import resources


@lru_cache(500)
def get_symbiosis_score(plant_a: Plant, plant_b: Plant) -> int:
    return 0


def get_all_plants() -> Dict[str, str]:
    return all_plants


# Load in the plant names from the ./plants.txt file

all_plants = {}
local_folder = os.path.dirname(__file__)
plants_list_file = resources.get("plantdata/plants.txt")

with open(plants_list_file, "r") as file:
    for line in file.readlines():
        line = line.strip()

        is_comment = line.startswith("#")
        if is_comment or not line:
            continue

        all_plants[line] = line
