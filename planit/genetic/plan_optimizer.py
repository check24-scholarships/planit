
import random
from dataclasses import dataclass

from .genetic_algorithm import Evolution, Individual


# WIP, a lot is still going to change


@dataclass()
class Plant:
    species: str


class PlanRequirements:
    def __init__(self, positions, plants):
        self.positions = positions
        self.plants = plants


class Plan (Individual):
    def __init__(self, plan_requirements: PlanRequirements):
        self.plan_requirements = plan_requirements
        self.positions = plan_requirements.positions
        self.plants_by_pos = {}

    def randomize(self):
        plants = set(self.plan_requirements.plants)

        for pos in self.positions:
            self.plants_by_pos[pos] = plants.pop()

    def mutate(self):
        if len(self.positions) < 2:
            return

        # Pick two random plants and swap them
        a, b = random.sample(self.positions, 2)
        plants = self.plants_by_pos
        plants[a], plants[b] = plants[b], plants[a]

    def crossover(self, other):
        offspring = Plan(self.plan_requirements)
        offspring.plan_requirements = self.plants_by_pos
        return offspring


req = PlanRequirements(
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    ["Carrot", "Carrot", "Beetroot", "Beetroot"])

evo = Evolution(Plan, 50, 10, init_params={"plan_requirements"})

for i in range(100):
    evo.evolve()
