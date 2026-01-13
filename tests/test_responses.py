
from pdfgate_sdk_python.responses import camel_to_snake


def test_camel_to_snake():
    assert camel_to_snake("simpleTest") == "simple_test"
    assert camel_to_snake("TestHTTPResponse") == "test_http_response"
    assert camel_to_snake("already_snake_case") == "already_snake_case"
    assert camel_to_snake("mixedExampleTestCase") == "mixed_example_test_case"