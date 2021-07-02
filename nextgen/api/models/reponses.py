from datetime import datetime
from typing import Generic, Optional, TypeVar

from bson import ObjectId
from pydantic import validator
from pydantic.generics import GenericModel

from nextgen.api.models.core import ApiBaseModel, ApiConfig, MongoBaseModel, MongoObjectId


ResponseT = TypeVar("ResponseT")


class ApiResponse(GenericModel, Generic[ResponseT]):
    data: Optional[ResponseT]
    errors: Optional[list[str]]
    success: bool

    @validator("errors", always=True)
    def check_consistency(cls, value, values):
        if value is not None and values["data"] is not None:
            raise ValueError("Must not provide both data and error")
        if value is None and values.get("data") is None:
            raise ValueError("Must provide data or error")
        return value

    class Config(ApiConfig):
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: lambda oid: str(oid)}


class ResultDetails(MongoBaseModel):
    result_details_id: MongoObjectId
    mutation_probability: float
    mutation_points_number: int
    mutation_type: str
    crossover_probability: float
    crossover_points_number: int
    crossover_type: str
    selection_type: str
    duel_groups: int
    duel_group_size: int
    best_percentage: int
    use_inverse: bool
    inverse_probability: float
    use_elite: bool
    elite_percentage: int
    population_size: int
    tollerance: float


class EvoResult(MongoBaseModel):
    user_id: MongoObjectId
    generations: int
    best_solution: list[list[float]]
    elapsed_seconds: float
    details: ResultDetails


class AccessToken(ApiBaseModel):
    username: str
    token: str
