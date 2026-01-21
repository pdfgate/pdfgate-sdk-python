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
pdf = client.generate_pdf(params)

with open("output.pdf", "wb") as f:
  f.write(pdf)
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
watermark_pdf_params = WatermarkPDFByFileParams(
    file=FileParam(name="input.pdf", data=pdf_file),
    type=WatermarkType.IMAGE,
    watermark=FileParam(name="watermark.jpg", data=jpg_file),
)
watermarked_pdf = cast(PDFGateDocument, client.watermark_pdf(watermark_pdf_params))
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
