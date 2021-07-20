
import random
from dataclasses import dataclass

from .genetic_algorithm import Evolution, Individual
from . import plantdata

from tabulate import tabulate


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
        plants = list(self.plan_requirements.plants)
        random.shuffle(plants)

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
        # TODO: Write the crossover algorithm
        offspring = Plan(self.plan_requirements)
        offspring.plan_requirements = self.plan_requirements
        offspring.plants_by_pos = dict(self.plants_by_pos)
        return offspring

    def __str__(self):
        width = max(x for (x, y) in self.positions)
        height = max(y for (x, y) in self.positions)

        table = []
        for y in range(height + 1):
            table.append([""] * (width + 1))

        for pos, plant in self.plants_by_pos.items():
            table[pos[1]][pos[0]] = plant

        return tabulate(table)


@dataclass()
class PlantCombination:
    main_plant: str
    neighbours: list


AFFECTED_TILES = [
    (-1, 1),  (0, 1),  (1, 1),
    (-1, 0),           (1, 0),
    (-1, -1), (0, -1), (-1, -1)
]


def get_plant_combinations(plan: Plan):
    plant_combinations = []

    for pos, plant in plan.plants_by_pos.items():
        neighbours = []

        for relative_pos in AFFECTED_TILES:
            neighbour_pos = (pos[0] + relative_pos[0], pos[1] + relative_pos[1])
            neighbour = plan.plants_by_pos.get(neighbour_pos, None)

            if neighbour is None:
                continue

            neighbours.append(neighbour)

        plant_combinations.append(PlantCombination(plant, neighbours))

    return plant_combinations


def evaluate_plan(plan: Plan):
    plant_combinations = get_plant_combinations(plan)
    symbiosis_score = 0

    for combination in plant_combinations:
        plant = combination.main_plant
        score = sum(plantdata.get_symbiosis_score(plant, neighbour) for neighbour in combination.neighbours) / 8
        symbiosis_score += score / len(plant_combinations)

    return symbiosis_score


positions = [
    (x, y) for x in range(5) for y in range(5)
]

available_plants = ["Carrot", "Beetroot", "Cabbage", "Celery"]
plants = [available_plants[i % len(available_plants)] for i in range(len(positions))]

req = PlanRequirements(positions, plants)

print(positions)
print(plants)

evo = Evolution(Plan, 50, 10, evaluate_plan, init_params={"plan_requirements": req})

evo.get_best()
print(evo.population[0])

for i in range(1000):
    evo.evolve()
    best = evo.get_best()
    print(best.fitness)

print(best)
print("---")
