"""
Module: mongo

This module defines a utility class for interacting with MongoDB databases.

Classes:
    - DataBase: A utility class for interacting with MongoDB databases.

Usage:
    1. Import the DataBase class from this module.
    2. Create an instance of the DataBase class by providing the necessary configuration.
    3. Use the methods of the DataBase class to perform various database operations.

Example:
    ```python
    from module.mongo import DataBase
    from module.models import MongoDbClientConfig, UploadDataInput, QueryDataInput, UpdateDataInput, DeleteDataInput

    # Example usage of the DataBase class
    db_config = MongoDbClientConfig(db_url="mongodb://localhost:27017")
    database = DataBase(config=db_config)

    # Example usage of database operations
    upload_data_input = UploadDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
    database.upload(input_data=upload_data_input)

    query_data_input = QueryDataInput(db_name="example_db", table_name="example_table", data={"key": "value"})
    result = database.query(input_data=query_data_input)
    ```

Classes and Methods:
    - DataBase:
        - __init__(config: MongoDbClientConfig): Initializes the MongoDB client instance.
        - connect() -> pymongo.MongoClient: Establishes a connection to the MongoDB instance.
        - validate(): Validates input data and raises errors for missing or invalid attributes.
        - upload(input_data: UploadDataInput) -> pymongo.InsertOneResult or pymongo.InsertManyResult:
            Inserts data into a specified database and collection.
        - query(input_data: QueryDataInput) -> pymongo.cursor.Cursor or dict: Retrieves data based on provided filters.
        - update(input_data: UpdateDataInput) -> pymongo.UpdateResult: Updates data based on provided filters.
        - delete(input_data: DeleteDataInput) -> pymongo.DeleteResult: Deletes data based on provided filters.

Notes:
    - This class is designed for MongoDB database interactions.
    - You can connect to a MongoDB instance by providing the `db_url` parameter during initialization.
    - The provided methods handle data validation and various database operations.
"""

import pymongo
from pydantic import ValidationError
from pymongo.results import (
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult,
)

from .validator import (
    DeleteDataInput,
    MongoDbClientConfig,
    QueryDataInput,
    UpdateDataInput,
    UploadDataInput,
)


class DataBase:
    """
    A utility class for interacting with MongoDB databases.

    This class provides methods for connecting to a MongoDB instance, validating input data, and performing various database operations such as uploading, querying, updating, and deleting data.

    Args:
        config (MongoDbClientConfig): The configuration for the MongoDB client.

    Attributes:
        database_url (str): The URL of the connected MongoDB instance.
        mongod (pymongo.MongoClient): The MongoDB client instance established using the provided URL.

    Methods:
        - connect() -> pymongo.MongoClient: Establishes a connection to the MongoDB instance.
        - validate(): Validates input data and raises errors for missing or invalid attributes.
        - upload(input_data: UploadDataInput) -> pymongo.InsertOneResult or pymongo.InsertManyResult: Inserts data into a specified database and collection.
        - query(input_data: QueryDataInput) -> pymongo.cursor.Cursor or dict: Retrieves data based on provided filters.
        - update(input_data: UpdateDataInput) -> pymongo.UpdateResult: Updates data based on provided filters.
        - delete(input_data: DeleteDataInput) -> pymongo.DeleteResult: Deletes data based on provided filters.

    Notes:
        - This class is designed for MongoDB database interactions.
        - You can connect to a MongoDB instance by providing the `db_url` parameter during initialization.
        - The provided methods handle data validation and various database operations.
    """

    def __init__(self, config: MongoDbClientConfig) -> None:
        """Initialize the MongoDB client instance.

        Args:
            config (MongoDbClientConfig): The configuration for the MongoDB client.

        Raises:
            ValueError: If `config` is not valid.
        """
        try:
            validated_config = MongoDbClientConfig(**config.model_dump())
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e.errors()}") from e

        self.database_url = validated_config.db_url
        self.mongod = self.connect()

    def connect(self) -> pymongo.MongoClient:
        """Establish a connection to the MongoDB instance.

        Returns:
            pymongo.MongoClient: The MongoDB client instance.
        """
        return pymongo.MongoClient(self.database_url)

    def upload(
        self, input_data: UploadDataInput
    ) -> InsertOneResult or InsertManyResult:
        """Insert data into a specified database and collection.

        Args:
            input_data (UploadDataInput): The input data including the database name,
                collection name, and the data to be inserted.

        Returns:
            InsertOneResult or InsertManyResult: The response object indicating the result of the insertion.

        Raises:
            ValueError: If the input data is invalid.
        """
        try:
            validated_input = UploadDataInput(**input_data.model_dump())
        except ValidationError as e:
            error_message = f"Invalid input data: {e.errors()}"
            raise ValueError(error_message) from e

        database = self.mongod[validated_input.db_name]
        dataset = database[validated_input.table_name]

        return dataset.insert_one(validated_input.data)

    def query(self, input_data: QueryDataInput) -> list:
        """Retrieve data from a specified database and collection based on filters.

        Args:
            input_data (QueryDataInput): The input data including the database name,
                collection name, filter

        Returns:
            dict: The retrieved data.

        Raises:
            ValueError: If the input data is invalid.
        """
        try:
            validated_input = QueryDataInput(**input_data.model_dump())
        except ValidationError as e:
            error_message = f"Invalid input data: {e.errors()}"
            raise ValueError(error_message) from e

        database = self.mongod[validated_input.db_name]
        dataset = database[validated_input.table_name]
        return list(dataset.find(validated_input.data))

    def update(self, input_data: UpdateDataInput) -> UpdateResult:
        """Update data in a specified database and collection based on filters.

        Args:
            input_data (UpdateDataInput): The input data including the database name,
                collection name, and the data to be updated.

        Returns:
            UpdateResult: The response object indicating the result of the update operation.

        Raises:
            ValueError: If the input data is invalid.
        """
        try:
            validated_input = UpdateDataInput(**input_data.model_dump())
        except ValidationError as e:
            error_message = f"Invalid input data: {e.errors()}"
            raise ValueError(error_message) from e

        database = self.mongod[validated_input.db_name]
        dataset = database[validated_input.table_name]

        return dataset.update_one(
            {"user_uuid": validated_input.data["user_uuid"]},
            {"$set": validated_input.data["user_data"]},
        )

    def delete(self, input_data: DeleteDataInput) -> DeleteResult:
        """
        Delete data from a specified database collection based on a filter.

        Args:
            input_data (DeleteDataInput): The input data including the database name,
                collection name, and the filter to be applied for deletion.

        Returns:
            DeleteResult: The response object indicating the result of the delete operation.
        Raises:
            ValueError: If any input is invalid.
        """
        try:
            validated_input = DeleteDataInput(**input_data.model_dump())
        except ValidationError as e:
            error_message = f"Invalid input data: {e.errors()}"
            raise ValueError(error_message) from e

        database = self.mongod[validated_input.db_name]
        dataset = database[validated_input.table_name]
        return dataset.delete_one(validated_input.data)
