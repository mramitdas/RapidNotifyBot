import re

from pydantic import BaseModel, EmailStr, conint, constr, validator

from .utils import TimestampMixin


class BaseUser(BaseModel):
    """
    Represents the base user model with common attributes.

    Attributes:

    Config:
        from_attributes (bool): Indicates whether attribute values should be populated from the corresponding class attributes when creating an instance. Defaults to True.
    """

    user_uuid: int | None = None
    user_telegram_id: int | None = None

    class Config:
        """
        Configuration options for Pydantic models.

        Attributes:
            from_attributes (bool): Determines whether attribute values should be populated from class attributes when creating an instance of the model. If True, class attributes with the same name as fields in the model will be used to initialize those fields. Defaults to True, enabling attribute initialization from class attributes.
        """

        from_attributes = True


class UserIn(TimestampMixin, BaseUser):
    """
    Represents a user input model with additional fields and validation.

    Attributes:
        password (str): The password associated with the user. Defaults to randomly generated password.
        is_active (bool): Indicates whether the user account is active. Defaults to True.
        is_staff (bool): Indicates whether the user has staff privileges. Defaults to False.
        is_admin (bool): Indicates whether the user has admin privileges. Defaults to False.
        is_superuser (bool): Indicates whether the user has superuser privileges. Defaults to False.

    Validators:
        check_aadhar_no (classmethod): A validator method that checks the Aadhar number (if provided) for its format. Raises a ValueError if the format is invalid.

    Config:
        from_attributes (bool): Indicates whether attribute values should be populated from the corresponding class attributes when creating an instance. Defaults to True.

    Inherits from:
        - TimestampMixin: A mixin class providing timestamp fields (e.g., created_at, updated_at).
        - BaseUser: The base user model with common attributes.

    Note:
        The `check_aadhar_no` validator is applied to the `aadhar_no` field if a value is provided and ensures it is exactly 12 digits long.

    """

    password: str = None
    is_active: bool = True
    is_staff: bool = False
    is_admin: bool = False
    is_superuser: bool = False

    class Config:
        """
        Configuration options for Pydantic models.

        Attributes:
            from_attributes (bool): Determines whether attribute values should be populated from class attributes when creating an instance of the model. If True, class attributes with the same name as fields in the model will be used to initialize those fields. Defaults to True, enabling attribute initialization from class attributes.
        """

        from_attributes = True


class UserOut(BaseUser):
    """
    Represents a user output model.

    This class inherits attributes and behavior from the `BaseUser` class and is intended to be used for representing user data in output or response objects.

    Attributes:
        - user_uuid (int): The unique identifier for the user.

    Inherits from:
        - BaseUser: The base user model with common attributes.

    Note:
        This class does not introduce additional attributes or behavior beyond what is defined in the `BaseUser` class. It serves as a specialized version of `BaseUser` specifically designed for representing user data in response objects.
    """

    user_uuid: int | None = None

    class Config:
        """
        Configuration options for Pydantic models.

        Attributes:
            from_attributes (bool): Determines whether attribute values should be populated from class attributes when creating an instance of the model. If True, class attributes with the same name as fields in the model will be used to initialize those fields. Defaults to True, enabling attribute initialization from class attributes.
        """

        from_attributes = True


class UserSearch(BaseUser):
    """
    Represents a user search model with optional filter criteria.

    This class inherits attributes and behavior from the `BaseUser` class but sets several fields to None, allowing them to be used as optional filter criteria when searching for users.

    Attributes:
        - user_uuid (int): The unique identifier for the user.

    Inherits from:
        - BaseUser: The base user model with common attributes.

    Note:
        - Fields that are set to None, such as `user_uuid`, `full_name`, `user_role`, and `phone_no`, can be used as optional filter criteria when performing user searches.
        - When creating instances of this class, you can specify values for specific fields to filter user search results based on the provided criteria.
    """

    user_uuid: int | None = None

    class Config:
        """
        Configuration options for Pydantic models.

        Attributes:
            from_attributes (bool): Determines whether attribute values should be populated from class attributes when creating an instance of the model. If True, class attributes with the same name as fields in the model will be used to initialize those fields. Defaults to True, enabling attribute initialization from class attributes.
        """

        from_attributes = True


class UserUpdate(BaseModel):
    """
    Represents a user update model for modifying user data.

    Attributes:
        user_uuid (int): The unique identifier for the user whose subscription is being updated.
        user_data (BaseUser): An instance of the BaseUser class containing updated user data.

    Note:
        - Use this class to define the criteria for selecting a user to update and provide the new user data to be applied.

    Configuration Options:
        - Config.from_attributes (bool): Determines whether attribute values should be populated from class attributes when creating an instance of the model. If True, class attributes with the same name as fields in the model will be used to initialize those fields. Defaults to True, enabling attribute initialization from class attributes.
    """

    user_uuid: int
    user_data: BaseUser

    class Config:
        """
        Configuration options for Pydantic models.

        Attributes:
            from_attributes (bool): Determines whether attribute values should be populated from class attributes when creating an instance of the model. If True, class attributes with the same name as fields in the model will be used to initialize those fields. Defaults to True, enabling attribute initialization from class attributes.
        """

        from_attributes = True