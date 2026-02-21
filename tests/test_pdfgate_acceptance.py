import io
import os
import sys
from typing import Any, TypedDict, cast
import uuid

import pytest
from PIL import Image
from pdfgate.params import (
    CompressPDFParams,
    ExtractPDFFormDataParams,
    FlattenPDFParams,
    GeneratePDFAuthentication,
    GeneratePDFParams,
    GetDocumentParams,
    GetFileParams,
    PageSizeType,
    PdfPageMargin,
    ProtectPDFParams,
    Viewport,
    WatermarkPDFParams,
    WatermarkType,
)
from pdfgate.pdfgate import PDFGate
from pdfgate.responses import PDFGateDocument


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
