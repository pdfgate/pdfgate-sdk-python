from datetime import datetime
import random
from typing import TypedDict
import uuid
import pytest
import requests
import responses
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN
from pdfgate_sdk_python.errors import PDFGateError, ParamsValidationError
from pdfgate_sdk_python.params import GeneratePDFParams, GetDocumentParams
from pdfgate_sdk_python.pdfgate import PDFGate, URLBuilder, try_make_request
from requests import exceptions

from pdfgate_sdk_python.responses import DocumentStatus


RANDOM_PRODUCTION_API_KEY = f"live_{str(uuid.uuid4())}"
DOCUMENT_ID = str(uuid.uuid4())

class TestURLBuilder:
    @staticmethod
    def random_file_url() -> str:
        return f"{PRODUCTION_API_DOMAIN}/file/open/{str(uuid.uuid4())}"


class DocumentResponse(TypedDict):
    id: str
    status: str
    createdAt: str
    fileUrl: str
    size: int


@pytest.fixture
def document_response() -> DocumentResponse:
    return {
        "id": str(uuid.uuid4()),
        "status": random.choice([status.value for status in DocumentStatus]),
        "fileUrl": TestURLBuilder.random_file_url(),
        "size": random.randint(1000, 1000000),
        "createdAt": datetime.now().isoformat(),
    }

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
def test_get_document_returns_document(document_response: DocumentResponse) -> None:
    responses.add(
        responses.GET,
        URLBuilder.get_document_url(PRODUCTION_API_DOMAIN, document_response["id"]),
        json=document_response,
        status=200
    )
    client = PDFGate(api_key=RANDOM_PRODUCTION_API_KEY)
    params = GetDocumentParams(document_id=document_response["id"])

    document = client.get_document(params)

    assert document.get("id") == document_response["id"]
    assert document.get("status") == document_response["status"]
    assert document.get("created_at") == document_response["createdAt"]
    assert document.get("file_url") == document_response["fileUrl"]

def test_generate_pdf_raises_when_neither_html_nor_url_provided() -> None:
    client = PDFGate(api_key=RANDOM_PRODUCTION_API_KEY)
    params = GeneratePDFParams()

    with pytest.raises(ParamsValidationError):
        client.generate_pdf(params)

def test_generate_pdf_raises_when_both_html_and_url_provided() -> None:
    client = PDFGate(api_key=RANDOM_PRODUCTION_API_KEY)
    params = GeneratePDFParams(
        html="<h1>Test</h1>",
        url="https://example.com"
    )

    with pytest.raises(ParamsValidationError):
        client.generate_pdf(params)

@responses.activate
def test_generate_pdf_returns_json_when_json_reponse_true(document_response: DocumentResponse) -> None:
    responses.add(
        responses.POST,
        URLBuilder.generate_pdf_url(PRODUCTION_API_DOMAIN),
        json=document_response,
        status=201
    )
    client = PDFGate(api_key=RANDOM_PRODUCTION_API_KEY)
    params = GeneratePDFParams(
        html="<h1>Test</h1>",
        json_response=True
    )

    response = client.generate_pdf(params)
    assert isinstance(response, dict)
    assert response.get("id") == document_response["id"]
    assert response.get("status") == document_response["status"]
    assert response.get("created_at") == document_response["createdAt"]

@responses.activate
def test_generate_pdf_returns_bytes_when_json_reponse_false() -> None:
    responses.add(
        responses.POST,
        URLBuilder.generate_pdf_url(PRODUCTION_API_DOMAIN),
        body=b"%PDF-1.4\n%\xd3\xeb\xe9\xe1\n1 0 obj\n<</Title (PDF - Wikipedia)\n/Creator (Mozilla/5.0 \\(X11; Linux x86_64\\) AppleW",
        content_type="application/octet-stream",
        status=201
    )
    client = PDFGate(api_key=RANDOM_PRODUCTION_API_KEY)
    params = GeneratePDFParams(
        html="<h1>Test</h1>",
        json_response=False
    )

    response = client.generate_pdf(params)
    assert isinstance(response, bytes)