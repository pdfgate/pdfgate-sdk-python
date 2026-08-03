from datetime import datetime
import hashlib
import hmac
import json
import random
from typing import TypedDict, Union
import uuid
import httpx
import pytest
import respx
from pdfgate.config import Config
from pdfgate.errors import (
    PDFGateError,
    ParamsValidationError,
    WebhookSignatureVerificationError,
)
from pdfgate.http_client import PDFGateHTTPClientSync
from pdfgate import verify_signature
from pdfgate.params import (
    AddFormFieldsParams,
    CreateEnvelopeParams,
    CreateWebhookParams,
    DeleteDocumentParams,
    DeleteWebhookParams,
    EnvelopeDocument,
    EnvelopeRecipient,
    FieldOverride,
    FileParam,
    FlattenPDFParams,
    GeneratePDFParams,
    GetDocumentParams,
    GetEnvelopeParams,
    GetWebhookParams,
    ManualFormField,
    SendEnvelopeParams,
    UploadFileParams,
    WatermarkPDFParams,
    WatermarkType,
)
from pdfgate.pdfgate import PDFGate

from pdfgate.request_builder import PDFGateRequest
from pdfgate.responses import DocumentFieldType, DocumentStatus, WebhookEventType
from pdfgate.url_builder import URLBuilder


class TestURLBuilder:
    @staticmethod
    def random_file_url() -> str:
        return f"{Config.PRODUCTION_API_DOMAIN}/file/open/{str(uuid.uuid4())}"


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
    return URLBuilder(Config.PRODUCTION_API_DOMAIN)


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


def test_try_make_request_raises_when_request_returns_an_http_error(
    respx_mock: respx.MockRouter,
    api_key: str,
) -> None:
    url = "https://example.com"
    message = "Required field 'pdf' is missing"
    route = respx_mock.get(url)
    route.mock(
        return_value=httpx.Response(
            400, json={"statusCode": 400, "message": message, "error": "Bad Request"}
        )
    )
    httpx_request = httpx.Request("GET", url=url)
    request = PDFGateRequest(request=httpx_request)

    error_message_pattern = rf"HTTP Error.*400.*{message}.*"
    http_client = PDFGateHTTPClientSync(api_key=api_key)
    with pytest.raises(PDFGateError, match=error_message_pattern):
        http_client.try_make_request(request)


@pytest.mark.parametrize(
    "body, match_pattern",
    [
        (
            httpx.ConnectTimeout("Request timed out"),
            r"Request failed.*Request timed out",
        ),
        (
            httpx.ConnectError("Connection failed"),
            r"Request failed.*Connection failed",
        ),
    ],
)
def test_try_make_request_raises_when_request_fails(
    respx_mock: respx.MockRouter,
    api_key: str,
    body: Union[httpx.ConnectTimeout, httpx.ConnectError],
    match_pattern: str,
) -> None:
    url = "https://example.com"
    route = respx_mock.get(url)
    route.mock(side_effect=body)
    httpx_request = httpx.Request("GET", url=url)
    request = PDFGateRequest(request=httpx_request)

    http_client = PDFGateHTTPClientSync(api_key=api_key)
    with pytest.raises(PDFGateError, match=match_pattern):
        http_client.try_make_request(request)


def test_get_document_returns_document(
    client: PDFGate,
    url_builder: URLBuilder,
    document_response: DocumentResponse,
    respx_mock: respx.MockRouter,
) -> None:
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


def test_generate_pdf_raises_when_neither_html_nor_url_provided(
    client: PDFGate,
) -> None:
    params = GeneratePDFParams()

    with pytest.raises(ParamsValidationError):
        client.generate_pdf(params)


def build_signature_header(secret: str, timestamp: int, payload: bytes) -> str:
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


def test_verify_signature_accepts_valid_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "whsecret_test"
    payload = (
        b'{"eventId":"evt_123","event":"document.completed",'
        b'"timestamp":"2026-05-12T10:00:00Z",'
        b'"resource":{"kind":"document","id":"doc_123"},'
        b'"data":{"documentId":"doc_123"}}'
    )
    timestamp = 1_712_345_678
    signature_header = build_signature_header(secret, timestamp, payload)
    monkeypatch.setattr("pdfgate.webhooks.time.time", lambda: timestamp)

    event = verify_signature(
        secret=secret,
        signature_header=signature_header,
        payload=payload,
    )

    assert event.get("event_id") == "evt_123"
    assert event.get("event") == "document.completed"
    assert event.get("timestamp") == "2026-05-12T10:00:00Z"
    assert event.get("resource") == {"kind": "document", "id": "doc_123"}
    assert event.get("data") == {"document_id": "doc_123"}


