
SYMBIOSIS = {
    ("Carrot", "Beetroot"): 1,

    ("Cabbage", "Carrot"): -1,
    ("Cabbage", "Beetroot"): 0,

    ("Celery", "Beetroot"): 1,
    ("Celery", "Carrot"): 1,
    ("Celery", "Cabbage"): 0
}


def get_symbiosis_score(plant_a, plant_b):
    score = SYMBIOSIS.get((plant_a, plant_b), None)
    if score is not None:
        return score

    score = SYMBIOSIS.get((plant_b, plant_a), None)
    if score is not None:
        return score

    return 0
