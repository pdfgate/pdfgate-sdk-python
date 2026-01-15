
import io
import os
from typing import Any, cast
import uuid

import pytest
import pypdf
from pdfgate_sdk_python.params import ExtractPDFFormDataByDocumentIdParams, ExtractPDFFormDataByFileParams, FlattenPDFBinaryParams, FlattenPDFDocumentParams, GeneratePDFParams, GetDocumentParams, GetFileParams, PDFFileParam, ProtectPDFByDocumentIdParams, ProtectPDFByFileParams
from pdfgate_sdk_python.pdfgate import PDFGate
from pdfgate_sdk_python.responses import PDFGateDocument



@pytest.fixture(scope="module")
def api_key() -> str:
    return os.getenv("PDFGATE_API_KEY", "")

@pytest.fixture(scope="module")
def client(api_key: str) -> PDFGate:
    return PDFGate(api_key=api_key)

@pytest.fixture(scope="module")
def document_id(client: PDFGate) -> str:
    generate_pdf_params = GeneratePDFParams(html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=True)
    document_response = client.generate_pdf(generate_pdf_params)
    pdf_document = cast(PDFGateDocument, document_response)

    return pdf_document.get("id", "")

@pytest.fixture(scope="module")
def pdf_file(client: PDFGate) -> bytes:
    generate_pdf_params = GeneratePDFParams(html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=False)
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
    generate_pdf_params = GeneratePDFParams(html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=True)
    document_response = client.generate_pdf(generate_pdf_params)

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response
    assert "created_at" in document_response

def test_generate_pdf_with_binary_response(client: PDFGate) -> None:
    generate_pdf_params = GeneratePDFParams(html="<html><body><h1>Hello, PDFGate!</h1></body></html>", json_response=False)
    file_content = cast(bytes, client.generate_pdf(generate_pdf_params))

    assert isinstance(file_content, bytes)
    assert file_content.startswith(b'%PDF')

def test_get_file(client: PDFGate, document_id: str) -> None:
    file_content = client.get_file(GetFileParams(document_id=document_id))

    assert isinstance(file_content, bytes)
    assert file_content.startswith(b'%PDF')

def test_get_document(client: PDFGate, document_id: str) -> None:
    document_response = client.get_document(GetDocumentParams(document_id=document_id))

    assert isinstance(document_response, dict)
    assert "id" in document_response
    assert "status" in document_response
    assert "created_at" in document_response

def test_flatten_pdf_by_document_id(client: PDFGate, document_id: str) -> None:
    flatten_pdf_params = FlattenPDFDocumentParams(document_id=document_id, json_response=True)
    flattened_document = client.flatten_pdf(flatten_pdf_params)

    assert isinstance(flattened_document, dict)
    assert "id" in flattened_document
    assert flattened_document["id"] != document_id
    assert "status" in flattened_document
    assert "created_at" in flattened_document

def test_flatten_pdf_by_file(client: PDFGate, pdf_file: bytes) -> None:
    file_param = PDFFileParam(name="input.pdf", data=pdf_file)
    flatten_pdf_params = FlattenPDFBinaryParams(file=file_param, json_response=True)
    flattened_document = client.flatten_pdf(flatten_pdf_params)

    assert isinstance(flattened_document, dict)
    assert "id" in flattened_document
    assert "status" in flattened_document
    assert "created_at" in flattened_document

def test_extract_pdf_form_data_by_document_id(client: PDFGate, html_with_form: str) -> None:
    generate_pdf_params = GeneratePDFParams(html=html_with_form, enable_form_fields=True, json_response=True)
    document_response = cast(PDFGateDocument, client.generate_pdf(generate_pdf_params))
    document_id = cast(str, document_response.get("id"))

    extract_form_params = ExtractPDFFormDataByDocumentIdParams(document_id=document_id)
    response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))

    assert isinstance(response, dict)
    assert "first_name" in response and response.get("first_name")  == "John"
    assert "last_name" in response and response.get("last_name")  == "Doe"

def test_extract_pdf_form_data_by_file(client: PDFGate, html_with_form: str) -> None:
    generate_pdf_params = GeneratePDFParams(html=html_with_form, enable_form_fields=True, json_response=False)
    file_content = cast(bytes, client.generate_pdf(generate_pdf_params))

    extract_form_params = ExtractPDFFormDataByFileParams(file=PDFFileParam(name="input.pdf", data=file_content))
    response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))

    assert isinstance(response, dict)
    assert "first_name" in response and response.get("first_name")  == "John"
    assert "last_name" in response and response.get("last_name")  == "Doe"

def test_protect_pdf_by_document_id_with_json_response(client:PDFGate, document_id: str) -> None:
    user_password = str(uuid.uuid4())
    owner_password = str(uuid.uuid4())
    protect_pdf_params = ProtectPDFByDocumentIdParams(
        document_id=document_id,
        user_password=user_password,
        owner_password=owner_password,
        json_response=True
    )

    response = client.protect_pdf(protect_pdf_params)
    
    assert isinstance(response, dict)
    assert "id" in response and response.get("id")  != document_id
    assert "status" in response and response.get("status")  == "completed"

def test_protect_pdf_by_file_with_file_response(client: PDFGate, pdf_file: bytes) -> None:
    user_password = str(uuid.uuid4())
    owner_password = str(uuid.uuid4())
    protect_pdf_params = ProtectPDFByFileParams(
        file=PDFFileParam(name="input.pdf", data=pdf_file),
        user_password=user_password,
        owner_password=owner_password,
        json_response=False
    )

    protected_file_content = client.protect_pdf(protect_pdf_params)

    assert isinstance(protected_file_content, bytes)

    reader = pypdf.PdfReader(io.BytesIO(protected_file_content))
    assert reader.is_encrypted
    assert reader.decrypt(user_password) == pypdf.PasswordType.USER_PASSWORD
    assert reader.decrypt(owner_password) == pypdf.PasswordType.OWNER_PASSWORD