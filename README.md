# PDFGate's official Python SDK

The PDFGate Python SDK provides convenient access to the PDFGate API from applications written in Python. It includes typed parameter objects, synchronous and asynchronous clients, response helpers, webhook management, and webhook signature verification for common PDF generation, processing, and signing workflows.

📘 Documentation: https://pdfgate.com/documentation<br>
🔑 Dashboard & API keys: https://dashboard.pdfgate.com

## pdfgate

[![PyPI - Version](https://img.shields.io/pypi/v/pdfgate.svg)](https://pypi.org/project/pdfgate)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pdfgate.svg)](https://pypi.org/project/pdfgate)


## Table of Contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Sync & Async](#sync--async)
- [Responses](#responses)
- [Managing Webhooks](#managing-webhooks)
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


client = PDFGate(api_key=os.environ["PDFGATE_API_KEY"])
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
- `add_form_fields`
- `compress_pdf`
- `watermark_pdf`
- `protect_pdf`
- `upload_file`

To get raw PDF bytes, call `get_file` with a document ID.
`delete_document` returns `None`.

Webhook management methods (`create_webhook`, `get_webhook`) return a
`WebhookResponse`; `delete_webhook` returns `None`.

Every method has an `async` counterpart (e.g. `add_form_fields_async`,
`delete_document_async`, `create_webhook_async`).

# Managing Webhooks

Register, retrieve, and delete webhook endpoints that receive PDFGate event
notifications. The `secret` returned by `create_webhook` is shown only once —
store it to verify incoming payloads.

```python
from pdfgate import (
    CreateWebhookParams,
    DeleteWebhookParams,
    GetWebhookParams,
    WebhookEventType,
)

created = client.create_webhook(
    CreateWebhookParams(
        url="https://example.com/pdfgate-callback",
        event_types=[
            WebhookEventType.ENVELOPE_COMPLETED,
            WebhookEventType.ENVELOPE_SENT,
        ],
        description="Production signing events",
    )
)
webhook_id = created["id"]
secret = created["secret"]

fetched = client.get_webhook(GetWebhookParams(webhook_id=webhook_id))

client.delete_webhook(DeleteWebhookParams(webhook_id=webhook_id))
```

The subscribable events are exposed via `WebhookEventType`:
`ENVELOPE_SENT`, `ENVELOPE_COMPLETED`, `ENVELOPE_EXPIRED`, and
`ENVELOPE_DOCUMENT_COMPLETED`. The webhook URL must be publicly accessible
(localhost is not supported).

# Webhook Verification

Use `verify_signature` with the raw request body and the
`x-pdfgate-signature` header value received from PDFGate:

```python
from pdfgate import verify_signature


event = verify_signature(
    secret="whsecret_...",
    signature_header=request.headers["x-pdfgate-signature"],
    payload=request_body,
)

event_id = event["event_id"]
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

print(document_response["id"])
print(document_response["status"])
print(document_response.get("file_url"))
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
    document_id=document_id,
    # Optional: flatten only these fields and leave the rest interactive.
    # Omit field_names to flatten the whole document.
    field_names=["signature", "date"],
)
flattened_document = client.flatten_pdf(flatten_pdf_params)
```

## Add form fields to a PDF

```python
from pdfgate import (
    AddFormFieldsParams,
    DocumentFieldType,
    FieldOverride,
    ManualFormField,
)

response = client.add_form_fields(
    AddFormFieldsParams(
        document_id=document_id,
        # Customize placeholder fields detected in the PDF, keyed by field name.
        field_overrides={"signature": FieldOverride(role="signer", optional=False)},
        # Or place fields at explicit positions on a given page.
        fields=[
            ManualFormField(
                name="signed_on",
                type=DocumentFieldType.DATE,
                page=1,
                x=100,
                y=650,
                width=160,
                height=24,
            )
        ],
    )
)
```

## Delete a stored document

```python
from pdfgate import DeleteDocumentParams

client.delete_document(DeleteDocumentParams(document_id=document_id))
```

A document referenced by a draft or in-progress envelope cannot be deleted until
those envelopes are completed or expired.

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
    user_password="user-password",
    owner_password="owner-password",
)
response = client.protect_pdf(protect_pdf_params)
```

## Extract PDF form fields values

```python
html_form = """
<form>
    <input type="text" name="first_name" value="John" />
    <input type="text" name="last_name" value="Doe" />
</form>
"""
generate_pdf_params = GeneratePDFParams(
    html=html_form, enable_form_fields=True
)
document_response = client.generate_pdf(generate_pdf_params)
document_id = document_response["id"]

extract_form_params = ExtractPDFFormDataParams(document_id=document_id)
response = client.extract_pdf_form_data(extract_form_params)
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

Run mypy manually:

```sh
hatch run dev:check
```

## Docs

Docs are built using [MkDocs](https://www.mkdocs.org/), they live in the `docs/` folder, and in the code. If you make any changes, and would like to see them live before publishing them, spin up a server locally with:

```sh
hatch run docs:serve
```

Changes to `docs/**` and `mkdocs.yml` trigger a new deployment of the docs site. If you change the code's documentation and want to manually update the docs site you can do it from the _Actions_ tab of the repo or by running:

```sh
hatch run docs:mkdocs gh-deploy
```

## Support

For support, contact [support@pdfgate.com](mailto:support@pdfgate.com).

## License

`pdfgate` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
