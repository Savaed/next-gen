import math
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Union

import numpy as np


FitnessFunctionConfig = namedtuple(
    "FitnessFunctionConfig", ["arg_min", "arg_max", "x1_for_optimum", "x2_for_optimum", "optimum", "formula"]
)


class ChromosomeRepresentation(str, Enum):
    BINARY = "binary"
    REAL = "real"


class BinaryCrossoverType:
    MULTI_POINTS = "multiPoints"
    UNIFORM = "uniform"


class RealCrossoverType(str, Enum):
    ARITHMETIC = "arithmetic"
    HEURISTIC = "heuristic"


class BinaryMutationType:
    MULTI_POINTS = "multiPoints"
    EDGE = "edge"


class RealMutationType(str, Enum):
    UNIFORM = "uniform"


class SelectionType(str, Enum):
    BEST = "best"
    DUEL = "duel"
    DOUBLE_DUEL = "doubleDuel"
    RANK = "rank"
    ROULETTE = "roulette"


class SupportedFunctionName(str, Enum):
    BOOTH = "booth"
    BEALE = "beale"
    DROP_WAVE = "dropWave"
    EGGHOLDER = "eggholder"
    EASOM = "easom"


class EvolutionHistory(object):
    """The complete history of evolution algorithms.

    Contains mean, standard devation and best solution over generations.
    """

    def __init__(self) -> None:
        self._history = np.array([])

    def add(self, evaluated_population: np.ndarray, best_solution: np.ndarray) -> None:
        """Add a new entry to the evolution history.

        Parameters
        ----------
        evaluated_population : np.ndarray
            An array-like object contained evaluation population in i-th generation.
        best_solution : np.ndarray
            The best (with min. or max fitness function value) solution in i-th generation.
        """

        new_row_data = np.array(
            [
                evaluated_population[:, -1].mean(),
                evaluated_population[:, -1].std(),
                best_solution,
            ]
        )
        self._history = np.append(self._history, new_row_data)

    @property
    def means(self) -> np.ndarray:
        return self._history.reshape((-1, 3))[:, 0]

    @property
    def std(self) -> np.ndarray:
        return self._history.reshape((-1, 3))[:, 1]

    @property
    def best_solutions(self) -> np.ndarray:
        return np.stack(self._history.reshape((-1, 3))[:, 2])


class EvolutionResult(object):
    """The result of evolution algorithm.

    Contains elapsed time in seconds, history object, best solution and number of generations.
    """

    def __init__(self, history: EvolutionHistory, elpsed_seconds: float) -> None:
        self._elpsed_seconds = elpsed_seconds
        self._history = history

    @property
    def elapsed_seconds(self) -> float:
        return round(self._elpsed_seconds, 2)

    @property
    def evo_history(self) -> EvolutionHistory:
        return self._history

    @property
    def best_solution(self) -> np.ndarray:
        best_solution_index = np.stack(self._history.best_solutions)[:, -1].argmin()
        return self._history.best_solutions[best_solution_index]

    @property
    def generations(self) -> int:
        return self._history.best_solutions.shape[0]


