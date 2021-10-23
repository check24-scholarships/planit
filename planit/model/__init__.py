# -*- coding: utf-8 -*-

from .db import Db
from typing import Dict

# Create db object
db: Db = Db()


# Provide functions

def add_plant(alias: str, common_name: str) -> bool:
    """ Add a plant to the db if it does not exist so far. """
    return db.add_plant(alias, common_name)

def add_symbiosis_score(plant_a: str, plant_b: str, score: int) -> bool:
    """ Add a symbiosis score to the db if it does not exist so far. """
    return db.add_symbiosis_score(plant_a, plant_b, score)

def get_all_plants() -> Dict[str, str]:
    """ Get all plants from the db. """
    return db.get_all_plants()

def get_symbiosis_score(plant_a: str, plant_b: str) -> int:
    """ Get the symbiosis score of the plants a and b from the db. """
    return db.get_symbiosis_score(plant_a, plant_b)
