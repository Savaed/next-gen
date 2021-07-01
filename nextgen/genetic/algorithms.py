from timeit import default_timer as timer

import numpy as np

from nextgen.genetic.decoder import BinaryDecoder
from nextgen.genetic.factory import GeneticOperatorsFactory
from nextgen.genetic.helpers import get_random_at_interval
from nextgen.genetic.models import (
    ChromosomeRepresentation,
    EvolutionConfig,
    EvolutionHistory,
    EvolutionResult,
    FitnessFunctionConfig,
)
from nextgen.genetic.selection import Selection


class EvoAlgorithm(object):
    def __init__(
        self,
        function_config: FitnessFunctionConfig,
        evolution_config: EvolutionConfig,
        representation: ChromosomeRepresentation,
        precision: int = 6,
    ) -> None:
        self._representation = representation
        self._operators = GeneticOperatorsFactory(
            evolution_config.mutation.type,
            evolution_config.crossover.type,
            crossover_points=evolution_config.crossover.points_number,
            mutation_points=evolution_config.mutation.points_number,
            arg_min=function_config.arg_min,
            arg_max=function_config.arg_max,
        ).get_operators(representation)

        if representation == ChromosomeRepresentation.BINARY:
            self._decoder = BinaryDecoder(function_config.arg_min, function_config.arg_max, precision)
            self._population_shape = (evolution_config.population_size, 2 * self._decoder.argument_bit_length)

        if representation == ChromosomeRepresentation.REAL:
            self._population_shape = (evolution_config.population_size, 2)

        self._selection = Selection(
            evolution_config.selection.selection_type,
            k=evolution_config.selection.duel_groups,
            n=evolution_config.selection.duel_group_size,
        )
        self._function_config = function_config
        self._evolution_config = evolution_config
        self._population = np.array([])
        self._rng = np.random.default_rng()

    def evolve(self) -> EvolutionResult:
        start = timer()
        optimized = False
        history = EvolutionHistory()
        generation = 0
        self._population = self._init_population()
        decode = self._representation == ChromosomeRepresentation.BINARY

        while not optimized and generation < self._evolution_config.generations:
            evaluated_population, optimized, best_solution = self._evaluate(decode)

            history.add(evaluated_population, best_solution)

            self._population = self._selection.select(
                evaluated_population,
                self._evolution_config.extra.use_elite,
                self._evolution_config.extra.elite_percentage,
                self._evolution_config.selection.best_percentage,
            )
            self._cross()
            self._mutate()

            if self._evolution_config.extra.use_inverse and self._representation == ChromosomeRepresentation.BINARY:
                self._inverse()

            generation += 1

        end = timer() - start
        return EvolutionResult(history, end)

    # region Privates

    def _cross(self) -> None:
        if self._population_shape[0] < 2:
            raise ValueError("To crossover the population must contain at least 2 individuals")

        single_individual = np.array([])

        # Move individual to a new population if the old is odd.
        if self._population_shape[0] % 2 == 1:
            single_individual = self._population[-1]
            self._population = np.delete(self._population, -1, 0)

        cross_probability = self._rng.random(self._population_shape[0])
        pairs = list(zip(self._population[:-1:2], self._population[1::2]))
        potential_parents = list(zip(cross_probability, pairs))
        self._population = np.array([])

        for probability, parents in potential_parents:
            if probability < self._evolution_config.crossover.probability:
                childs = self._operators.cross(np.array(parents))
                self._population = np.append(self._population, childs)
            else:
                self._population = np.append(self._population, parents)

        self._population = (
            np.append(self._population, single_individual)
            .reshape(self._population_shape)
            .astype(np.int8 if self._representation == ChromosomeRepresentation.BINARY else np.float32)
        )

    def _evaluate(self, decode: bool) -> tuple[np.ndarray, bool, float]:
        if decode:
            decoded_population = np.apply_along_axis(self._decoder.decode_individual, 1, self._population)
        else:
            decoded_population = self._population

        evaluated_population: np.ndarray = np.apply_along_axis(
            self._function_config.fitness_function, 1, decoded_population
        )

        best_solution = self._get_best_solution(decoded_population, evaluated_population)
        optimized = abs(best_solution[-1] - self._function_config.optimum) < self._evolution_config.tollerance

        # 'solutions' will be in format [[chromosome], fitness_function_value] eg. [[1,1,0,1,1,0], 2.5]
        solutions = np.array(list(zip(self._population, evaluated_population)))
        return solutions, optimized, best_solution

    def _mutate(self) -> None:
        mutate_probability = self._rng.random(self._population_shape[0])
        potential_mutants = list(zip(mutate_probability, self._population))

        for i, (probability, individual) in enumerate(potential_mutants):
            if probability < self._evolution_config.mutation.probability:
                self._population[i] = self._operators.mutate(individual)

    def _inverse(self) -> None:
        inverse_probability = self._rng.random(size=self._population_shape[0])
        potenial_inverted = list(zip(inverse_probability, self._population))

        for i, (probability, individual) in enumerate(potenial_inverted):
            if probability < self._evolution_config.extra.inverse_probability:
                self._population[i] = self._operators.inverse(individual)

    def _init_population(self) -> np.ndarray:
        population_size = self._population_shape[0] * self._population_shape[1]

        if self._representation == ChromosomeRepresentation.BINARY:
            random_population = self._rng.integers(0, 1, size=population_size, endpoint=True)

        if self._representation == ChromosomeRepresentation.REAL:
            random_population = get_random_at_interval(
                self._function_config.arg_min, self._function_config.arg_max, population_size
            )

        return random_population.reshape(self._population_shape)

    def _get_best_solution(self, decoded_population: np.ndarray, evaluated_population: np.ndarray) -> np.ndarray:
        best_solution = [decoded_population[evaluated_population.argmin()], evaluated_population.min()]
        return np.append(np.array([x for x in best_solution[0]]), best_solution[-1])

    # endregion
