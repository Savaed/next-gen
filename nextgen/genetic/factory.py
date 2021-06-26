from typing import Union

from nextgen.genetic import models
from nextgen.genetic.operators import BinaryGeneticOperators, RealGeneticOperators


class GeneticOperatorsFactory(object):
    """Factory class that provides method for get operators based on the chromosome representation."""

    def __init__(
        self,
        mutation_type: Union[models.BinaryMutationType, models.RealMutationType],
        crossover_type: Union[models.BinaryCrossoverType, models.RealCrossoverType],
        **kwargs,
    ) -> None:
        self._mutation_type = mutation_type
        self._crossover_type = crossover_type

        self._crossover_points_number = kwargs["crossover_points"] if "crossover_points" in kwargs else 1
        self._mutation_points_number = kwargs["mutation_points"] if "mutation_points" in kwargs else 1

        self._arg_min = kwargs["arg_min"]
        self._arg_max = kwargs["arg_max"]

    def get_operators(
        self, representation: models.ChromosomeRepresentation
    ) -> Union[BinaryGeneticOperators, RealGeneticOperators]:
        """Get rigth operator for passed chromosome representation.

        Parameters
        ----------
        representation : models.ChromosomeRepresentation
            The chromosome representation. It may be 'binary' or 'real'.

        Returns
        -------
        Union[BinaryGeneticOperators, RealGeneticOperators]
            The genetic operator, either BinaryGeneticOperators for 'binary' chromosome and RealGeneticOperators for 'real'.

        Raises
        ------
        ValueError
            The passed chromosome representation not supported.
        """
        if representation == models.ChromosomeRepresentation.BINARY:
            return BinaryGeneticOperators(
                self._mutation_type,
                self._crossover_type,
                crossover_points=self._crossover_points_number,
                mutation_points=self._mutation_points_number,
            )
        if representation == models.ChromosomeRepresentation.REAL:
            return RealGeneticOperators(self._mutation_type, self._crossover_type, self._arg_min, self._arg_max)

        raise ValueError(f"Chromosome representation '{representation}' not supported.")
