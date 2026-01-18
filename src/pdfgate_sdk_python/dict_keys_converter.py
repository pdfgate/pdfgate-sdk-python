import re
from typing import Any, Union


def camel_to_snake(name: str) -> str:
    """Convert a string from camelCase to snake_case."""
    # Inserts an underscore before any uppercase letter that is followed by a
    # lowercase letter or digit.
    # This is needed for cases like: TestHTTPResponse -> TestHTTP_Response
    s1 = re.sub("(.)([A-Z][a-z0-9]+)", r"\1_\2", name)
    # Inserts an underscore before any uppercase letter that is preceded by a lowercase letter or digit
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def convert_camel_keys_to_snake(
    data: Union[dict[Any, Any], list[Any], Any],
) -> Union[dict[Any, Any], list[Any], Any]:
    """Recursively converts all keys in a dictionary or list to snake_case."""
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():  # type: ignore
            new_key = camel_to_snake(key)  # type: ignore
            new_dict[new_key] = convert_camel_keys_to_snake(value)  # type: ignore
        return new_dict  # type: ignore
    elif isinstance(data, list):
        return [convert_camel_keys_to_snake(item) for item in data]  # type: ignore
    else:
        return data


def snake_to_camel(key: str) -> str:
    """Convert a snake_case string to camelCase."""
    parts = key.split("_")

    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def convert_snake_keys_to_camel(
    data: Union[dict[Any, Any], list[Any], Any],
) -> Union[dict[Any, Any], list[Any], Any]:
    """Recursively converts all keys in a dictionary or list to camelCase."""
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():  # type: ignore
            new_key = snake_to_camel(key)  # type: ignore
            new_dict[new_key] = convert_snake_keys_to_camel(value)  # type: ignore
        return new_dict  # type: ignore
    elif isinstance(data, list):
        return [convert_snake_keys_to_camel(item) for item in data]  # type: ignore
    else:
        return data