class SupportedFunction(object):
    """Contains all suported 2D functions."""

    def __init__(self) -> None:
        self._functions = dict()

        self._functions[SupportedFunctionName.BOOTH] = FitnessFunctionConfig(
            arg_min=-10.0,
            arg_max=10.0,
            x1_for_optimum=1.0,
            x2_for_optimum=3.0,
            optimum=0.0,
            formula=lambda x: ((x[0] + 2.0 * x[1] - 7) ** 2 + (2.0 ** x[0] + x[1] - 5) ** 2),
        )

        self._functions[SupportedFunctionName.BEALE] = FitnessFunctionConfig(
            arg_min=-4.5,
            arg_max=4.5,
            x1_for_optimum=3.0,
            x2_for_optimum=0.5,
            optimum=0.0,
            formula=lambda x: (
                (1.5 - x[0] + x[0] * x[1]) ** 2
                + (2.25 - x[0] + x[0] * x[1] ** 2) ** 2
                + (2.625 - x[0] + x[0] * x[1] ** 3) ** 2
            ),
        )

        self._functions[SupportedFunctionName.DROP_WAVE] = FitnessFunctionConfig(
            arg_min=-5.12,
            arg_max=5.12,
            x1_for_optimum=0.0,
            x2_for_optimum=0.0,
            optimum=-1.0,
            formula=lambda x: (
                -(1.0 + math.cos(12.0 * math.sqrt(x[0] * x[0] + x[1] * x[1])))
                / (0.5 * (x[0] * x[0] + x[1] * x[1]) + 2.0)
            ),
        )

        self._functions[SupportedFunctionName.EGGHOLDER] = FitnessFunctionConfig(
            arg_min=-512.0,
            arg_max=512.0,
            x1_for_optimum=512.0,
            x2_for_optimum=404.2319,
            optimum=-959.6407,
            formula=lambda x: (
                -(x[1] + 47.0) * math.sin(math.sqrt(abs(x[1] + (x[0] / 2.0) + 47.0)))
                - x[0] * math.sin(math.sqrt(abs(x[0] - (x[1] + 47.0))))
            ),
        )

        self._functions[SupportedFunctionName.EASOM] = FitnessFunctionConfig(
            arg_min=-100.0,
            arg_max=100.0,
            x1_for_optimum=math.pi,
            x2_for_optimum=math.pi,
            optimum=-1.0,
            formula=lambda x: (
                -math.cos(x[0]) * math.cos(x[1]) * math.exp(-((x[0] - math.pi) ** 2) - (x[1] - math.pi) ** 2)
            ),
        )

    def get_function(self, name: SupportedFunctionName) -> FitnessFunctionConfig:
        """Get supported 2D function based on the name.

        Parameters
        ----------
        name : SupportedFunctionName
            The name of function.

        Returns
        -------
        FunctionConfig
            Supported function object.
        """

        return self._get_function_by_name(name)

    def test_function(self, name: SupportedFunctionName) -> None:
        """Compute and print the global function optimum and the real optimum.

        Parameters
        ----------
        name : SupportedFunctionName
            The name of function to test.
        """
        options = self._get_function_by_name(name)
        fitness_function: Callable[[list[float]], float] = options.formula
        calculated_optimum = fitness_function([options.x1_for_optimum, options.x2_for_optimum])
        print(f"[{name.name}] Fitness function returned optimum: '{calculated_optimum:0.4f}'")
        print(f"[{name.name}] Fitness function real optimum: '{options.optimum:0.4f}'")

    def _get_function_by_name(self, name: SupportedFunctionName) -> FitnessFunctionConfig:
        return self._functions[name]


@dataclass
class FunctionConfig:
    fitness_function: Callable[[list[float]], float]
    arg_min: float
    arg_max: float
    x1_for_optimum: float
    x2_for_optimum: float
    optimum: float


@dataclass
class BaseGenetiOperatorConfig:
    probability: float
    points_number: int


@dataclass
class MutationConfig(BaseGenetiOperatorConfig):
    type: Union[BinaryMutationType, RealMutationType]


@dataclass
class CrossoverConfig(BaseGenetiOperatorConfig):
    type: Union[BinaryCrossoverType, RealCrossoverType]


@dataclass
class SelectionConfig:
    selection_type: SelectionType
    duel_groups: int
    duel_group_size: int
    best_percentage: float


@dataclass
class ExtraConfig:
    use_inverse: bool = False
    inverse_probability: float = 0.0
    use_elite: bool = False
    elite_percentage: int = 0


@dataclass
class EvolutionConfig:
    population_size: int
    generations: int
    tollerance: float
    mutation: MutationConfig
    crossover: CrossoverConfig
    selection: SelectionConfig
    extra: ExtraConfig
