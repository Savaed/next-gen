from typing import Optional, Union

from nextgen.api.models.core import ApiBaseModel
from nextgen.genetic.models import (
    BinaryCrossoverType,
    BinaryMutationType,
    RealCrossoverType,
    RealMutationType,
    SelectionType,
)


class AuthCredentials(ApiBaseModel):
    username: str
    password: str


class AlgorithmConfig(ApiBaseModel):
    mutation_probability: float
    mutation_points_number: Optional[int]
    mutation_type: Union[BinaryMutationType, RealMutationType]
    crossover_probability: float
    crossover_points_number: Optional[int]
    crossover_type: Union[BinaryCrossoverType, RealCrossoverType]
    selection_type: SelectionType
    duel_groups: Optional[int]
    duel_group_size: Optional[int]
    best_percentage: Optional[int]
    use_inverse: bool
    inverse_probability: Optional[float]
    use_elite: bool
    elite_percentage: Optional[int]
    population_size: int
    tollerance: float
