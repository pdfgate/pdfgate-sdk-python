import io
import os
import sys
from typing import Any, TypedDict, cast
import uuid

import pytest
from PIL import Image
from pdfgate.errors import PDFGateError
from pdfgate.params import (
    AddFormFieldsParams,
    CompressPDFParams,
    CreateEnvelopeParams,
    CreateWebhookParams,
    DeleteDocumentParams,
    DeleteWebhookParams,
    EnvelopeDocument,
    EnvelopeRecipient,
    ExtractPDFFormDataParams,
    FileParam,
    FlattenPDFParams,
    GeneratePDFAuthentication,
    GeneratePDFParams,
    GetDocumentParams,
    GetEnvelopeParams,
    GetFileParams,
    GetWebhookParams,
    ManualFormField,
    PageSizeType,
    PdfPageMargin,
    ProtectPDFParams,
    SendEnvelopeParams,
    VoidEnvelopeParams,
    DeleteEnvelopeParams,
    UploadFileParams,
    Viewport,
    WatermarkPDFParams,
    WatermarkType,
)
from pdfgate.pdfgate import PDFGate
from pdfgate.responses import (
    DocumentFieldType,
    PDFGateDocument,
    PDFGateEnvelope,
    WebhookEventType,
)


@pytest.fixture(scope="module")
def api_key() -> str:
    return os.getenv("PDFGATE_API_KEY", "")


@pytest.fixture(scope="module")
def client(api_key: str) -> PDFGate:
    return PDFGate(api_key=api_key)


@pytest.fixture(scope="module")
def pdf_document(client: PDFGate) -> PDFGateDocument:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>"
    )
    document_response = client.generate_pdf(generate_pdf_params)

    return document_response


@pytest.fixture(scope="module")
def document_id(pdf_document: PDFGateDocument) -> str:
    return pdf_document.get("id", "")


class DocumentIdWithSize(TypedDict):
    document_id: str
    size: int


@pytest.fixture(scope="module")
def document_id_with_size(pdf_document: PDFGateDocument) -> DocumentIdWithSize:
    return {
        "document_id": pdf_document.get("id", ""),
        "size": cast(int, pdf_document.get("size", 0)),
    }


_ENVELOPE_HTML = """
<html><body style="font-family: Arial, sans-serif; padding: 40px;">
  <h2>Agreement</h2>
  <p>Please review and complete the required fields below.</p>
  <div style="margin-top: 30px;">
    <label>Full Name</label><br />
    <input type="text" name="recipient-name" style="width: 300px; height: 30px;" />
  </div>
  <div style="margin-top: 30px;">
    <label>Signature</label><br />
    <pdfgate-signature-field name="signature" style="width: 200px; height: 200px;"></pdfgate-signature-field>
  </div>
  <div style="margin-top: 30px;">
    <label>Date</label><br />
    <input type="datetime-local" name="signature-date" pdfgate-auto-fill="true" style="width: 200px; height: 30px;" />
  </div>
</body></html>
"""


@pytest.fixture(scope="module")
def envelope_document_id(client: PDFGate) -> str:
    document_response = client.generate_pdf(
        GeneratePDFParams(
            html=_ENVELOPE_HTML,
            enable_form_fields=True,
        )
    )
    return cast(str, document_response.get("id"))


@pytest.fixture(scope="module")
def created_envelope(client: PDFGate, envelope_document_id: str) -> PDFGateEnvelope:
    return client.create_envelope(
        CreateEnvelopeParams(
            requester_name="John Doe",
            documents=[
                EnvelopeDocument(
                    source_document_id=envelope_document_id,
                    name="Employment Agreement",
                    recipients=[
                        EnvelopeRecipient(
                            email="anna@example.com",
                            name="Anna Smith",
                        )
                    ],
                )
            ],
            metadata={"customerId": "cus_123", "department": "sales"},
        )
    )


@pytest.fixture(scope="module")
def pdf_file(client: PDFGate) -> bytes:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>"
    )
    document_response = client.generate_pdf(generate_pdf_params)
    document_id = cast(str, document_response.get("id"))
    file_content = client.get_file(GetFileParams(document_id=document_id))

    assert isinstance(file_content, bytes)

    return file_content


