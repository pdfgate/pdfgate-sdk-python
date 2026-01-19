"""pdfgate_sdk_python.pdfgate

Client for interacting with the PDFGate API.
"""

from typing import Any, Union, cast

from pdfgate_sdk_python.http_client import PDFGateHTTPClientAsync, PDFGateHTTPClientSync
from pdfgate_sdk_python.request_builder import RequestBuilder, get_domain_from_api_key
from pdfgate_sdk_python.response_builder import ResponseBuilder

from .errors import ParamsValidationError
from .params import (
    CompressPDFParams,
    ExtractPDFFormDataParams,
    FlattenPDFParams,
    GeneratePDFParams,
    GetDocumentParams,
    GetFileParams,
    ProtectPDFParams,
    WatermarkPDFParams,
)
from .responses import PDFGateDocument


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
        result = cast(
            PDFGateDocument, ResponseBuilder.build_response(response, json=True)
        )

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
        result = cast(
            PDFGateDocument, ResponseBuilder.build_response(response, json=True)
        )

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

    def generate_pdf(self, params: GeneratePDFParams) -> Union[bytes, PDFGateDocument]:
        """Generate a PDF from a URL or raw HTML.

        Returns:
            Either the raw PDF bytes or a `PDFGateDocument` parsed from the JSON response.
        """
        if not params.html and not params.url:
            raise ParamsValidationError(
                "Either the 'html' or 'url' parameters must be provided to generate a PDF."
            )

        request = self.request_builder.build_generate_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    async def generate_pdf_async(
        self, params: GeneratePDFParams
    ) -> Union[bytes, PDFGateDocument]:
        """Generate a PDF from a URL or raw HTML.

        Returns:
            Either the raw PDF bytes or a `PDFGateDocument` parsed from the JSON response.
        """
        if not params.html and not params.url:
            raise ParamsValidationError(
                "Either the 'html' or 'url' parameters must be provided to generate a PDF."
            )

        request = self.request_builder.build_generate_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    def flatten_pdf(self, params: FlattenPDFParams) -> Union[bytes, PDFGateDocument]:
        """Flatten an interactive PDF into a static, non-editable PDF.

        Args:
            params: Either a `FlattenPDFByDocumentIdParams` or
                `FlattenPDFBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_flatten_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    async def flatten_pdf_async(
        self, params: FlattenPDFParams
    ) -> Union[bytes, PDFGateDocument]:
        """Flatten an interactive PDF into a static, non-editable PDF.

        Args:
            params: Either a `FlattenPDFByDocumentIdParams` or
                `FlattenPDFBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_flatten_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    def extract_pdf_form_data(self, params: ExtractPDFFormDataParams) -> Any:
        """Extract form field data from a fillable PDF and return it as JSON.

        Args:
            params: Either a `ExtractPDFFormDataByDocumentIdParams` or
                `ExtractPDFFormDataBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            JSON object mapping form field names to their values.
        """
        request = self.request_builder.build_extract_pdf_form_data(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_response(response, json=True)

        return result

    async def extract_pdf_form_data_async(
        self, params: ExtractPDFFormDataParams
    ) -> Any:
        """Extract form field data from a fillable PDF and return it as JSON.

        Args:
            params: Either a `ExtractPDFFormDataByDocumentIdParams` or
                `ExtractPDFFormDataBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            JSON object mapping form field names to their values.
        """
        request = self.request_builder.build_extract_pdf_form_data(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_response(response, json=True)

        return result

    def protect_pdf(self, params: ProtectPDFParams) -> Union[bytes, PDFGateDocument]:
        """Protect a PDF using encryption + optional permission restrictions.

        Security options highlights:
            - `algorithm`: `"AES256"` (default) or `"AES128"`.
            - `user_password`: password required to open the PDF (optional).
            - `owner_password`: full control password; required in some cases (e.g., AES256 with `user_password`).
            - Restrictions: `disable_print`, `disable_copy`, `disable_editing`.
            - `encrypt_metadata`: whether PDF metadata is encrypted (default `False`).

        Args:
            params: Either a `ProtectPDFByDocumentIdParams` or
                `ProtectPDFBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_protect_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    async def protect_pdf_async(
        self, params: ProtectPDFParams
    ) -> Union[bytes, PDFGateDocument]:
        """Protect a PDF using encryption + optional permission restrictions.

        Security options highlights:
            - `algorithm`: `"AES256"` (default) or `"AES128"`.
            - `user_password`: password required to open the PDF (optional).
            - `owner_password`: full control password; required in some cases (e.g., AES256 with `user_password`).
            - Restrictions: `disable_print`, `disable_copy`, `disable_editing`.
            - `encrypt_metadata`: whether PDF metadata is encrypted (default `False`).

        Args:
            params: Either a `ProtectPDFByDocumentIdParams` or
                `ProtectPDFBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_protect_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    def compress_pdf(self, params: CompressPDFParams) -> Union[bytes, PDFGateDocument]:
        """Compress a PDF document to reduce its size without changing its visual content.

        Args:
            params: Either a `CompressPDFByDocumentIdParams` or
                `CompressPDFBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_compress_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    async def compress_pdf_async(
        self, params: CompressPDFParams
    ) -> Union[bytes, PDFGateDocument]:
        """Compress a PDF document to reduce its size without changing its visual content.

        Args:
            params: Either a `CompressPDFByDocumentIdParams` or
                `CompressPDFBinaryParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_compress_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    def watermark_pdf(self, params: WatermarkPDFParams) -> Any:
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
            params: Either a `WatermarkPDFByDocumentIdParams` or
                `WatermarkPDFByFileParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_watermark_pdf(params)
        response = self.sync_client.try_make_request(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result

    async def watermark_pdf_async(self, params: WatermarkPDFParams) -> Any:
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
            params: Either a `WatermarkPDFByDocumentIdParams` or
                `WatermarkPDFByFileParams` instance depending on whether the file
                is provided as a document ID or raw binary data.

        Returns:
            Depending on the `json_response` flag in `params`, this method either
            returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        request = self.request_builder.build_watermark_pdf(params)
        response = await self.async_client.try_make_request_async(request)
        result = ResponseBuilder.build_response(response, json=params.json_response)

        return result
