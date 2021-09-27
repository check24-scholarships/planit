# -*- coding: utf-8 -*-

from .db import Db
from typing import Dict

# Create db object
db: Db = Db()


# Provide functions

def add_plant(alias: str, common_name: str) -> None:
    """ Add a plant to the db. """
    return db.add_plant(alias, common_name)

def get_all_plants() -> Dict[str, str]:
    """ Get all plants from the db. """
    return db.get_all_plants()

def get_symbiosis_score(plant_a: str, plant_b: str) -> int:
    """ Get the symbiosis score of the plants a and b from the db. """
    return db.get_symbiosis_score(plant_a, plant_b)
