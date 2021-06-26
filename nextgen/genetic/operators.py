from abc import abstractmethod

import numpy as np

from nextgen.genetic.helpers import get_random_at_interval, random_unique_int
from nextgen.genetic.models import BinaryCrossoverType, BinaryMutationType, RealCrossoverType, RealMutationType


@abstractmethod
class GeneticOperators(object):
    def cross(self, parents: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def mutate(self, individual: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class BinaryGeneticOperators(GeneticOperators):
    def __init__(self, mutation_type: BinaryMutationType, crossover_type: BinaryCrossoverType, **kwargs) -> None:
        self._mutation_type = mutation_type
        self._crossover_type = crossover_type
        self._rng = np.random.default_rng()

        self._crossover_points_number = kwargs["crossover_points"] if "crossover_points" in kwargs else 1
        self._mutation_points_number = kwargs["mutation_points"] if "mutation_points" in kwargs else 1

    @property
    def operators_types(self) -> tuple[BinaryCrossoverType, BinaryMutationType]:
        return self._crossover_type, self._mutation_type

    @property
    def crossover_points_number(self) -> int:
        return self._crossover_points_number

    @property
    def mutation_points_number(self) -> int:
        return self._mutation_points_number

    def cross(self, parents: np.ndarray) -> np.ndarray:
        childs = parents.copy()
        individual_size = parents[0][0].size

        if self._crossover_type == BinaryCrossoverType.UNIFORM:
            swaps = self._rng.integers(0, 1, size=individual_size, endpoint=True)

            for i, swap in enumerate(swaps):
                if swap:
                    childs[0][i], childs[1][i] = childs[1][i], childs[0][i]

            return childs

        if individual_size - 1 < self._crossover_points_number:
            return childs

        slices = self._get_slices(individual_size)

        for i, slice in enumerate(slices):
            start, stop = slice

            if i % 2 == 1:
                childs[0][start:stop], childs[1][start:stop] = parents[1][start:stop], parents[0][start:stop]

        return childs

    def mutate(self, individual: np.ndarray) -> np.ndarray:
        x_men = individual.copy()

        if self._mutation_type == BinaryMutationType.EDGE:
            x_men[-1] ^= 1  # Invert a single gen using XOR with '1' mask: 1 XOR 1 => 0, 0 XOR 1 => 1
            return x_men

        mutation_indexes = random_unique_int(0, x_men.size - 1, size=self._mutation_points_number)

        for i in mutation_indexes:
            x_men[i] ^= 1

        return x_men

    def inverse(self, individual: np.ndarray) -> np.ndarray:
        if individual.size < 4:
            return individual.copy()

        pivot_indexes = sorted(random_unique_int(1, individual.size - 2, size=2))

        mr_negative = individual.copy()
        mr_negative[pivot_indexes[0] : pivot_indexes[1]] = individual[pivot_indexes[1] - 1 : pivot_indexes[0] - 1 : -1]

        return mr_negative

    # region Privates

    def _get_slices(self, individual_size: int) -> list[tuple[int, int]]:
        # Get n sorted random ints from [1, len(individual) - 1], where n: number of pivot points in the crossover.
        pivot_indexes = sorted(random_unique_int(1, individual_size - 2, size=self._crossover_points_number))

        # Create tuples with start, stop cross indexes. Add tuples: (0, first_pivot) and (last_pivot, len(individual))
        slices = [(0, pivot_indexes[0])]
        slices += list(zip(pivot_indexes[:-1], pivot_indexes[1:]))
        slices.append((pivot_indexes[-1], individual_size))

        return slices

    # endregion


class RealGeneticOperators(GeneticOperators):
    def __init__(
        self, mutation_type: RealMutationType, crossover_type: RealCrossoverType, arg_min: float, arg_max: float
    ) -> None:
        self._mutation_type = mutation_type
        self._crossover_type = crossover_type
        self._arg_min = arg_min
        self._arg_max = arg_max

    def mutate(self, individual: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng()
        i = rng.integers(0, individual.size)
        individual[i] = get_random_at_interval(self._arg_min, self._arg_max, 1)
        return individual

    def cross(self, parents: np.ndarray) -> np.ndarray:
        if self._crossover_type == RealCrossoverType.ARITHMETIC:
            return self._arithmetic_cross(parents)

        if self._crossover_type == RealCrossoverType.HEURISTIC:
            return self._heuristic_cross(parents)

    # region Privates

    def _arithmetic_cross(self, parents: np.ndarray) -> np.ndarray:
        k = np.random.default_rng().random()
        child1 = [k * parents[0][0] + (1 - k) * parents[1][0], k * parents[0][1] + (1 - k) * parents[1][1]]
        child2 = [(1 - k) * parents[0][0] + k * parents[1][0], (1 - k) * parents[0][1] + k * parents[1][1]]
        return np.array([child1, child2])

    def _heuristic_cross(self, parents: np.ndarray) -> np.ndarray:
        k = np.random.default_rng().random()
        child = [
            k * abs(parents[1][0] - parents[0][0] + parents[0][0]),
            k * abs(parents[1][1] - parents[0][1] + parents[0][1]),
        ]
        return child

    # endregion
