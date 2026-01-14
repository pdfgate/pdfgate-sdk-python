
import os
from typing import cast

import pytest
from pdfgate_sdk_python.params import GeneratePDFParams, GetDocumentParams, GetFileParams
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