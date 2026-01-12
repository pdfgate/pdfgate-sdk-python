from typing import Union
import pytest
from pdfgate_sdk_python.responses import PDFGateDocumentResponseValidator

def test_document_response_validator_raises_when_required_field_is_not_present():
    invalid_data = {
        "id": "doc_123",
        # "status" field is missing
        "created_at": "2024-01-01T00:00:00",
        "expires_at": "2024-01-02T00:00:00"
    }

    with pytest.raises(ValueError, match="Missing required field: status"):
        PDFGateDocumentResponseValidator.validate(invalid_data)

def test_document_response_validator_raises_when_field_is_not_of_the_expected_type():
    invalid_data: dict[str, Union[str, int]] = {
        "id": 123,  # should be str
        "status": "completed",
        "created_at": "2024-01-01T00:00:00",
        "expires_at": "2024-01-02T00:00:00"
    }

    with pytest.raises(ValueError, match="Field id must be of type str"):
        PDFGateDocumentResponseValidator.validate(invalid_data)

def test_document_response_validator_raises_when_optional_field_is_not_of_the_expected_type():
    invalid_data: dict[str, Union[str, int]] = {
        "id": "doc_123",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00",
        "expires_at": "2024-01-02T00:00:00",
        "size": "not_an_int"  # should be int
    }

    with pytest.raises(ValueError, match="Field size must be of type int"):
        PDFGateDocumentResponseValidator.validate(invalid_data)