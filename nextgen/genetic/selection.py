import math

import numpy as np

from nextgen.genetic.models import SelectionType


class Selection(object):
    def __init__(self, selection_type: SelectionType, maximum=False, **kwargs) -> None:
        self._selection_type = selection_type
        self._k = kwargs["k"] if "k" in kwargs else 2
        self._n = kwargs["n"] if "n" in kwargs else 2

    def select(
        self, population: np.ndarray, elite: bool = False, elite_percentage: float = 0.0, best_percentage: float = 0.0
    ) -> np.ndarray:
        new_population = np.array([])

        if elite:
            new_population, population = self._select_by_best(population, elite_percentage)
            np.random.default_rng().shuffle(population)

        if self._selection_type == SelectionType.ROULETTE:
            return np.append(new_population, self._select_by_roulette(population))

        if self._selection_type == SelectionType.RANK:
            return np.append(new_population, self._select_by_rank(population))

        if self._selection_type == SelectionType.DUEL:
            return np.append(new_population, self._select_by_duel(population, self._k, self._n))

        if self._selection_type == SelectionType.DOUBLE_DUEL:
            return np.append(new_population, self._select_by_duel(population, self._k, self._n, double=True))

        if self._selection_type == SelectionType.BEST:
            return np.append(new_population, self._select_by_best(population, best_percentage))

        raise ValueError("Unsupported selection type")

    # region Privates

    def _select_by_rank(self, population: np.ndarray) -> np.ndarray:
        individual_values = np.array([abs(individual_info[1]) for individual_info in population])
        new_population = []

        ranks = self._create_ranks(individual_values)

        for repeats, i in ranks:
            new_population.extend([population[i] for _ in range(repeats)])

        # Shuffle new population (it will be larger then the original one) and takes pop_size elements.
        new_population = np.array(new_population)[:, 0]
        np.random.shuffle(new_population)
        return new_population[: population.shape[0]]

    def _create_ranks(self, individual_values):
        sorted_indexes = np.argsort(individual_values)
        repeats = [len(sorted_indexes) - i for i in range(len(sorted_indexes))]
        ranks = list(zip(repeats, sorted_indexes))
        return ranks

    def _select_by_roulette(self, population: np.ndarray) -> np.ndarray:
        selected_population_info = {}
        selected_population = []

        # The fitness function values should be '1 / fitness function' if a problem is to minimize function.
        individual_values = np.array([1 / abs(individual_info[1]) for individual_info in population])

        fitness_function_sum = sum(individual_values)
        choosing_probability = individual_values / fitness_function_sum
        distribution = np.array([0.0] + list(np.cumsum(choosing_probability)))
        choices = np.random.default_rng().random(size=population.shape[0])

        # Calculate how many particular individuals copies will be in the next generation.
        for i in range(len(distribution) - 1):
            selected_population_info[i] = np.count_nonzero(
                (distribution[i] < choices) & (choices < distribution[i + 1])
            )

        # Get n=copies_number copies of individual at index=individual_index from collection=population.
        for individual_index, copies_number in selected_population_info.items():
            selected_population += [population[individual_index] for _ in range(copies_number)]

        return np.array(selected_population)[:, 0]

    def _select_by_duel(self, population: np.ndarray, k: int, n: int, double: bool = False) -> np.ndarray:
        new_population = []

        # Calculate max number of groups (duels).
        population_size = population.shape[0]
        max_k = math.ceil(population_size / n)

        # If intial duel groups (k) is greater than the maximum number max_k OR
        # entire population cannot be divided equally into k groups of n individuals
        # each (population_size // n != k) then set the number of groups k to max_k.
        k = max_k if (k > max_k or population_size // n != k) else k

        missing_individuals = population_size

        while missing_individuals > 0:
            # This prevents selecting more individuals than necessary to obtain a new population of size equals to the old population.
            k = k if missing_individuals > k else missing_individuals

            groups = np.array_split(population, k)
            winners = list(map(self._get_duel_winner, np.array(groups)))

            if double and len(winners) > 1:
                groups = np.array_split(winners, k // 2)
                winners = list(map(self._get_duel_winner, np.array(groups)))

            new_population += winners
            missing_individuals = population_size - len(new_population)

        return np.array(new_population)[:, 0]

    def _select_by_best(self, population: np.ndarray, best_percentage: float = 0.3) -> np.ndarray:
        # Sort group by the last column (fitness function value) and get the minimum/maximum values.
        sorted_population = population[population[:, -1].argsort()]

        pivot_index = math.ceil(best_percentage * len(sorted_population))
        return (sorted_population[:pivot_index][:, 0], sorted_population[pivot_index:])

    def _get_duel_winner(self, group: np.ndarray) -> np.ndarray:
        # Sort group by the last column (fitness function value) and get the minimum value [0].
        winner = group[group[:, -1].argsort()][0]
        return winner

    # endregion
