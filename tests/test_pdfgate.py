from datetime import datetime
import random
from typing import TypedDict
import uuid
import httpx
import pytest
import requests
import responses
import respx
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN
from pdfgate_sdk_python.errors import PDFGateError, ParamsValidationError
from pdfgate_sdk_python.params import FlattenPDFBinaryParams, FlattenPDFDocumentParams, GeneratePDFParams, GetDocumentParams, PDFFileParam
from pdfgate_sdk_python.pdfgate import PDFGate, URLBuilder, try_make_request
from requests import exceptions

from pdfgate_sdk_python.responses import DocumentStatus


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

class FlattenedDocumentResponse(DocumentResponse):
    derivedFrom: str

@pytest.fixture
def api_key() -> str:
    return f"live_{str(uuid.uuid4())}"

@pytest.fixture(scope="module")
def url_builder() -> URLBuilder:
    return URLBuilder(PRODUCTION_API_DOMAIN)

@pytest.fixture
def document_id() -> str:
    return str(uuid.uuid4())

@pytest.fixture
def client(api_key: str) -> PDFGate:
    return PDFGate(api_key=api_key)

@pytest.fixture
def document_response() -> DocumentResponse:
    return {
        "id": str(uuid.uuid4()),
        "status": random.choice([status.value for status in DocumentStatus]),
        "fileUrl": TestURLBuilder.random_file_url(),
        "size": random.randint(1000, 1000000),
        "createdAt": datetime.now().isoformat(),
    }

@pytest.fixture
def flattened_document_response(document_id: str) -> FlattenedDocumentResponse:
    return {
        "id": str(uuid.uuid4()),
        "status": random.choice([status.value for status in DocumentStatus]),
        "fileUrl": TestURLBuilder.random_file_url(),
        "size": random.randint(1000, 1000000),
        "createdAt": datetime.now().isoformat(),
        "derivedFrom": document_id,
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

def test_get_document_returns_document(client: PDFGate, url_builder: URLBuilder, document_response: DocumentResponse, respx_mock: respx.MockRouter) -> None:
    url = url_builder.get_document_url(document_response["id"])
    response_json = dict(document_response)
    route = respx_mock.get(url)
    route.mock(return_value=httpx.Response(200, json=response_json))
    params = GetDocumentParams(document_id=document_response["id"])

    document = client.get_document(params)

    assert document.get("id") == document_response["id"]
    assert document.get("status") == document_response["status"]
    assert document.get("created_at") == document_response["createdAt"]
    assert document.get("file_url") == document_response["fileUrl"]

def test_generate_pdf_raises_when_neither_html_nor_url_provided(client: PDFGate) -> None:
    params = GeneratePDFParams()

    with pytest.raises(ParamsValidationError):
        client.generate_pdf(params)

def test_generate_pdf_returns_json_when_json_reponse_true(document_response: DocumentResponse, client: PDFGate, url_builder: URLBuilder, respx_mock: respx.MockRouter) -> None:
    url = url_builder.generate_pdf_url()
    route = respx_mock.post(url)
    route.mock(return_value=httpx.Response(201, json=document_response))
    params = GeneratePDFParams(
        html="<h1>Test</h1>",
        json_response=True
    )

    response = client.generate_pdf(params)

    assert isinstance(response, dict)
    assert response.get("id") == document_response["id"]
    assert response.get("status") == document_response["status"]
    assert response.get("created_at") == document_response["createdAt"]

def test_generate_pdf_returns_bytes_when_json_reponse_false(client: PDFGate, url_builder: URLBuilder, respx_mock: respx.MockRouter) -> None:
    url = url_builder.generate_pdf_url()
    route = respx_mock.post(url)
    route.mock(return_value=httpx.Response(201, content=b"%PDF-1.4\n%\xd3\xeb\xe9\xe1\n1 0 obj\n<</Title (PDF - Wikipedia)\n/Creator (Mozilla/5.0 \\(X11; Linux x86_64\\) AppleW", headers={"Content-Type": "application/octet-stream"}))
    params = GeneratePDFParams(
        html="<h1>Test</h1>",
        json_response=False
    )
    params = GeneratePDFParams(
        html="<h1>Test</h1>",
        json_response=False
    )

    response = client.generate_pdf(params)

    assert isinstance(response, bytes)
    assert response.startswith(b"%PDF-1.4")

@responses.activate
def test_flatten_pdf_by_document_id_returns_json_when_json_reponse_true(client: PDFGate, flattened_document_response: FlattenedDocumentResponse, document_id: str) -> None:
    responses.add(
        responses.POST,
        URLBuilder.flatten_pdf_url(PRODUCTION_API_DOMAIN),
        json=flattened_document_response,
        status=201
    )
    params = FlattenPDFDocumentParams(document_id=document_id, json_response=True)

    response = client.flatten_pdf(params)
    assert isinstance(response, dict)
    assert response.get("id") == flattened_document_response["id"]
    assert response.get("status") == flattened_document_response["status"]
    assert response.get("created_at") == flattened_document_response["createdAt"]
    assert response.get("derived_from") == document_id

@responses.activate
def test_flatten_pdf_by_file_returns_bytes_when_json_reponse_false(client: PDFGate) -> None:
    responses.add(
        responses.POST,
        URLBuilder.flatten_pdf_url(PRODUCTION_API_DOMAIN),
        body=b"%PDF-1.4\n%\xd3\xeb\xe9\xe1\n1 0 obj\n<</Title (PDF - Wikipedia)\n/Creator (Mozilla/5.0 \\(X11; Linux x86_64\\) AppleW",
        content_type="application/octet-stream",
        status=201
    )
    params = FlattenPDFBinaryParams(
        file=PDFFileParam(
            name="input.pdf",
            data=b"%PDF-1.4\n%\xd3\xeb\xe9\xe1\n1 0 obj\n<</Title (PDF - Wikipedia)\n/Creator (Mozilla/5.0 \\(X11; Linux x86_64\\) AppleW"
        ),
        json_response=False
    )

    response = client.flatten_pdf(params)
    assert isinstance(response, bytes)