@pytest.fixture(scope="module")
def jpg_file() -> bytes:
    """Generates a random image."""
    image = Image.effect_noise((128, 128), 100)
    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format="JPEG", quality=90)
    jpeg_bytes = image_byte_arr.getvalue()

    return jpeg_bytes


@pytest.fixture
def html_with_form() -> str:
    return """
        <form>
            <input type='text' name='first_name' value='John'/>
            <input type='text' name='last_name' value='Doe'/>
        </form>
        """


def test_generate_pdf_with_enum_params(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>",
        page_size_type=PageSizeType.A4,
        margin=PdfPageMargin(top="10", bottom="10", left="10", right="10"),
    )
    document_response = client.generate_pdf(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


def test_generate_pdf_with_json_response(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>"
    )
    document_response = client.generate_pdf(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


@pytest.mark.asyncio
async def test_generate_pdf_async_with_json_response(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>"
    )
    document_response = await client.generate_pdf_async(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


def test_generate_pdf_with_authentication(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        url="https://httpbin.org/basic-auth/user/passwd",
        authentication=GeneratePDFAuthentication(username="user", password="passwd"),
        viewport=Viewport(width=1280, height=720),
    )
    document_response = client.generate_pdf(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response and document_response["status"] == "completed"


def test_get_file(client: PDFGate, document_id: str) -> None:
    file_content = client.get_file(GetFileParams(document_id=document_id))

    assert isinstance(file_content, bytes)
    assert file_content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_get_file_async(client: PDFGate, document_id: str) -> None:
    file_content = await client.get_file_async(GetFileParams(document_id=document_id))

    assert isinstance(file_content, bytes)
    assert file_content.startswith(b"%PDF")


def test_get_document(client: PDFGate, document_id: str) -> None:
    document_response = client.get_document(GetDocumentParams(document_id=document_id))

    assert isinstance(document_response, dict)
    assert "id" in document_response and document_response["id"] == document_id
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


@pytest.mark.asyncio
async def test_get_document_async(client: PDFGate, document_id: str) -> None:
    document_response = await client.get_document_async(
        GetDocumentParams(document_id=document_id)
    )

    assert isinstance(document_response, dict)
    assert "id" in document_response and document_response["id"] == document_id
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


def test_flatten_pdf_by_document_id(client: PDFGate, document_id: str) -> None:
    flatten_pdf_params = FlattenPDFParams(document_id=document_id)
    flattened_document = client.flatten_pdf(flatten_pdf_params)

    assert isinstance(flattened_document, dict)
    assert "id" in flattened_document
    assert flattened_document["id"] != document_id
    assert "status" in flattened_document
    assert "created_at" in flattened_document


def test_extract_pdf_form_data_by_document_id(
    client: PDFGate, html_with_form: str
) -> None:
    generate_pdf_params = GeneratePDFParams(
        html=html_with_form, enable_form_fields=True
    )
    document_response = client.generate_pdf(generate_pdf_params)
    document_id = cast(str, document_response.get("id"))

    extract_form_params = ExtractPDFFormDataParams(document_id=document_id)
    response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))

    assert isinstance(response, dict)
    assert "first_name" in response and response.get("first_name") == "John"
    assert "last_name" in response and response.get("last_name") == "Doe"


def test_protect_pdf_by_document_id_with_json_response(
    client: PDFGate, document_id: str
) -> None:
    user_password = str(uuid.uuid4())
    owner_password = str(uuid.uuid4())
    protect_pdf_params = ProtectPDFParams(
        document_id=document_id,
        user_password=user_password,
        owner_password=owner_password,
    )

    response = client.protect_pdf(protect_pdf_params)

    assert isinstance(response, dict)
    assert "id" in response and response.get("id") != document_id
    assert "status" in response and response.get("status") == "completed"


def test_compress_pdf_by_document_id_with_json_response(
    client: PDFGate, document_id_with_size: DocumentIdWithSize
) -> None:
    compress_pdf_params = CompressPDFParams(
        document_id=document_id_with_size["document_id"]
    )

    response = client.compress_pdf(compress_pdf_params)

    assert isinstance(response, dict)
    assert (
        "id" in response and response.get("id") != document_id_with_size["document_id"]
    )
    assert "status" in response and response.get("status") == "completed"
    assert "type" in response and response.get("type") == "compressed"
    assert (
        "size" in response
        and cast(int, response.get("size", sys.maxsize)) < document_id_with_size["size"]
    )


def test_watermark_pdf_with_text_by_document_id(
    client: PDFGate, document_id: str
) -> None:
    watermark_pdf_params = WatermarkPDFParams(
        document_id=document_id,
        type=WatermarkType.TEXT,
        text="Confidential - Do Not Distribute",
    )
    response = client.watermark_pdf(watermark_pdf_params)

    assert isinstance(response, dict)
    assert "id" in response and response.get("id") != document_id
    assert "type" in response and response.get("type") == "watermarked"
    assert "derived_from" in response and response.get("derived_from") == document_id
    assert "status" in response and response.get("status") == "completed"


def test_upload_file(client: PDFGate, pdf_file: bytes) -> None:
    file_param = FileParam.pdf(name="input.pdf", data=pdf_file)
    document_response = client.upload_file(UploadFileParams(file=file_param))

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "type" in document_response and document_response["type"] == "uploaded"
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


@pytest.mark.asyncio
async def test_upload_file_async(client: PDFGate, pdf_file: bytes) -> None:
    file_param = FileParam.pdf(name="input.pdf", data=pdf_file)
    document_response = await client.upload_file_async(
        UploadFileParams(file=file_param)
    )

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "type" in document_response and document_response["type"] == "uploaded"
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


def test_create_envelope(created_envelope: PDFGateEnvelope) -> None:
    assert isinstance(created_envelope, dict)
    assert "id" in created_envelope
    assert created_envelope.get("status") == "created"
    assert "created_at" in created_envelope
    documents = created_envelope.get("documents", [])
    assert len(documents) >= 1
    assert created_envelope.get("metadata") == {
        "customer_id": "cus_123",
        "department": "sales",
    }


@pytest.mark.asyncio
async def test_create_envelope_async(
    client: PDFGate, envelope_document_id: str
) -> None:
    params = CreateEnvelopeParams(
        requester_name="Jane Doe",
        documents=[
            EnvelopeDocument(
                source_document_id=envelope_document_id,
                name="Service Agreement",
                recipients=[
                    EnvelopeRecipient(
                        email="bob@example.com",
                        name="Bob Smith",
                    )
                ],
            )
        ],
        metadata={"customerId": "cus_456", "department": "engineering"},
    )

    response = await client.create_envelope_async(params)

    assert isinstance(response, dict)
    assert "id" in response
    assert response.get("status") == "created"
    assert "created_at" in response
    documents = response.get("documents", [])
    assert len(documents) >= 1
    assert response.get("metadata") == {
        "customer_id": "cus_456",
        "department": "engineering",
    }


def test_send_envelope(client: PDFGate, created_envelope: PDFGateEnvelope) -> None:
    created_envelope_id = cast(str, created_envelope.get("id"))
    response = client.send_envelope(SendEnvelopeParams(envelope_id=created_envelope_id))

    assert isinstance(response, dict)
    assert response.get("id") == created_envelope_id
    assert response.get("status") == "in_progress"
    documents = response.get("documents", [])
    assert len(documents) >= 1


def test_get_envelope(client: PDFGate, created_envelope: PDFGateEnvelope) -> None:
    created_envelope_id = cast(str, created_envelope.get("id"))

    response = client.get_envelope(GetEnvelopeParams(envelope_id=created_envelope_id))

    assert isinstance(response, dict)
    assert response.get("id") == created_envelope_id
    assert response.get("status") in {"created", "in_progress"}
    documents = response.get("documents", [])
    assert len(documents) >= 1
    assert response.get("metadata") == {
        "customer_id": "cus_123",
        "department": "sales",
    }


def test_void_and_delete_envelope(client: PDFGate, envelope_document_id: str) -> None:
    # Own envelope — voiding the shared created_envelope fixture would break
    # the send/get tests that reuse it.
    envelope = client.create_envelope(
        CreateEnvelopeParams(
            requester_name="Jane Doe",
            documents=[
                EnvelopeDocument(
                    source_document_id=envelope_document_id,
                    name="Void Delete Agreement",
                    recipients=[
                        EnvelopeRecipient(
                            email="anna@example.com",
                            name="Anna Smith",
                        )
                    ],
                )
            ],
            expires_in_days=10,
        )
    )
    envelope_id = cast(str, envelope.get("id"))
    assert "expires_at" in envelope

    voided = client.void_envelope(
        VoidEnvelopeParams(envelope_id=envelope_id, reason="Acceptance test void")
    )
    assert voided.get("status") == "voided"
    assert "voided_at" in voided
    assert voided.get("void_reason") == "Acceptance test void"

    with pytest.raises(PDFGateError):
        client.void_envelope(VoidEnvelopeParams(envelope_id=envelope_id))

    client.delete_envelope(DeleteEnvelopeParams(envelope_id=envelope_id))

    with pytest.raises(PDFGateError):
        client.get_envelope(GetEnvelopeParams(envelope_id=envelope_id))


def test_flatten_pdf_with_field_names(client: PDFGate, html_with_form: str) -> None:
    document = client.generate_pdf(
        GeneratePDFParams(html=html_with_form, enable_form_fields=True)
    )
    document_id = cast(str, document.get("id"))

    flattened = client.flatten_pdf(
        FlattenPDFParams(document_id=document_id, field_names=["first_name"])
    )

    assert isinstance(flattened, dict)
    assert "id" in flattened
    assert flattened["id"] != document_id
    assert flattened.get("status") == "completed"


def test_add_form_fields(client: PDFGate, document_id: str) -> None:
    response = client.add_form_fields(
        AddFormFieldsParams(
            document_id=document_id,
            fields=[
                ManualFormField(
                    name="full_name",
                    type=DocumentFieldType.TEXT,
                    page=1,
                    x=50,
                    y=500,
                    width=200,
                    height=24,
                )
            ],
        )
    )

    assert isinstance(response, dict)
    assert response.get("id") != document_id
    assert response.get("status") == "completed"
    assert response.get("type") == "document_fields_added"


def test_delete_document(client: PDFGate) -> None:
    document = client.generate_pdf(
        GeneratePDFParams(html="<html><body><h1>Delete me</h1></body></html>")
    )
    document_id = cast(str, document.get("id"))

    client.delete_document(DeleteDocumentParams(document_id=document_id))

    with pytest.raises(PDFGateError):
        client.get_document(GetDocumentParams(document_id=document_id))


def test_webhook_lifecycle(client: PDFGate) -> None:
    url = f"https://example.com/pdfgate-hook-{uuid.uuid4()}"

    created = client.create_webhook(
        CreateWebhookParams(
            url=url,
            event_types=[
                WebhookEventType.ENVELOPE_COMPLETED,
                WebhookEventType.ENVELOPE_SENT,
            ],
            description="Python SDK acceptance test",
        )
    )

    assert isinstance(created, dict)
    webhook_id = cast(str, created.get("id"))
    assert webhook_id
    assert created.get("url") == url
    assert created.get("status") == "active"
    # The signing secret is only returned at creation time.
    assert isinstance(created.get("secret"), str) and created.get("secret")

    try:
        fetched = client.get_webhook(GetWebhookParams(webhook_id=webhook_id))
        assert fetched.get("id") == webhook_id
        assert fetched.get("url") == url
        # The secret is not returned outside of creation.
        assert fetched.get("secret") is None
    finally:
        client.delete_webhook(DeleteWebhookParams(webhook_id=webhook_id))

    with pytest.raises(PDFGateError):
        client.get_webhook(GetWebhookParams(webhook_id=webhook_id))
