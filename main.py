
import planit.genetic.plan_optimizer as optimizer
from planit.genetic.plantdata import visualize_symbioses
from planit.ui.ui import run_app


run_app()


def table_to_plan(table):
    plants_by_pos = {}

    for y, row in enumerate(table):
        for x, plant in enumerate(row):
            plants_by_pos[(x, y)] = plant

    movable_plants = list(plants_by_pos.keys())
    return optimizer.Plan(plants_by_pos, movable_plants)


def optimize(table):
    plan = table_to_plan(table)

    print("\n\n")
    print("Before:")
    print(optimizer.evaluate_fitness(plan))
    print(plan)

    best = optimizer.optimize(plan, 1000)

    print("")
    print("After:")
    print(best.fitness)
    print(best)


visualize_symbioses()


optimize([["Carrot", "Carrot", "Celery"]])

optimize([["Carrot", "Cabbage", "Cabbage"],
          ["Cabbage", "Beetroot", "Celery"]])

optimize([["Celery", "Beetroot", "Beetroot"],
          ["Cabbage", "Cabbage", "Beetroot"],
          ["Cabbage", "Carrot", "Celery"]])
