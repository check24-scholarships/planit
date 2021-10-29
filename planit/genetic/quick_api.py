
from . import plan_optimizer as optimizer


def table_to_plan(table):
    """
    Converts a 2d list of rows and columns to an optimizable plan.

    E.g.
    ```
    table_to_plan([["Carrot", "Cabbage", "Cabbage"],
                   ["Cabbage", "Beetroot", "Celery"]])
    ```
    """
    plants_by_pos = {}

    for y, row in enumerate(table):
        for x, plant in enumerate(row):
            plants_by_pos[(x, y)] = plant

    movable_plants = list(plants_by_pos.keys())
    return optimizer.Plan(plants_by_pos, movable_plants)


def optimize(table):
    """
    Optimises a plan and shows the result in the console.

    E.g.
    ```
    optimize([["Carrot", "Carrot", "Celery"]])

    optimize([["Celery",  "Beetroot", "Beetroot"],
              ["Cabbage", "Cabbage",  "Beetroot"],
              ["Cabbage", "Carrot",   "Celery"  ]])
    ```
    """
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

