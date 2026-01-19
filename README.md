# PDFGate's official Python SDK

PDFGate lets you generate, process, and secure PDFs via a simple API:

- HTML or URL to PDF
- Fillable forms
- Flatten, compress, watermark, protect PDFs
- Extract PDF form data

📘 Documentation: https://pdfgate.com/documentation
🔑 Dashboard & API keys: https://dashboard.pdfgate.com

# Installation

```sh
pip install pdfgate
```

# Quick start

```python
import os

import pdfgate
import GeneratePDFParams


client = PDFGate(api_key=os.getenv("PDFGATE_API_KEY"))
params = GeneratePDFParams(url="https://example.com")
pdf = client.generate_pdf(params)

with open("output.pdf", "wb") as f:
  f.write(pdf)
```

# Responses

The two response types for most endpoints are either the raw bytes of the
PDF file or the documents metadata that you can use to query or download later:

- file: this is represented by `bytes` and it can be saved directly into a file.
- `PDFGateDocument`: this is a `TypedDict` that holds all the metadata of the file including its `id`,  and a `file_url` to download it if it was requested by specifying `pre_signed_url_expires_in` in the request.

# Examples

## Generate PDF

```python
params = GeneratePDFParams(html="<h1>Hello from PDFGate!</h1>")
pdf = client.generate_pdf(params)

with open("output.pdf", "wb") as f:
  f.write(pdf)
```

## Get document metadata

```python
document_response = client.get_document(GetDocumentParams(document_id=document_id))

assert document_response = {
    "id" : "6642381c5c61"
    "status" : DocumentStatus.COMPLETED
    "type" : DocumentType.FROM_HTML,
    "file_url" : "https://api.pdfgate.com/file/open/:preSignedUrlToken"
    "size" : 1620006
    "createdAt" : datetime(2024,02,13, 15, 56, 12, 607)"
}
```

## Download a stored PDF file

```python
file_content = client.get_file(GetFileParams(document_id=document_id))

with open("output.pdf", "wb") as f:
  f.write(pdf)
```

## Flatten a PDF (make form-fields non-editable)

```python
flatten_pdf_params = FlattenPDFDocumentParams(
    document_id=document_id, json_response=True
)
flattened_document = client.flatten_pdf(flatten_pdf_params)
```

## Compress a PDF

```python
compress_pdf_params = CompressPDFByDocumentIdParams(
    document_id=document_id, json_response=True
)
response = client.compress_pdf(compress_pdf_params)
```

## Watermark a PDF

```python

```

## Protect (encrypt) a PDF

```python
protect_pdf_params = ProtectPDFByDocumentIdParams(
    document_id=document_id,
    user_password=str(uuid.uuid4()),
    owner_password=str(uuid.uuid4()),
    json_response=True,
)
response = client.protect_pdf(protect_pdf_params)
```

## Extract PDF form fields values

```python
html_form = """
    <form>
        <input type='text' name='first_name' value='John'/>
        <input type='text' name='last_name' value='Doe'/>
    </form>
    """
generate_pdf_params = GeneratePDFParams(
    html=html_form, enable_form_fields=True, json_response=True
)
document_response = cast(PDFGateDocument, client.generate_pdf(generate_pdf_params))
document_id = cast(str, document_response.get("id"))

extract_form_params = ExtractPDFFormDataByDocumentIdParams(document_id=document_id)
response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))
```

# Development

Hatch is used as a build system and for dependency management.

Run tests:

```sh
hatch run test:test
```

Run Ruff to run linting and formatting:

```sh
hatch run dev:lint
```

Run mypy for type checking:

```sh
hatch run dev:check
```

# Support

📧 Email: support@pdfgate.com
📘 Docs: https://pdfgate.com/documentation
