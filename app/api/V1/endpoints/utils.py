"""
dict_utils module

This module provides utility functions for working with dictionaries in Python.

Functions:
- join_dict_values(dictionary, separator='\n'): Iterate through dictionary keys and join their values using a separator.

Note:
    The join_dict_values function expects the input to be a dictionary, and it will raise a ValueError if the input is not of the correct type.
"""


def join_dict_values(dictionary, separator="\n"):
    """
    Iterate through dictionary keys and join their values using a separator.

    Parameters:
    - dictionary (dict): The input dictionary.
    - separator (str): The separator used to join values. Default is a single space.

    Returns:
    - str: The joined values.
    """
    # Check if the input is a dictionary
    if not isinstance(dictionary, dict):
        raise ValueError("Input must be a dictionary")

    # Join values using the specified separator
    joined_values = separator.join(str(value) for value in dictionary.values())

    return joined_values
