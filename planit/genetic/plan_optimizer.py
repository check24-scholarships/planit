
import random
from dataclasses import dataclass

from .genetic_algorithm import Evolution, Individual
from . import plantdata

from tabulate import tabulate


# WIP, a lot is still going to change


class Plan (Individual):
    def __init__(self, plants_by_pos: dict, movable_positions: list):
        self.movable_positions = movable_positions
        self.plants_by_pos = plants_by_pos

    def randomize(self):
        plants = list(self.plants_by_pos.values())
        random.shuffle(plants)

        for pos in self.movable_positions:
            self.plants_by_pos[pos] = plants.pop()

    def mutate(self):
        if len(self.movable_positions) < 2:
            return

        # Pick two random plants and swap them
        a, b = random.sample(self.movable_positions, 2)
        plants = self.plants_by_pos
        plants[a], plants[b] = plants[b], plants[a]

    def crossover(self, other):
        # TODO: Write the crossover algorithm
        offspring = Plan(self.plants_by_pos, self.movable_positions)
        return offspring

    def __str__(self):
        width = max(x for (x, y) in self.movable_positions)
        height = max(y for (x, y) in self.movable_positions)

        # Create the table filled with empty strings
        table = []
        for y in range(height + 1):
            table.append([""] * (width + 1))

        # Fill the table
        for pos, plant in self.plants_by_pos.items():
            table[pos[1]][pos[0]] = plant

        return tabulate(table)


@dataclass()
class PlantCombination:
    main_plant: str
    neighbours: list


# Relative positions of the tiles that affect the central tile
AFFECTED_TILES = [
    (-1, 1),  (0, 1),  (1, 1),
    (-1, 0),           (1, 0),
    (-1, -1), (0, -1), (-1, -1)
]


def get_plant_combinations(plan: Plan):
    plant_combinations = []

    for pos, plant in plan.plants_by_pos.items():
        neighbours = []

        for (dx, dy) in AFFECTED_TILES:
            neighbour_pos = (pos[0] + dx, pos[1] + dy)
            neighbour = plan.plants_by_pos.get(neighbour_pos, None)

            if neighbour is None:
                continue

            neighbours.append(neighbour)

        plant_combinations.append(PlantCombination(plant, neighbours))

    return plant_combinations


def get_neighbours(plan: Plan, pos):
    neighbours = []

    for (dx, dy) in AFFECTED_TILES:
        neighbour_pos = (pos[0] + dx, pos[1] + dy)
        neighbour = plan.plants_by_pos.get(neighbour_pos, None)

        if neighbour is None:
            continue

        neighbours.append(neighbour)

    return neighbours


def evaluate_plan(plan: Plan):
    plant_combinations = get_plant_combinations(plan)
    symbiosis_score = 0

    for combination in plant_combinations:
        plant = combination.main_plant
        score = sum(plantdata.get_symbiosis_score(plant, neighbour)
                    for neighbour in combination.neighbours) / len(AFFECTED_TILES)
        symbiosis_score += score

    symbiosis_score /= len(plant_combinations)
    return symbiosis_score


positions = [
    (x, y) for x in range(5) for y in range(5)
]

available_plants = ["Carrot", "Beetroot", "Cabbage", "Celery"]
plants = [available_plants[i % len(available_plants)] for i in range(len(positions))]
plants_by_pos = {(x, y): plant for (x, y), plant in zip(positions, plants)}

random_solution = Plan(plants_by_pos, positions)
random_solution.randomize()
plants_by_pos = random_solution.plants_by_pos
positions = random_solution.movable_positions

print(positions)
print(plants)

evo = Evolution(Plan, 50, 10, evaluate_plan, init_params={"plants_by_pos": plants_by_pos, "movable_positions": positions})

best = evo.population[0]
print(best)

for i in range(10000):
    evo.evolve()
    best = evo.get_best()
    print(best.fitness)

print(best)
print("---")
