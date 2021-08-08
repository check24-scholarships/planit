
import operator


class Individual:
    """
    Represents one solution in a population.
    """

    fitness: int

    def randomize(self):
        """
        Initialises the individual with a random solution.
        """
        pass

    def mutate(self):
        pass

    def crossover(self, other) -> "Individual":
        pass

    def __repr__(self):
        if self.fitness is None:
            return f"(@{id(self)} -> 0)"

        return f"(@{id(self)} -> {self.fitness})"

    def __str__(self):
        return self.__repr__()


class Selection:
    """
    Different selection methods that define which individuals should be bred.
    """

    @staticmethod
    def tournament(population: list, offspring_count: int, contenders_per_round: int = 2):
        contenders = set(population)
        winner_pairs = []

        for _ in range(offspring_count):
            pair = []

            for _ in range(2):
                round_contenders = set(contenders.pop() for _ in range(contenders_per_round))
                winner = max(round_contenders, key=operator.attrgetter("fitness"))
                round_contenders.remove(winner)
                contenders.update(round_contenders)

                pair.append(winner)

            winner_pairs.append(pair)

        return winner_pairs

    @staticmethod
    def fittest(population: list, offspring_count: int):
        population.sort(reverse=True, key=operator.attrgetter("fitness"))
        parents_a = population[:offspring_count*2:2]
        parents_b = population[1:offspring_count*2:2]
        pairs = [(a, b) for a, b in zip(parents_a, parents_b)]
        return pairs


# TODO: Add stall generations counter


class Evolution:
    def __init__(
            self,
            individual_class,
            size: int,
            offspring_count: int,
            fitness_func,

            init_params={},
            randomize_params={},
            mutate_params={},
            crossover_params={},

            selection_method=Selection.tournament):

        assert offspring_count <= size/2

        self.individual_class = individual_class
        self.size = 0
        self.offspring_count = offspring_count
        self.fitness_func = fitness_func

        self.init_params = init_params
        self.randomize_params = randomize_params
        self.mutate_params = mutate_params
        self.crossover_params = crossover_params

        self.selection_method = selection_method

        self.population = []
        for i in range(size):
            self._add_random_individual()

    def _add_random_individual(self):
        """
        Adds a new individual to the population that is first randomized.
        """
        individual = self.individual_class(**self.init_params)
        individual.randomize(**self.randomize_params)
        individual.fitness = self.fitness_func(individual)
        self.population.append(individual)

    def _sort_population(self):
        """ Sorts the population based on the fitness scores from low to high. """
        self.population = sorted(self.population, key=operator.attrgetter("fitness"))

    def _kill_weakest(self, n):
        """ Removes the weakest n individuals from the population. """
        self._sort_population()
        del self.population[:n]

    def evolve(self):
        parent_pairs = self.selection_method(self.population, self.offspring_count)

        offsprings = []
        for (a, b) in parent_pairs:
            offspring = a.crossover(b, **self.crossover_params)
            offspring.mutate(**self.mutate_params)
            offspring.fitness = self.fitness_func(offspring)

            offsprings.append(offspring)

        self.population.extend(offsprings)
        self._kill_weakest(len(offsprings))

    def get_best(self):
        """ Returns the individual with the highest fitness. """
        return self.get_best_n(1)[0]

    def get_best_n(self, n):
        """ Returns the n best individuals with the highest fitness values. """
        self._sort_population()
        return self.population[len(self.population) - n:]
