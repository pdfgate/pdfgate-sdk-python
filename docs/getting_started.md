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

To get raw PDF bytes, call `get_file` with a document ID.

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
