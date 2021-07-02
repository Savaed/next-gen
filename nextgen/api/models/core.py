from datetime import datetime
from functools import partial
from typing import Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi_utils.camelcase import snake2camel
from pydantic import BaseConfig, BaseModel

from nextgen.data.dbmodels import BaseMongoDocument


class MongoObjectId(str):
    """Wrapper which allows to serialize and deserialize MongoDB '_id' ObjectId field."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class ApiConfig(BaseConfig):
    """Basic FastApi serialization and deserialization configuration."""

    allow_population_by_field_name = True
    arbitrary_types_allowed = True
    use_enum_values = True
    alias_generator = partial(snake2camel, start_lower=True)
    json_encoders = {datetime: lambda dt: dt.isoformat()}


class ApiBaseModel(BaseModel):
    """Base class for API request and response models."""

    class Config(ApiConfig):
        pass


class MongoBaseModel(BaseModel):
    """Base class for API request and response models which need conversion to and from MongoDB models."""

    id: MongoObjectId
    modified: datetime
    created: Optional[datetime]

    class Config(ApiConfig):
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: lambda oid: str(oid)}

    @classmethod
    def from_mongo(cls, mongo_object: BaseMongoDocument) -> dict[str:Any]:
        """Cast MongoDB model to API model. Properly handles '_id' and ObjectId conversions.

        Parameters
        ----------
        mongo_object : Union
            Mongo object which will be casted to API model.

        Returns
        -------
        dict[str: Any]
            API model object.
        """

        return cls(**mongo_object.to_dict())
