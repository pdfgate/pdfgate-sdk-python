from typing import Any
from pdfgate.dict_keys_converter import (
    camel_to_snake,
    convert_camel_keys_to_snake,
    convert_snake_keys_to_camel,
    snake_to_camel,
)


def test_camel_to_snake() -> None:
    assert camel_to_snake("simpleTest") == "simple_test"
    assert camel_to_snake("TestHTTPResponse") == "test_http_response"
    assert camel_to_snake("already_snake_case") == "already_snake_case"
    assert camel_to_snake("mixedExampleTestCase") == "mixed_example_test_case"


def test_snake_to_camel() -> None:
    assert snake_to_camel("simple_test") == "simpleTest"
    assert snake_to_camel("alreadyCamelCase") == "alreadyCamelCase"
    assert snake_to_camel("mixed_example_case") == "mixedExampleCase"


def test_convert_camel_keys_to_snake() -> None:
    data: dict[Any, Any] = {
        "firstKey": "value1",
        "secondKey": {
            "nestedKeyOne": 1,
            "nestedKeyTwo": [{"listItemKey": "item1"}, {"listItemKey": "item2"}],
        },
        "thirdKeyList": [1, 2, 3],
    }
    converted = convert_camel_keys_to_snake(data)
    expected: dict[Any, Any] = {
        "first_key": "value1",
        "second_key": {
            "nested_key_one": 1,
            "nested_key_two": [{"list_item_key": "item1"}, {"list_item_key": "item2"}],
        },
        "third_key_list": [1, 2, 3],
    }
    assert converted == expected


def test_convert_snake_keys_to_camel() -> None:
    data: dict[Any, Any] = {
        "first_key": "value1",
        "second_key": {
            "nested_key_one": 1,
            "nested_key_two": [{"list_item_key": "item1"}, {"list_item_key": "item2"}],
        },
        "third_key_list": [1, 2, 3],
    }
    converted = convert_snake_keys_to_camel(data)
    expected: dict[Any, Any] = {
        "firstKey": "value1",
        "secondKey": {
            "nestedKeyOne": 1,
            "nestedKeyTwo": [{"listItemKey": "item1"}, {"listItemKey": "item2"}],
        },
        "thirdKeyList": [1, 2, 3],
    }
    assert converted == expected
