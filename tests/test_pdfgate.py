from datetime import datetime
import random
from typing import Union
import uuid
import pytest
import requests
import responses
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN
from pdfgate_sdk_python.errors import PDFGateError, ParamsValidationError
from pdfgate_sdk_python.params import GeneratePDFParams, GetDocumentParams
from pdfgate_sdk_python.pdfgate import PDFGate, URLBuilder, try_make_request
from requests import exceptions


VALID_API_KEY = f"live_{str(uuid.uuid4())}"
DOCUMENT_ID = str(uuid.uuid4())

class TestURLBuilder:
    @staticmethod
    def random_file_url() -> str:
        return f"{PRODUCTION_API_DOMAIN}/file/open/{str(uuid.uuid4())}"

def test_invalid_api_key_raises() -> None:
    with pytest.raises(PDFGateError, match="Invalid API key format"):
        PDFGate("wrong_prefix_213123")

@responses.activate
def test_try_make_request_raises_when_request_returns_an_http_error() -> None:
    url = "https://example.com"
    message = "Required field 'pdf' is missing"
    responses.add(
        responses.GET,
        url,
        json={
            "statusCode": 400,
            "message": message,
            "error": "Bad Request"
        },
        status=400
    )
    request = requests.Request("GET", url=url).prepare()

    error_message_pattern = rf"HTTP Error.*400.*{message}.*"
    with pytest.raises(PDFGateError, match=error_message_pattern):
        try_make_request(request)


@pytest.mark.parametrize("body, match_pattern", [
    (exceptions.Timeout("Request timed out"), r"Request failed.*Request timed out"),
    (exceptions.ConnectionError("Connection failed"), r"Request failed.*Connection failed"),
])
@responses.activate
def test_try_make_request_raises_when_request_fails(body: Exception, match_pattern: str) -> None:
    url = "https://example.com"
    responses.add(responses.GET, url, body=body)
    request = requests.Request("GET", url=url).prepare()

    with pytest.raises(PDFGateError, match=match_pattern):
        try_make_request(request)

@responses.activate
def test_get_document_returns_document() -> None:
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

def test_generate_pdf_raises_when_neither_html_nor_url_provided() -> None:
    client = PDFGate(api_key=VALID_API_KEY)
    params = GeneratePDFParams()

    with pytest.raises(ParamsValidationError):
        client.generate_pdf(params)