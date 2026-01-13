from datetime import datetime
import random
from typing import Union
import uuid
import pytest
import responses
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN
from pdfgate_sdk_python.errors import PDFGateError
from pdfgate_sdk_python.params import GetDocumentParams
from pdfgate_sdk_python.pdfgate import PDFGate, URLBuilder
from requests import exceptions


VALID_API_KEY = f"live_{str(uuid.uuid4())}"
DOCUMENT_ID = str(uuid.uuid4())

class TestURLBuilder:
    @staticmethod
    def random_file_url() -> str:
        return f"{PRODUCTION_API_DOMAIN}/file/open/{str(uuid.uuid4())}"

def test_invalid_api_key_raises():
    with pytest.raises(PDFGateError, match="Invalid API key format"):
        PDFGate("wrong_prefix_213123")

@responses.activate
def test_get_document_raises_when_request_returns_an_http_error():
    responses.add(
        responses.GET,
        URLBuilder.get_document_url(PRODUCTION_API_DOMAIN, DOCUMENT_ID),
        json={
            "statusCode": 400,
            "message": "preSignedUrlExpiresIn: preSignedUrlExpiresIn must not be greater than 86400",
            "error": "Bad Request"
        },
        status=400
    )
    client = PDFGate(api_key=VALID_API_KEY)
    invalid_pre_signed_url_expires_in = 90000  # Invalid value greater than 86400
    params = GetDocumentParams(
        document_id=DOCUMENT_ID,
        pre_signed_url_expires_in=invalid_pre_signed_url_expires_in
    )

    error_message_pattern = r"HTTP Error.*400.*preSignedUrlExpiresIn must not be greater than.*"
    with pytest.raises(PDFGateError, match=error_message_pattern):
        client.get_document(params)


@pytest.mark.parametrize("body, match_pattern", [
    (exceptions.Timeout("Request timed out"), r"Request failed.*Request timed out"),
    (exceptions.ConnectionError("Connection failed"), r"Request failed.*Connection failed"),
])
@responses.activate
def test_get_document_raises_when_request_fails(body: Exception, match_pattern: str):
    responses.add(
        responses.GET,
        URLBuilder.get_document_url(PRODUCTION_API_DOMAIN, DOCUMENT_ID),
        body=body
    )
    client = PDFGate(api_key=VALID_API_KEY)
    params = GetDocumentParams(document_id=DOCUMENT_ID)
    with pytest.raises(PDFGateError, match=match_pattern):
        client.get_document(params)

@responses.activate
def test_get_document_returns_document():
    mock_response: dict[str, Union[str, int]] = {
        "id": DOCUMENT_ID,
        "status": "completed",
        "fileUrl": TestURLBuilder.random_file_url(),
        "size": random.randint(1000, 1000000),
        "createdAt": datetime.now().isoformat(),
    }
    responses.add(
        responses.GET,
        URLBuilder.get_document_url(PRODUCTION_API_DOMAIN, DOCUMENT_ID),
        json=mock_response,
        status=200
    )
    client = PDFGate(api_key=VALID_API_KEY)
    params = GetDocumentParams(document_id=DOCUMENT_ID)

    document = client.get_document(params)

    assert document.get("id") == mock_response["id"]
    assert document.get("status") == mock_response["status"]
    assert document.get("created_at") == mock_response["createdAt"]
    assert document.get("file_url") == mock_response["fileUrl"]