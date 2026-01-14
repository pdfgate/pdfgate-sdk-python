
from pdfgate_sdk_python.params import snake_to_camel


def test_snake_to_camel():
    assert snake_to_camel("simple_test") == "simpleTest"
    assert snake_to_camel("alreadyCamelCase") == "alreadyCamelCase"
    assert snake_to_camel("mixed_example_case") == "mixedExampleCase"