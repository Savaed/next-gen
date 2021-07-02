from datetime import datetime
from enum import Enum
from typing import Any

from mongoengine import Document
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    EmbeddedDocumentField,
    FloatField,
    IntField,
    ListField,
    ReferenceField,
    StringField,
)
from pydantic.main import BaseModel

from nextgen.data.decorators import custom_collection_name


class BaseMongoDocument(Document):
    created = DateTimeField(default=datetime.utcnow().astimezone())
    modified = DateTimeField(default=datetime.utcnow().astimezone())
    meta = {"abstract": True}

    def to_dict(self) -> dict[str:Any]:
        parsed = self.to_mongo().to_dict()
        if "id" not in parsed:
            parsed["id"] = parsed.pop("_id", None)
        return parsed

    @classmethod
    def from_api_model(cls, api_model: BaseModel):
        return cls(**api_model.dict())


@custom_collection_name
class User(BaseMongoDocument):
    username = StringField()
    hashed_password = StringField()
    roles = ListField()


@custom_collection_name
class EvoResultDetails(BaseMongoDocument):
    mean = ListField()
    std = ListField()
    best_solutions = ListField()


class ResultDetails(EmbeddedDocument):
    result_details_id = ReferenceField(EvoResultDetails)
    mutation_probability = FloatField()
    mutation_points_number = IntField()
    mutation_type = StringField()
    crossover_probability = FloatField()
    crossover_points_number = IntField()
    crossover_type = StringField()
    selection_type = StringField()
    duel_groups = IntField()
    duel_group_size = IntField()
    best_percentage = IntField()
    use_inverse = BooleanField()
    inverse_probability = FloatField()
    use_elite = BooleanField()
    elite_percentage = IntField()
    population_size = IntField()
    tollerance = FloatField()


@custom_collection_name
class EvoResult(BaseMongoDocument):
    user_id = ReferenceField(User)
    generations = IntField()
    best_solution = ListField()
    elapsed_seconds = FloatField()
    details = EmbeddedDocumentField(ResultDetails)