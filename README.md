# PDFGate's official Python SDK

PDFGate lets you generate, process, and secure PDFs via a simple API:

- HTML or URL to PDF
- Fillable forms
- Flatten, compress, watermark, protect PDFs
- Extract PDF form data

📘 Documentation: https://pdfgate.com/documentation<br>
🔑 Dashboard & API keys: https://dashboard.pdfgate.com

## pdfgate-sdk-python

[![PyPI - Version](https://img.shields.io/pypi/v/pdfgate-sdk-python.svg)](https://pypi.org/project/pdfgate-sdk-python)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pdfgate-sdk-python.svg)](https://pypi.org/project/pdfgate-sdk-python)


## Table of Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Sync & Async](#sync--async)
- [Responses](#responses)
- [Webhook Verification](#webhook-verification)
- [Examples](#examples)
- [Development](#development)
- [Support](#support)
- [License](#license)

# Installation

```sh
pip install pdfgate
```

# Quick start

```python
import os

from pdfgate import PDFGate, GeneratePDFParams


client = PDFGate(api_key=os.getenv("PDFGATE_API_KEY"))
params = GeneratePDFParams(url="https://example.com")
document = client.generate_pdf(params)

print(document["id"])
```

# Sync & Async

There are sync and async versions of all methods, the only difference is that the method name has an `async` suffix:

```python
document_response = client.get_document(GetDocumentParams(document_id=document_id))

# VS

document_response = await client.get_document_async(GetDocumentParams(document_id=document_id))
```

Other than that, nothing changes and the interfaces are the same.

# Responses

The SDK returns a `PDFGateDocument` for all processing endpoints:

- `generate_pdf`
- `flatten_pdf`
- `compress_pdf`
- `watermark_pdf`
- `protect_pdf`
- `upload_file`

To get raw PDF bytes, call `get_file` with a document ID.

# Webhook Verification

Use `verify_signature` with the raw request body and the
`x-pdfgate-signature` header value received from PDFGate:

```python
import json

from pdfgate import verify_signature


verify_signature(
    secret="whsecret_...",
    signature_header=request.headers["x-pdfgate-signature"],
    payload=request_body,
)

event = json.loads(request_body)
```

# Examples

## Generate PDF

```python
params = GeneratePDFParams(html="<h1>Hello from PDFGate!</h1>")
document = client.generate_pdf(params)
print(document["id"])
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
  f.write(file_content)
```

## Upload a PDF file

```python
file_param = FileParam.pdf(name="input.pdf", data=pdf_file_bytes)
document_response = client.upload_file(UploadFileParams(file=file_param))
```

If both `file` and `url` are provided, `file` is prioritized and the request is sent as multipart.

## Flatten a PDF (make form-fields non-editable)

```python
flatten_pdf_params = FlattenPDFParams(
    document_id=document_id
)
flattened_document = client.flatten_pdf(flatten_pdf_params)
```

## Compress a PDF

```python
compress_pdf_params = CompressPDFParams(
    document_id=document_id
)
response = client.compress_pdf(compress_pdf_params)
```

## Watermark a PDF

```python
watermark_pdf_params = WatermarkPDFParams(
    document_id=document_id,
    type=WatermarkType.IMAGE,
    watermark=FileParam(name="watermark.jpg", data=jpg_file),
)
watermarked_pdf = client.watermark_pdf(watermark_pdf_params)
```

## Protect (encrypt) a PDF

```python
protect_pdf_params = ProtectPDFParams(
    document_id=document_id,
    user_password=str(uuid.uuid4()),
    owner_password=str(uuid.uuid4()),
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
    html=html_form, enable_form_fields=True
)
document_response = cast(PDFGateDocument, client.generate_pdf(generate_pdf_params))
document_id = cast(str, document_response.get("id"))

extract_form_params = ExtractPDFFormDataParams(document_id=document_id)
response = cast(dict[str, Any], client.extract_pdf_form_data(extract_form_params))
```

# Development

Before doing anything, install [pre-commit](https://pre-commit.com/) by running:

```sh
hatch run dev:pre-commit install
```

This will run several checks every time you try to `git commit` including:

- linting and formatting with `Ruff`
- type checking with `mypy`

If you are on VS Code, it's recommended to install the `Ruff` extension so you'll get formatting on the fly.

Hatch is used as a build system and for dependency management, so all main actions are configured to be run with Hatch.

## Tests

Unit tests:
```sh
hatch run test:test
```

Acceptance tests hit the PDFGate API so they are slower, and require an API key that is expected to be set as an env var named `PDFGATE_API_KEY`. You can set it on your Bash/zsh/fish profile or inline as in:

```sh
PDFGATE_API_KEY="test_123" hatch run test:test_acceptance
```

## Manually run Ruff

Linting:
```sh
hatch run dev:lint
```

Formatting:
```sh
hatch run dev:ruff format .
```

## Type checking

Manually mypy for type checking:

```sh
hatch run dev:check
```

## Docs

Docs are build using [MkDocs](https://www.mkdocs.org/), they live in the `docs/` folder, and in the code. If you make any changes, and would like to see them live before publishing them, spin up a server locally with:

```sh
hatch run docs:serve
```

Changes to `docs/**` and `mkdocs.yml` trigger a new deployment of the docs site. If you change the code's documentation and want to manually update the docs site you can do it from the _Actions_ tab of the repo or by running:

```sh
hatch run docs:mkdocs gh-deploy
```

# Support

📧 Email: support@pdfgate.com<br>
📘 Docs: https://pdfgate.com/documentation

## License

`pdfgate-sdk-python` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
