"""
Module: validator

This module defines Pydantic models for input data related to MongoDB operations.

Classes:
    - MongoDbClientConfig: Pydantic model for MongoDB client configuration.

    - BaseInput: Base Pydantic model for common input attributes for MongoDB operations.

    - UploadDataInput: Pydantic model for input data to upload (insert) into MongoDB.

    - QueryDataInput: Pydantic model for input data to query (read) from MongoDB, inheriting from UploadDataInput.

    - UpdateDataInput: Pydantic model for input data to update existing records in MongoDB.

    - DeleteDataInput: Pydantic model for input data to delete records from MongoDB, inheriting from QueryDataInput.

Usage:
    1. Import the required classes from this module.
    2. Use these classes as Pydantic models to validate and handle input data in MongoDB-related operations.

Example:
    ```python
    from module.validator import MongoDbClientConfig, UploadDataInput, QueryDataInput

    # Example usage of the Pydantic models
    client_config = MongoDbClientConfig(db_url="mongodb://localhost:27017")
    upload_data_input = UploadDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
    query_data_input = QueryDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
    ```

Note:
    The provided Pydantic models help ensure the correctness of input data for MongoDB operations and can be used
    as type hints for better code clarity.

"""

from typing import Dict

from pydantic import BaseModel, validator


class MongoDbClientConfig(BaseModel):
    """
    Pydantic model for MongoDB client configuration.

    Attributes:
        db_url (str): The MongoDB database URL.

    Usage:
        ```python
        client_config = MongoDbClientConfig(db_url="mongodb://localhost:27017")
        ```

    """

    db_url: str


class BaseInput(BaseModel):
    """
    Base Pydantic model for common input attributes for MongoDB operations.

    Attributes:
        db_name (str): The name of the MongoDB database.
        table_name (str): The name of the MongoDB table (collection).

    Usage:
        ```python
        base_input = BaseInput(db_name="example_db", table_name="example_table")
        ```

    """

    db_name: str
    table_name: str


class UploadDataInput(BaseInput):
    """
    Pydantic model for input data to upload (insert) into MongoDB.

    Attributes:
        data (Dict): The data to be uploaded.

    Usage:
        ```python
        upload_data_input = UploadDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
        ```

    """

    data: Dict

    @validator("data", pre=True, always=True)
    def validate_data(cls, value):
        """
        Validator to ensure that the data attribute is not blank.

        Args:
            value (Dict): The data to be validated.

        Returns:
            Dict: The validated data.

        Raises:
            ValueError: If the data is blank.

        """
        if not value:
            raise ValueError("Data cannot be blank")
        return value


class QueryDataInput(UploadDataInput):
    """
    Pydantic model for input data to query (read) from MongoDB, inheriting from UploadDataInput.

    Inherits:
        UploadDataInput

    Usage:
        ```python
        query_data_input = QueryDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
        ```

    """


class UpdateDataInput(BaseInput):
    """
    Pydantic model for input data to update existing records in MongoDB.

    Attributes:
        data (Dict): The data to be updated.

    Usage:
        ```python
        update_data_input = UpdateDataInput(db_name="example_db", table_name="example_table", data={"key": "new_value"})
        ```

    """

    data: Dict


class DeleteDataInput(QueryDataInput):
    """
    Pydantic model for input data to delete records from MongoDB, inheriting from QueryDataInput.

    Inherits:
        QueryDataInput

    Usage:
        ```python
        delete_data_input = DeleteDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
        ```

    """
