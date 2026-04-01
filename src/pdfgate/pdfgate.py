from typing import Any

from pdfgate.http_client import PDFGateHTTPClientAsync, PDFGateHTTPClientSync
from pdfgate.request_builder import RequestBuilder, get_domain_from_api_key
from pdfgate.response_builder import ResponseBuilder

from .errors import ParamsValidationError
from .params import (
    CompressPDFParams,
    CreateEnvelopeParams,
    ExtractPDFFormDataParams,
    FlattenPDFParams,
    GeneratePDFParams,
    GetDocumentParams,
    GetEnvelopeParams,
    GetFileParams,
    ProtectPDFParams,
    SendEnvelopeParams,
    UploadFileParams,
    WatermarkPDFParams,
)
from .responses import PDFGateDocument, PDFGateEnvelope


class PDFGate:
    """Client for the PDFGate API.

    Attributes:
        api_key (str):
            API key used for authentication.
        domain (str):
            Base API domain derived from the API key.
        request_builder (RequestBuilder):
            Builds HTTP requests for the API from parameter objects.
        sync_client (PDFGateHTTPClientSync):
            Synchronous HTTP client that handles HTTP errors.
        async_client (PDFGateHTTPClientAsync):
            Asynchronous HTTP client that handles HTTP errors.
    """

    def __init__(self, api_key: str):
        """Initialize a PDFGate client.

        Args:
            api_key: The API key to use. Must start with 'live_' or 'test_'.

        Raises:
            PDFGateError: If the API key is invalid.
        """
        self.domain = get_domain_from_api_key(api_key)
        self.api_key = api_key
        self.request_builder = RequestBuilder(api_key=api_key)
        self.sync_client = PDFGateHTTPClientSync(api_key=api_key)
        self.async_client = PDFGateHTTPClientAsync(api_key=api_key)

    def get_document(self, params: GetDocumentParams) -> PDFGateDocument:
        """Retrieve a stored document’s metadata (and optionally a fresh pre-signed download URL).

        Returns:
            A `PDFGateDocument` parsed from the JSON response.

        Raises:
            PDFGateError: If the HTTP request fails (including non-2xx responses) or if
                there is a network/connection error. The error includes status code
                and message when available.
        """
        request = self.request_builder.build_get_document(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    async def get_document_async(self, params: GetDocumentParams) -> PDFGateDocument:
        """Retrieve a stored document’s metadata (and optionally a fresh pre-signed download URL).

        Returns:
            A `PDFGateDocument` parsed from the JSON response.

        Raises:
            PDFGateError: If the HTTP request fails (including non-2xx responses) or if
                there is a network/connection error. The error includes status code
                and message when available.
        """
        request = self.request_builder.build_get_document(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def get_file(self, params: GetFileParams) -> bytes:
        """Download a raw PDF file by its document ID.

        Important: Accessing stored generated files requires enabling
        “Save files” in the PDFGate Dashboard settings (disabled by default).

        Returns:
            The raw bytes of the file.
        """
        request = self.request_builder.build_get_file(params.document_id)
        response = self.sync_client.try_make_request(request=request)

        return response.content

    async def get_file_async(self, params: GetFileParams) -> bytes:
        """Download a raw PDF file by its document ID.

        Important: Accessing stored generated files requires enabling
        “Save files” in the PDFGate Dashboard settings (disabled by default).

        Returns:
            The raw bytes of the file.
        """
        request = self.request_builder.build_get_file(params.document_id)
        response = await self.async_client.try_make_request_async(request=request)

        return response.content

    def generate_pdf(self, params: GeneratePDFParams) -> PDFGateDocument:
        """Generate a PDF from a URL or raw HTML.

        Returns:
            A `PDFGateDocument` parsed from the JSON response.
        """
        if not params.html and not params.url:
            raise ParamsValidationError(
                "Either the 'html' or 'url' parameters must be provided to generate a PDF."
            )

        request = self.request_builder.build_generate_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    async def generate_pdf_async(self, params: GeneratePDFParams) -> PDFGateDocument:
        """Generate a PDF from a URL or raw HTML.

        Returns:
            A `PDFGateDocument` parsed from the JSON response.
        """
        if not params.html and not params.url:
            raise ParamsValidationError(
                "Either the 'html' or 'url' parameters must be provided to generate a PDF."
            )

        request = self.request_builder.build_generate_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def flatten_pdf(self, params: FlattenPDFParams) -> PDFGateDocument:
        """Flatten an interactive PDF into a static, non-editable PDF.

        Args:
            params: A `FlattenPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_flatten_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    async def flatten_pdf_async(self, params: FlattenPDFParams) -> PDFGateDocument:
        """Flatten an interactive PDF into a static, non-editable PDF.

        Args:
            params: A `FlattenPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_flatten_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def extract_pdf_form_data(self, params: ExtractPDFFormDataParams) -> Any:
        """Extract form field data from a fillable PDF and return it as JSON.

        Args:
            params: A `ExtractPDFFormDataParams` instance.

        Returns:
            JSON object mapping form field names to their values.
        """
        request = self.request_builder.build_extract_pdf_form_data(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_json_response(response)

        return result

    async def extract_pdf_form_data_async(
        self, params: ExtractPDFFormDataParams
    ) -> Any:
        """Extract form field data from a fillable PDF and return it as JSON.

        Args:
            params: A `ExtractPDFFormDataParams` instance.

        Returns:
            JSON object mapping form field names to their values.
        """
        request = self.request_builder.build_extract_pdf_form_data(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_json_response(response)

        return result

    def protect_pdf(self, params: ProtectPDFParams) -> PDFGateDocument:
        """Protect a PDF using encryption + optional permission restrictions.

        Security options highlights:
            - `algorithm`: `"AES256"` (default) or `"AES128"`.
            - `user_password`: password required to open the PDF (optional).
            - `owner_password`: full control password; required in some cases (e.g., AES256 with `user_password`).
            - Restrictions: `disable_print`, `disable_copy`, `disable_editing`.
            - `encrypt_metadata`: whether PDF metadata is encrypted (default `False`).

        Args:
            params: A `ProtectPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_protect_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    async def protect_pdf_async(self, params: ProtectPDFParams) -> PDFGateDocument:
        """Protect a PDF using encryption + optional permission restrictions.

        Security options highlights:
            - `algorithm`: `"AES256"` (default) or `"AES128"`.
            - `user_password`: password required to open the PDF (optional).
            - `owner_password`: full control password; required in some cases (e.g., AES256 with `user_password`).
            - Restrictions: `disable_print`, `disable_copy`, `disable_editing`.
            - `encrypt_metadata`: whether PDF metadata is encrypted (default `False`).

        Args:
            params: A `ProtectPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_protect_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def compress_pdf(self, params: CompressPDFParams) -> PDFGateDocument:
        """Compress a PDF document to reduce its size without changing its visual content.

        Args:
            params: A `CompressPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_compress_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    async def compress_pdf_async(self, params: CompressPDFParams) -> PDFGateDocument:
        """Compress a PDF document to reduce its size without changing its visual content.

        Args:
            params: A `CompressPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_compress_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def watermark_pdf(self, params: WatermarkPDFParams) -> PDFGateDocument:
        """Apply a text or image watermark to a PDF.

        Watermark configuration highlights:
            - `type` is required: `"text"` or `"image"`.
            - For text watermarks: `text` required when `type="text"`.
            - For image watermarks: upload `watermark` image file (`.png`, `.jpg`, `.jpeg`).
            - Optional: `font` (standard PDF fonts), `fontFile`
            (`.ttf`/`.otf` overrides `font`), `fontSize`, `fontColor`,
            `opacity` (0..1), `xPosition`, `yPosition`, `imageWidth`, `imageHeight`,
            `rotate` (0..360).

        Args:
            params: A `WatermarkPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_watermark_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    async def watermark_pdf_async(self, params: WatermarkPDFParams) -> PDFGateDocument:
        """Apply a text or image watermark to a PDF.

        Watermark configuration highlights:
            - `type` is required: `"text"` or `"image"`.
            - For text watermarks: `text` required when `type="text"`.
            - For image watermarks: upload `watermark` image file (`.png`, `.jpg`, `.jpeg`).
            - Optional: `font` (standard PDF fonts), `fontFile`
            (`.ttf`/`.otf` overrides `font`), `fontSize`, `fontColor`,
            `opacity` (0..1), `xPosition`, `yPosition`, `imageWidth`, `imageHeight`,
            `rotate` (0..360).

        Args:
            params: A `WatermarkPDFParams` instance.

        Returns:
            A `PDFGateDocument` instance.
        """
        request = self.request_builder.build_watermark_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def upload_file(self, params: UploadFileParams) -> PDFGateDocument:
        """Upload a raw PDF file.

        Important: Accessing stored generated files requires enabling
        “Save files” in the PDFGate Dashboard settings (disabled by default).

        Args:
            params: Upload parameters. When both `file` and `url` are provided,
                `file` is prioritized and the request is sent as multipart.

        Returns:
            The metadata of the file so you can reference it on further calls.
        """
        request = self.request_builder.build_upload_file(params)
        response = self.sync_client.try_make_request(request=request)
        result = ResponseBuilder.build_document_response(response)

        return result

    def create_envelope(self, params: CreateEnvelopeParams) -> PDFGateEnvelope:
        """Create a signing envelope from one or more source documents.

        Args:
            params: Envelope creation parameters including documents, recipients,
                requester name, and optional metadata.

        Returns:
            The created envelope in ``created`` status.
        """
        request = self.request_builder.build_create_envelope(params)
        response = self.sync_client.try_make_request(request=request)
        return ResponseBuilder.build_envelope_response(response)

    def get_envelope(self, params: GetEnvelopeParams) -> PDFGateEnvelope:
        """Retrieve the current state of a signing envelope.

        Args:
            params: Envelope lookup parameters including the envelope ID.

        Returns:
            The current envelope state returned by the API.
        """
        request = self.request_builder.build_get_envelope(params)
        response = self.sync_client.try_make_request(request=request)
        return ResponseBuilder.build_envelope_response(response)

    async def create_envelope_async(
        self, params: CreateEnvelopeParams
    ) -> PDFGateEnvelope:
        """Create a signing envelope from one or more source documents.

        Args:
            params: Envelope creation parameters including documents, recipients,
                requester name, and optional metadata.

        Returns:
            The created envelope in ``created`` status.
        """
        request = self.request_builder.build_create_envelope(params)
        response = await self.async_client.try_make_request_async(request=request)
        return ResponseBuilder.build_envelope_response(response)

    async def get_envelope_async(self, params: GetEnvelopeParams) -> PDFGateEnvelope:
        """Retrieve the current state of a signing envelope.

        Args:
            params: Envelope lookup parameters including the envelope ID.

        Returns:
            The current envelope state returned by the API.
        """
        request = self.request_builder.build_get_envelope(params)
        response = await self.async_client.try_make_request_async(request=request)
        return ResponseBuilder.build_envelope_response(response)

    def send_envelope(self, params: SendEnvelopeParams) -> PDFGateEnvelope:
        """Send a signing envelope to all configured recipients.

        Args:
            params: Envelope send parameters including the envelope ID.

        Returns:
            The updated envelope in ``in_progress`` or a later status.
        """
        request = self.request_builder.build_send_envelope(params)
        response = self.sync_client.try_make_request(request=request)
        return ResponseBuilder.build_envelope_response(response)

    async def send_envelope_async(self, params: SendEnvelopeParams) -> PDFGateEnvelope:
        """Send a signing envelope to all configured recipients.

        Args:
            params: Envelope send parameters including the envelope ID.

        Returns:
            The updated envelope in ``in_progress`` or a later status.
        """
        request = self.request_builder.build_send_envelope(params)
        response = await self.async_client.try_make_request_async(request=request)
        return ResponseBuilder.build_envelope_response(response)

    async def upload_file_async(self, params: UploadFileParams) -> PDFGateDocument:
        """Upload a raw PDF file.

        Important: Accessing stored generated files requires enabling
        “Save files” in the PDFGate Dashboard settings (disabled by default).

        Args:
            params: Upload parameters. When both `file` and `url` are provided,
                `file` is prioritized and the request is sent as multipart.

        Returns:
            The metadata of the file so you can reference it on further calls.
        """
        request = self.request_builder.build_upload_file(params)
        response = await self.async_client.try_make_request_async(request=request)
        result = ResponseBuilder.build_document_response(response)

        return result
