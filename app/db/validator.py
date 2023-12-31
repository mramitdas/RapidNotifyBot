from typing import Dict, List, Union

from pydantic import BaseModel, ValidationError, validator

from app.exceptions.custom_exceptions import MissingAttributeError


class MongoDbClientConfig(BaseModel):
    db_url: str


class BaseInput(BaseModel):
    db_name: str
    table_name: str


class UploadDataInput(BaseInput):
    data: Dict

    @validator("data", pre=True, always=True)
    def validate_data(cls, value):
        if not value:
            raise ValueError("Data cannot be blank")
        return value


class QueryDataInput(UploadDataInput):
    pass


class UpdateDataInput(BaseInput):
    data: Dict


class DeleteDataInput(QueryDataInput):
    pass
