
"""
Mocked plant data
"""

SYMBIOSES = {
    ("Carrot", "Beetroot"): 1,
    ("Carrot", "Celery"): 1,
    ("Celery", "Beetroot"): 1,

    ("Cabbage", "Carrot"): -1,
    ("Cabbage", "Celery"): -1
}


# For type hinting
Plant = str


def get_symbiosis_score(plant_a: Plant, plant_b: Plant) -> int:
    score = SYMBIOSES.get((plant_a, plant_b), None)
    if score is not None:
        return score

    score = SYMBIOSES.get((plant_b, plant_a), None)
    if score is not None:
        return score

    return 0


def visualize_symbioses():
    from tabulate import tabulate

    plants = ["Carrot", "Celery", "Cabbage", "Beetroot"]
    table = [["", *plants]]

    for plant_col in plants:
        row = [plant_col]

        for plant_row in plants:
            score = get_symbiosis_score(plant_col, plant_row)
            row.append("+" if score == 1 else "-" if score == -1 else "#")

        table.append(row)

    print(tabulate(table, stralign="center"))