
import random
from collections import Counter

from .genetic_algorithm import Evolution, Individual
from . import plantdata

from tabulate import tabulate
from tqdm import trange

import typing
from ..standard_types import *


class Plan (Individual):
    def __init__(self, plants_by_pos: dict, movable_positions: list):
        self.movable_positions = movable_positions
        self.plants_by_pos = dict(plants_by_pos)

    @staticmethod
    def from_dict(d: dict):
        plants_by_pos = {}

        for pos, plant in d["plants_by_pos"].items():
            plants_by_pos[(pos[0], pos[1])] = plant

        return Plan(plants_by_pos, d["movable_positions"])

    def to_dict(self):
        return {
            "plants_by_pos": self.plants_by_pos,
            "movable_positions": self.movable_positions
        }

    def randomize(self):
        plants = list(self.plants_by_pos[pos] for pos in self.movable_positions)
        random.shuffle(plants)

        for pos in self.movable_positions:
            self.plants_by_pos[pos] = plants.pop()

    def mutate(self, swap_chance=0.1):
        if len(self.movable_positions) < 2:
            return

        # Pick two random plants and swap them => "Swap mutation"
        if random.random() <= swap_chance:
            a, b = random.sample(self.movable_positions, 2)
            plants = self.plants_by_pos
            plants[a], plants[b] = plants[b], plants[a]

    def crossover(self, other: "Plan"):
        movable_positions = set(self.movable_positions)

        total_plant_counts = Counter(self.plants_by_pos[pos] for pos in movable_positions)
        current_plant_counts = Counter({plant: 0 for plant in total_plant_counts.keys()})

        offspring_plants = {}
        skipped_positions = []

        def try_insert(pos, plant):
            if current_plant_counts[plant] + 1 > total_plant_counts[plant]:
                return False

            offspring_plants[pos] = plant
            current_plant_counts[plant] += 1
            return True

        # 1. Randomly try to copy one plant from one of the two parent plans to the offspring.
        # Sometimes this isn't possible because the offspring already has so many plants of that type that
        # adding another one would exceed the original plant count.
        for pos in movable_positions:
            donor_a, donor_b = (self, other) if random.random() > 0.5 else (other, self)

            if try_insert(pos, donor_a.plants_by_pos[pos]):
                continue

            if try_insert(pos, donor_b.plants_by_pos[pos]):
                continue

            skipped_positions.append(pos)

        # 2. Go over the skipped positions and fill them with a remaining plant that is not yet in the offspring
        # enough times.
        remaining_plants = []
        for plant in total_plant_counts.keys():
            remaining_plants.extend([plant] * (total_plant_counts[plant] - current_plant_counts[plant]))

        for pos, plant in zip(skipped_positions, remaining_plants):
            offspring_plants[pos] = plant

        # 3. Copy the non-movable plants
        all_positions = set(self.plants_by_pos.keys())
        non_movable_positions = all_positions - movable_positions

        for pos in non_movable_positions:
            offspring_plants[pos] = self.plants_by_pos[pos]

        return Plan(offspring_plants, list(self.movable_positions))

    def __str__(self):
        if len(self.plants_by_pos) == 0:
            return ""

        width = max(x for (x, y) in self.plants_by_pos.keys())
        height = max(y for (x, y) in self.plants_by_pos.keys())

        offset_x = min(x for (x, y) in self.plants_by_pos.keys())
        offset_y = min(y for (x, y) in self.plants_by_pos.keys())

        width -= offset_x
        height -= offset_y

        # Create the table filled with empty strings
        table = []
        for y in range(height + 1):
            table.append([""] * (width + 1))

        # Fill the table
        for pos, plant in self.plants_by_pos.items():
            x, y = pos
            x -= offset_x
            y -= offset_y
            table[y][x] = plant if plant else "###"

        # Rows with a higher index (-> higher y) will be shown further down the on screen which is not desirable.
        # => Flip it
        table = reversed(table)
        return tabulate(table)


# Relative positions of the tiles that affect the central tile with the weight
# (x, y, weight)
AFFECTED_TILES = [
    (-1,  1, 0.5), (0, 1, 1),  (1,  1, 0.5),
    (-1,  0, 1),               (1,  0, 1),
    (-1, -1, 0.5), (0, -1, 1), (1, -1, 0.5)
]

AFFECTED_TILES_TOTAL = sum(weight for (x, y, weight) in AFFECTED_TILES)


def get_neighbours(plan: Plan, pos):
    neighbours: typing.List[typing.Tuple[Plant, float]] = []

    for (dx, dy, weight) in AFFECTED_TILES:
        neighbour_pos = (pos[0] + dx, pos[1] + dy)
        neighbour = plan.plants_by_pos.get(neighbour_pos, None)

        if neighbour is None:
            continue

        neighbours.append((neighbour, weight))

    return neighbours


class Evaluator:
    """
    Base class of evaluators that compute a fitness score for a plan
    """
    def evaluate(self, plan: Plan) -> float:
        pass


class SymbiosisEvaluator (Evaluator):
    """
    Evaluator that computes a fitness score based on the the symbioses / anti-symbioses a plant can have
    """

    def __init__(self, positive_weight=1, negative_weight=1):
        self.positive_weight = positive_weight
        self.negative_weight = negative_weight

    def get_modified_symbiosis_score(self, plant, neighbour, influence_weight) -> float:
        """
        Returns the symbiosis score based on the different weighting options
        """
        symbiosis_score = plantdata.get_symbiosis_score(plant, neighbour)
        symbiosis_score *= self.positive_weight if symbiosis_score > 0 else self.negative_weight
        symbiosis_score *= influence_weight
        return symbiosis_score

    def evaluate(self, plan: Plan) -> float:
        """
        Evaluates the total symbiosis score (fitness) of a plan.

        The formula:
        * total score = average symbiosis score of each plant
        * symbiosis score of a plant = average of the weighted symbiosis score with each neighbour
        """

        total_score = 0
        non_empty_count = 0

        for pos, plant in plan.plants_by_pos.items():
            if plant is None:
                continue
            non_empty_count += 1

            plant_score = sum(
                self.get_modified_symbiosis_score(plant, neighbour, weight)
                for neighbour, weight in get_neighbours(plan, pos))
            total_score += plant_score

        if non_empty_count == 0:
            return 0

        total_score /= (
            non_empty_count
            * len(AFFECTED_TILES)
            * max(self.negative_weight, self.positive_weight))

        return total_score


def optimize(plan: Plan, iterations=1000) -> Plan:
    evo = Evolution(
        Plan,
        50,
        10,
        evaluate_fitness,
        init_params={"plants_by_pos": plan.plants_by_pos, "movable_positions": plan.movable_positions})

    for i in trange(iterations, leave=False):
        evo.evolve()

    return evo.get_best()


evaluate_fitness = SymbiosisEvaluator().evaluate


if __name__ == '__main__':
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
    print(random_solution)

    best = optimize(random_solution)
    print(best.fitness)
    print(best)