def test_verify_signature_accepts_any_matching_v1_signature(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "whsecret_test"
    payload = b'{"type":"document.completed"}'
    timestamp = 1_712_345_678
    valid_header = build_signature_header(secret, timestamp, payload)
    signature_header = (
        f"t={timestamp},v1=invalidsignature,{valid_header.split(',', 1)[1]}"
    )
    monkeypatch.setattr("pdfgate.webhooks.time.time", lambda: timestamp)

    event = verify_signature(
        secret=secret,
        signature_header=signature_header,
        payload=payload,
    )

    assert event == {"type": "document.completed"}


@pytest.mark.parametrize(
    "signature_header, match",
    [
        ("", "Missing webhook signature header"),
        ("v1=abc123", "Missing timestamp or v1 signature"),
        ("t=abc,v1=abc123", "Invalid webhook signature timestamp"),
    ],
)
def test_verify_signature_raises_for_malformed_header(
    signature_header: str, match: str
) -> None:
    with pytest.raises(WebhookSignatureVerificationError, match=match):
        verify_signature(
            secret="whsecret_test",
            signature_header=signature_header,
            payload=b"{}",
        )


def test_verify_signature_raises_when_signature_is_expired(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "whsecret_test"
    payload = b'{"type":"document.completed"}'
    timestamp = 1_712_345_678
    signature_header = build_signature_header(secret, timestamp, payload)
    monkeypatch.setattr(
        "pdfgate.webhooks.time.time",
        lambda: timestamp + Config.WEBHOOK_SIGNATURE_TOLERANCE_SECONDS + 1,
    )

    with pytest.raises(WebhookSignatureVerificationError, match="expired"):
        verify_signature(
            secret=secret,
            signature_header=signature_header,
            payload=payload,
        )


def test_verify_signature_raises_when_signature_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pdfgate.webhooks.time.time", lambda: 1_712_345_678)

    with pytest.raises(WebhookSignatureVerificationError, match="Invalid webhook"):
        verify_signature(
            secret="whsecret_test",
            signature_header="t=1712345678,v1=deadbeef",
            payload=b'{"type":"document.completed"}',
        )


def test_generate_pdf_returns_json(
    document_response: DocumentResponse,
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.generate_pdf_url()
    route = respx_mock.post(url)
    route.mock(return_value=httpx.Response(201, json=document_response))
    params = GeneratePDFParams(html="<h1>Test</h1>")

    response = client.generate_pdf(params)

    assert isinstance(response, dict)
    assert response.get("id") == document_response["id"]
    assert response.get("status") == document_response["status"]
    assert response.get("created_at") == document_response["createdAt"]
    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_body.get("jsonResponse") is True


def test_flatten_pdf_by_document_id_returns_json(
    client: PDFGate,
    url_builder: URLBuilder,
    flattened_document_response: FlattenedDocumentResponse,
    document_id: str,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.flatten_pdf_url()
    route = respx_mock.post(url)
    route.mock(return_value=httpx.Response(201, json=flattened_document_response))
    params = FlattenPDFParams(document_id=document_id)

    response = client.flatten_pdf(params)

    assert isinstance(response, dict)
    assert response.get("id") == flattened_document_response["id"]
    assert response.get("status") == flattened_document_response["status"]
    assert response.get("created_at") == flattened_document_response["createdAt"]
    assert response.get("derived_from") == document_id
    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_body.get("jsonResponse") is True


def test_watermark_pdf_with_image_sends_watermark_file(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.watermark_pdf_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": str(uuid.uuid4()),
                "status": "completed",
                "type": "watermarked",
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = WatermarkPDFParams(
        document_id=str(uuid.uuid4()),
        type=WatermarkType.IMAGE,
        watermark=FileParam(name="watermark.png", data=b"fake-image-bytes"),
    )

    response = client.watermark_pdf(params)

    assert isinstance(response, dict)
    request_body = route.calls.last.request.content
    assert b'name="watermark"' in request_body
    assert b"watermark.png" in request_body
    assert b'name="jsonResponse"' in request_body


def test_watermark_pdf_with_text_sends_font_file(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.watermark_pdf_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": str(uuid.uuid4()),
                "status": "completed",
                "type": "watermarked",
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = WatermarkPDFParams(
        document_id=str(uuid.uuid4()),
        type=WatermarkType.TEXT,
        text="Confidential",
        font_file=FileParam(
            name="custom.ttf", data=b"fake-font-bytes", type="font/ttf"
        ),
    )

    response = client.watermark_pdf(params)

    assert isinstance(response, dict)
    request = route.calls.last.request
    assert "multipart/form-data" in request.headers.get("content-type", "")
    request_body = request.content
    assert b'name="fontFile"' in request_body
    assert b"custom.ttf" in request_body
    assert b'name="text"' in request_body
    assert b'name="jsonResponse"' in request_body


def test_send_envelope_returns_json(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    envelope_id = str(uuid.uuid4())
    url = url_builder.send_envelope_url(envelope_id)
    route = respx_mock.post(url)
    response_json = {
        "id": envelope_id,
        "status": "in_progress",
        "documents": [
            {
                "sourceDocumentId": str(uuid.uuid4()),
                "recipients": [
                    {
                        "email": "anna@example.com",
                        "status": "pending",
                        "fields": [],
                    }
                ],
                "status": "pending",
            }
        ],
        "createdAt": datetime.now().isoformat(),
        "metadata": {"customerId": "cus_123", "department": "sales"},
    }
    route.mock(return_value=httpx.Response(200, json=response_json))

    response = client.send_envelope(SendEnvelopeParams(envelope_id=envelope_id))

    assert isinstance(response, dict)
    assert response.get("id") == envelope_id
    assert response.get("status") == "in_progress"
    assert response.get("created_at") == response_json["createdAt"]
    assert response.get("metadata") == {
        "customer_id": "cus_123",
        "department": "sales",
    }
    assert json.loads(route.calls.last.request.content.decode("utf-8")) == {}


def test_get_envelope_returns_json(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    envelope_id = str(uuid.uuid4())
    url = url_builder.get_envelope_url(envelope_id)
    route = respx_mock.get(url)
    response_json = {
        "id": envelope_id,
        "status": "in_progress",
        "documents": [
            {
                "sourceDocumentId": str(uuid.uuid4()),
                "auditLogDocumentId": str(uuid.uuid4()),
                "recipients": [
                    {
                        "email": "anna@example.com",
                        "status": "pending",
                        "fields": [],
                        "signingLink": "https://example.com/sign",
                        "previewLink": "https://example.com/preview",
                    }
                ],
                "status": "pending",
            }
        ],
        "createdAt": datetime.now().isoformat(),
        "metadata": {"customerId": "cus_123", "department": "sales"},
    }
    route.mock(return_value=httpx.Response(200, json=response_json))

    response = client.get_envelope(GetEnvelopeParams(envelope_id=envelope_id))

    assert isinstance(response, dict)
    assert response.get("id") == envelope_id
    assert response.get("status") == "in_progress"
    assert response.get("created_at") == response_json["createdAt"]
    assert response.get("metadata") == {
        "customer_id": "cus_123",
        "department": "sales",
    }
    documents = response.get("documents", [])
    assert len(documents) == 1
    assert documents[0].get("audit_log_document_id") is not None
    recipients = documents[0].get("recipients", [])
    assert len(recipients) == 1
    assert recipients[0].get("signing_link") == "https://example.com/sign"
    assert recipients[0].get("preview_link") == "https://example.com/preview"
    assert route.calls.last.request.content == b""


def test_upload_file_sends_multipart_when_file_is_present(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.upload_file_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": str(uuid.uuid4()),
                "status": "completed",
                "type": "uploaded",
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = UploadFileParams(
        file=FileParam.pdf(name="input.pdf", data=b"fake-pdf-bytes"),
        url="https://example.com/will-be-sent-as-form-data",
    )

    response = client.upload_file(params)

    assert isinstance(response, dict)
    assert str(route.calls.last.request.url) == url
    assert route.calls.last.request.headers["content-type"].startswith(
        "multipart/form-data"
    )
    request_body = route.calls.last.request.content
    assert b'name="file"' in request_body
    assert b"input.pdf" in request_body
    assert b'name="url"' in request_body


def test_upload_file_with_url_sends_json_and_default_timeout(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.upload_file_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": str(uuid.uuid4()),
                "status": "completed",
                "type": "uploaded",
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    request = client.request_builder.build_upload_file(
        UploadFileParams(url="https://example.com")
    )
    response = client.upload_file(UploadFileParams(url="https://example.com"))

    assert isinstance(response, dict)
    assert request.timeout == Config.DEFAULT_TIMEOUT_SECONDS
    assert str(route.calls.last.request.url) == url
    request_json = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_json.get("url") == "https://example.com"


def test_create_envelope_sends_correct_json(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    source_doc_id = str(uuid.uuid4())
    envelope_id = str(uuid.uuid4())
    url = url_builder.envelope_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": envelope_id,
                "status": "created",
                "documents": [
                    {
                        "sourceDocumentId": source_doc_id,
                        "recipients": [
                            {
                                "email": "anna@example.com",
                                "status": "pending",
                                "fields": [],
                            }
                        ],
                        "status": "pending",
                    }
                ],
                "createdAt": datetime.now().isoformat(),
                "metadata": {"customerId": "cus_123"},
            },
        )
    )
    params = CreateEnvelopeParams(
        requester_name="John Doe",
        documents=[
            EnvelopeDocument(
                source_document_id=source_doc_id,
                name="Employment Agreement",
                recipients=[
                    EnvelopeRecipient(
                        email="anna@example.com",
                        name="Anna Smith",
                        role="signer",
                        reminder_interval_days=3,
                        reminder_attempts=2,
                    )
                ],
            )
        ],
        metadata={"customerId": "cus_123"},
    )

    response = client.create_envelope(params)

    assert isinstance(response, dict)
    assert response.get("id") == envelope_id
    assert response.get("status") == "created"
    assert response.get("created_at") is not None
    assert response.get("metadata") == {"customer_id": "cus_123"}
    documents = response.get("documents", [])
    assert len(documents) == 1
    assert documents[0].get("source_document_id") == source_doc_id

    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_body.get("requesterName") == "John Doe"
    assert request_body.get("metadata") == {"customerId": "cus_123"}
    docs = request_body.get("documents", [])
    assert len(docs) == 1
    assert docs[0].get("sourceDocumentId") == source_doc_id
    assert docs[0].get("name") == "Employment Agreement"
    recipients = docs[0].get("recipients", [])
    assert len(recipients) == 1
    assert recipients[0].get("email") == "anna@example.com"
    assert recipients[0].get("name") == "Anna Smith"
    assert recipients[0].get("role") == "signer"
    assert recipients[0].get("reminderIntervalDays") == 3
    assert recipients[0].get("reminderAttempts") == 2


def test_create_envelope_omits_optional_fields(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    source_doc_id = str(uuid.uuid4())
    url = url_builder.envelope_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": str(uuid.uuid4()),
                "status": "created",
                "documents": [],
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = CreateEnvelopeParams(
        requester_name="Jane Doe",
        documents=[
            EnvelopeDocument(
                source_document_id=source_doc_id,
                name="Contract",
                recipients=[EnvelopeRecipient(email="bob@example.com", name="Bob")],
            )
        ],
    )

    client.create_envelope(params)

    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert "metadata" not in request_body
    recipients = request_body["documents"][0]["recipients"]
    assert "role" not in recipients[0]
    assert "reminderIntervalDays" not in recipients[0]
    assert "reminderAttempts" not in recipients[0]


@pytest.mark.asyncio
async def test_create_envelope_async(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    source_doc_id = str(uuid.uuid4())
    envelope_id = str(uuid.uuid4())
    url = url_builder.envelope_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": envelope_id,
                "status": "created",
                "documents": [],
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = CreateEnvelopeParams(
        requester_name="John Doe",
        documents=[
            EnvelopeDocument(
                source_document_id=source_doc_id,
                name="Agreement",
                recipients=[EnvelopeRecipient(email="anna@example.com", name="Anna")],
            )
        ],
    )

    response = await client.create_envelope_async(params)

    assert isinstance(response, dict)
    assert response.get("id") == envelope_id
    assert response.get("status") == "created"


def test_flatten_pdf_forwards_field_names(
    client: PDFGate,
    url_builder: URLBuilder,
    flattened_document_response: FlattenedDocumentResponse,
    document_id: str,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.flatten_pdf_url()
    route = respx_mock.post(url)
    route.mock(return_value=httpx.Response(201, json=flattened_document_response))
    params = FlattenPDFParams(document_id=document_id, field_names=["name", "email"])

    client.flatten_pdf(params)

    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_body.get("fieldNames") == ["name", "email"]
    assert request_body.get("jsonResponse") is True


def test_add_form_fields_sends_overrides_and_fields(
    client: PDFGate,
    url_builder: URLBuilder,
    document_id: str,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.add_form_fields_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": str(uuid.uuid4()),
                "status": "completed",
                "type": "document_fields_added",
                "derivedFrom": document_id,
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = AddFormFieldsParams(
        document_id=document_id,
        field_overrides={"full_name": FieldOverride(role="signer", font_size=12)},
        fields=[
            ManualFormField(
                name="signed_on",
                type=DocumentFieldType.DATE,
                page=1,
                x=10,
                y=20,
                width=100,
                height=24,
                font_size=10,
            )
        ],
    )

    response = client.add_form_fields(params)

    assert response.get("derived_from") == document_id
    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_body.get("jsonResponse") is True
    # Field-override keys must be preserved verbatim (not camelCased),
    # while the override option keys are converted to camelCase.
    assert "full_name" in request_body["fieldOverrides"]
    assert request_body["fieldOverrides"]["full_name"]["fontSize"] == 12
    assert request_body["fieldOverrides"]["full_name"]["role"] == "signer"
    # Manual field inner keys are converted to camelCase.
    assert request_body["fields"][0]["name"] == "signed_on"
    assert request_body["fields"][0]["type"] == "date"
    assert request_body["fields"][0]["fontSize"] == 10


def test_delete_document_sends_delete_request(
    client: PDFGate,
    url_builder: URLBuilder,
    document_id: str,
    respx_mock: respx.MockRouter,
) -> None:
    url = url_builder.get_document_url(document_id)
    route = respx_mock.delete(url)
    route.mock(return_value=httpx.Response(204))

    client.delete_document(DeleteDocumentParams(document_id=document_id))

    assert route.called
    assert route.calls.last.request.method == "DELETE"


def test_create_webhook_sends_config_and_parses_response(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    webhook_id = str(uuid.uuid4())
    url = url_builder.webhook_url()
    route = respx_mock.post(url)
    route.mock(
        return_value=httpx.Response(
            201,
            json={
                "id": webhook_id,
                "url": "https://example.com/hook",
                "eventTypes": ["envelope.completed"],
                "status": "active",
                "secret": "whsec_abc",
                "createdAt": datetime.now().isoformat(),
            },
        )
    )
    params = CreateWebhookParams(
        url="https://example.com/hook",
        event_types=[WebhookEventType.ENVELOPE_COMPLETED],
        description="my hook",
    )

    response = client.create_webhook(params)

    assert response.get("id") == webhook_id
    assert response.get("secret") == "whsec_abc"
    assert response.get("event_types") == ["envelope.completed"]
    request_body = json.loads(route.calls.last.request.content.decode("utf-8"))
    assert request_body.get("url") == "https://example.com/hook"
    assert request_body.get("eventTypes") == ["envelope.completed"]
    assert request_body.get("description") == "my hook"


def test_get_webhook_returns_json(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    webhook_id = str(uuid.uuid4())
    url = url_builder.get_webhook_url(webhook_id)
    route = respx_mock.get(url)
    route.mock(
        return_value=httpx.Response(
            200,
            json={
                "id": webhook_id,
                "url": "https://example.com/hook",
                "eventTypes": ["envelope.sent"],
                "status": "active",
                "createdAt": datetime.now().isoformat(),
            },
        )
    )

    response = client.get_webhook(GetWebhookParams(webhook_id=webhook_id))

    assert response.get("id") == webhook_id
    assert response.get("status") == "active"
    assert route.calls.last.request.method == "GET"


def test_delete_webhook_sends_delete_request(
    client: PDFGate,
    url_builder: URLBuilder,
    respx_mock: respx.MockRouter,
) -> None:
    webhook_id = str(uuid.uuid4())
    url = url_builder.get_webhook_url(webhook_id)
    route = respx_mock.delete(url)
    route.mock(return_value=httpx.Response(204))

    client.delete_webhook(DeleteWebhookParams(webhook_id=webhook_id))

    assert route.called
    assert route.calls.last.request.method == "DELETE"
