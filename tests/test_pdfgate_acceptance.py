import io
import os
import pathlib
import sys
from typing import Any, TypedDict, cast
import uuid

import pytest
import pypdf
from pdfgate_sdk_python.params import (
    CompressPDFByDocumentIdParams,
    CompressPDFByFileParams,
    ExtractPDFFormDataByDocumentIdParams,
    ExtractPDFFormDataByFileParams,
    FlattenPDFByFileParams,
    FlattenPDFByDocumentIdParams,
    GeneratePDFParams,
    GetDocumentParams,
    GetFileParams,
    PDFFileParam,
    ProtectPDFByDocumentIdParams,
    ProtectPDFByFileParams,
)
from pdfgate_sdk_python.pdfgate import PDFGate
from pdfgate_sdk_python.responses import PDFGateDocument


@pytest.fixture(scope="module")
def api_key() -> str:
    return os.getenv("PDFGATE_API_KEY", "")


@pytest.fixture(scope="module")
def client(api_key: str) -> PDFGate:
    return PDFGate(api_key=api_key)


@pytest.fixture(scope="module")
def pdf_document(client: PDFGate) -> PDFGateDocument:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=True
    )
    document_response = client.generate_pdf(generate_pdf_params)
    pdf_document = cast(PDFGateDocument, document_response)

    return pdf_document


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
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=False
    )
    file_content = client.generate_pdf(generate_pdf_params)

    assert isinstance(file_content, bytes)

    return file_content


@pytest.fixture
def html_with_form() -> str:
    return """
        <form>
            <input type='text' name='first_name' value='John'/>
            <input type='text' name='last_name' value='Doe'/>
        </form>
        """


def test_generate_pdf_with_json_response(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=True
    )
    document_response = client.generate_pdf(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


@pytest.mark.asyncio
async def test_generate_pdf_async_with_json_response(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=True
    )
    document_response = await client.generate_pdf_async(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response and document_response["status"] == "completed"
    assert "created_at" in document_response


def test_generate_pdf_with_binary_response(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(
        html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=False
    )
    file_content = cast(bytes, client.generate_pdf(generate_pdf_params))

    assert isinstance(file_content, bytes)
    assert file_content.startswith(b"%PDF")


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
    flatten_pdf_params = FlattenPDFByDocumentIdParams(
        document_id=document_id, json_response=True
    )
    flattened_document = client.flatten_pdf(flatten_pdf_params)

    assert isinstance(flattened_document, dict)
    assert "id" in flattened_document
    assert flattened_document["id"] != document_id
    assert "status" in flattened_document
    assert "created_at" in flattened_document


def test_flatten_pdf_by_file(client: PDFGate, pdf_file: bytes) -> None:
    file_param = PDFFileParam(name="input.pdf", data=pdf_file)
    flatten_pdf_params = FlattenPDFByFileParams(file=file_param, json_response=True)
    flattened_document = client.flatten_pdf(flatten_pdf_params)

    assert isinstance(flattened_document, dict)
    assert "id" in flattened_document
    assert "status" in flattened_document
    assert "created_at" in flattened_document


@pytest.mark.asyncio
async def test_flatten_pdf_async_by_file(client: PDFGate, pdf_file: bytes) -> None:
    file_param = PDFFileParam(name="input.pdf", data=pdf_file)
    flatten_pdf_params = FlattenPDFByFileParams(file=file_param, json_response=True)
    flattened_document = await client.flatten_pdf_async(flatten_pdf_params)

    assert isinstance(flattened_document, dict)
    assert "id" in flattened_document
    assert "status" in flattened_document
    assert "created_at" in flattened_document


def test_extract_pdf_form_data_by_document_id(
    client: PDFGate, html_with_form: str
) -> None:
    generate_pdf_params = GeneratePDFParams(
        html=html_with_form, enable_form_fields=True, json_response=True
    )
    document_response = cast(PDFGateDocument, client.generate_pdf(generate_pdf_params))
    document_id = cast(str, document_response.get("id"))

    extract_form_params = ExtractPDFFormDataByDocumentIdParams(document_id=document_id)
    response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))

    assert isinstance(response, dict)
    assert "first_name" in response and response.get("first_name") == "John"
    assert "last_name" in response and response.get("last_name") == "Doe"


def test_extract_pdf_form_data_by_file(client: PDFGate, html_with_form: str) -> None:
    generate_pdf_params = GeneratePDFParams(
        html=html_with_form, enable_form_fields=True, json_response=False
    )
    file_content = cast(bytes, client.generate_pdf(generate_pdf_params))

    extract_form_params = ExtractPDFFormDataByFileParams(
        file=PDFFileParam(name="input.pdf", data=file_content)
    )
    response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))

    assert isinstance(response, dict)
    assert "first_name" in response and response.get("first_name") == "John"
    assert "last_name" in response and response.get("last_name") == "Doe"


def test_protect_pdf_by_document_id_with_json_response(
    client: PDFGate, document_id: str
) -> None:
    user_password = str(uuid.uuid4())
    owner_password = str(uuid.uuid4())
    protect_pdf_params = ProtectPDFByDocumentIdParams(
        document_id=document_id,
        user_password=user_password,
        owner_password=owner_password,
        json_response=True,
    )

    response = client.protect_pdf(protect_pdf_params)

    assert isinstance(response, dict)
    assert "id" in response and response.get("id") != document_id
    assert "status" in response and response.get("status") == "completed"


def test_protect_pdf_by_file_with_file_response(
    client: PDFGate, pdf_file: bytes
) -> None:
    user_password = str(uuid.uuid4())
    owner_password = str(uuid.uuid4())
    protect_pdf_params = ProtectPDFByFileParams(
        file=PDFFileParam(name="input.pdf", data=pdf_file),
        user_password=user_password,
        owner_password=owner_password,
        json_response=False,
    )

    protected_file_content = client.protect_pdf(protect_pdf_params)

    assert isinstance(protected_file_content, bytes)

    reader = pypdf.PdfReader(io.BytesIO(protected_file_content))
    assert reader.is_encrypted
    assert reader.decrypt(user_password) == pypdf.PasswordType.USER_PASSWORD
    assert reader.decrypt(owner_password) == pypdf.PasswordType.OWNER_PASSWORD


def test_compress_pdf_by_document_id_with_json_response(
    client: PDFGate, document_id_with_size: DocumentIdWithSize
) -> None:
    compress_pdf_params = CompressPDFByDocumentIdParams(
        document_id=document_id_with_size["document_id"], json_response=True
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


def test_compress_pdf_by_file_with_file_response(
    client: PDFGate, pdf_file: bytes, tmp_path: pathlib.Path
) -> None:
    input_pdf = tmp_path / "input.pdf"
    with open(input_pdf, "wb") as f:
        f.write(pdf_file)

    compress_pdf_params = CompressPDFByFileParams(
        file=PDFFileParam(name="input.pdf", data=pdf_file), json_response=False
    )

    compressed_file = client.compress_pdf(compress_pdf_params)

    assert isinstance(compressed_file, bytes)
    assert compressed_file.startswith(b"%PDF")
    # The Sandobox API may not always yield a smaller file because it adds
    # a watermark.
    # assert len(compressed_file) < len(pdf_file)
