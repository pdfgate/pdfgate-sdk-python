"""Request construction utilities for PDFGate API calls."""

from dataclasses import asdict, dataclass
from datetime import timedelta
import mimetypes
from typing import Any
import httpx
from pdfgate.config import Config
from pdfgate.dict_keys_converter import convert_snake_keys_to_camel, remove_none_values
from pdfgate.errors import PDFGateError
from pdfgate.params import (
    AddFormFieldsParams,
    CompressPDFParams,
    CreateEnvelopeParams,
    CreateWebhookParams,
    DeleteDocumentParams,
    DeleteWebhookParams,
    ExtractPDFFormDataParams,
    FileParam,
    FlattenPDFParams,
    GeneratePDFParams,
    GetDocumentParams,
    GetEnvelopeParams,
    GetWebhookParams,
    PDFGateParams,
    ProtectPDFParams,
    SendEnvelopeParams,
    VoidEnvelopeParams,
    DeleteEnvelopeParams,
    UploadFileParams,
    WatermarkType,
    WatermarkPDFParams,
)
from pdfgate.url_builder import URLBuilder

FormDataFileParam = tuple[str, bytes, str]


def get_domain_from_api_key(api_key: str) -> str:
    """Return the API domain corresponding to an API key.

    Args:
        api_key:
            API key string that should start with 'live_' or 'test_'.

    Returns:
        The domain (URL) for the API (production or sandbox).

    Raises:
        PDFGateError: If the API key format is invalid.
    """
    if api_key.startswith("live_"):
        return Config.PRODUCTION_API_DOMAIN
    elif api_key.startswith("test_"):
        return Config.SANDBOX_API_DOMAIN
    else:
        raise PDFGateError(
            "Invalid API key format. Expected to start with 'live_' or 'test_'."
        )


def pdfgate_params_to_params_dict(instance: PDFGateParams) -> dict[str, Any]:
    """Convert a params dataclass into a JSON-ready dict."""
    return convert_snake_keys_to_camel(remove_none_values(asdict(instance)))  # type: ignore[return-value]


@dataclass
class PDFGateRequest:
    """Container for an HTTP request and its timeout."""

    request: httpx.Request
    timeout: int = int(
        timedelta(seconds=Config.DEFAULT_TIMEOUT_SECONDS).total_seconds()
    )


class RequestBuilder:
    """Build HTTP requests for PDFGate endpoints."""

    def __init__(self, api_key: str):
        domain = get_domain_from_api_key(api_key)
        self.url_builder = URLBuilder(domain)
        self.api_key = api_key

    def get_headers(self) -> dict[str, str]:
        """Return the authorization header for API calls."""
        return {"Authorization": f"Bearer {self.api_key}"}

    def _get_request(self, url: str, params: dict[str, Any] = {}) -> httpx.Request:
        """Create a GET request with standard headers."""
        return httpx.Request("GET", url=url, headers=self.get_headers(), params=params)

    def _json_post_request(self, url: str, json: dict[str, Any]) -> httpx.Request:
        """Create a JSON POST request with standard headers."""
        return httpx.Request("POST", url=url, headers=self.get_headers(), json=json)

    def _multipart_post_request(
        self, url: str, data: dict[str, Any] = {}, files: dict[str, Any] = {}
    ) -> httpx.Request:
        """Create a multipart POST request with standard headers."""
        return httpx.Request(
            "POST", url=url, headers=self.get_headers(), data=data, files=files
        )

    def _delete_request(self, url: str) -> httpx.Request:
        """Create a DELETE request with standard headers."""
        return httpx.Request("DELETE", url=url, headers=self.get_headers())

    def _build_file_param(
        self, file_param: FileParam, key: str
    ) -> dict[str, FormDataFileParam]:
        """Build a file parameter for multipart requests."""
        if file_param.type is None:
            mime_type, _encoding = mimetypes.guess_type(file_param.name)
            mime_type = mime_type or "application/octet-stream"
        else:
            mime_type = file_param.type or "application/octet-stream"

        return {key: (file_param.name, file_param.data, mime_type)}

    def build_get_file(self, document_id: str) -> PDFGateRequest:
        """Build a request to download a document's file content."""
        url = self.url_builder.get_file_url(document_id)
        request = self._get_request(url)

        return PDFGateRequest(request=request)

    def build_get_document(self, params: GetDocumentParams) -> PDFGateRequest:
        """Build a request to fetch a document's metadata."""
        params_dict: dict[str, int] = {}
        if params.pre_signed_url_expires_in is not None:
            params_dict["preSignedUrlExpiresIn"] = params.pre_signed_url_expires_in

        url = self.url_builder.get_document_url(params.document_id)
        request = self._get_request(url, params_dict)

        return PDFGateRequest(request=request)

    def build_generate_pdf(self, params: GeneratePDFParams) -> PDFGateRequest:
        """Build a request to generate a PDF from HTML or URL."""
        url = self.url_builder.generate_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        params_without_nulls["jsonResponse"] = True
        request = self._json_post_request(url, json=params_without_nulls)
        timeout = int(
            timedelta(minutes=Config.GENERATE_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_flatten_pdf(self, params: FlattenPDFParams) -> PDFGateRequest:
        """Build a request to flatten a PDF by document ID."""
        url = self.url_builder.flatten_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        params_without_nulls["jsonResponse"] = True

        request = self._json_post_request(url, json=params_without_nulls)
        timeout = int(
            timedelta(minutes=Config.FLATTEN_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_add_form_fields(self, params: AddFormFieldsParams) -> PDFGateRequest:
        """Build a request to add form fields to a PDF by document ID."""
        url = self.url_builder.add_form_fields_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        # ``field_overrides`` is keyed by the user's actual PDF field names, so its
        # top-level keys must be preserved verbatim (only the override options are
        # converted to camelCase).
        if params.field_overrides is not None:
            params_without_nulls["fieldOverrides"] = {
                field_name: convert_snake_keys_to_camel(
                    remove_none_values(asdict(override))
                )
                for field_name, override in params.field_overrides.items()
            }
        params_without_nulls["jsonResponse"] = True

        request = self._json_post_request(url, json=params_without_nulls)
        timeout = int(
            timedelta(minutes=Config.FLATTEN_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_delete_document(self, params: DeleteDocumentParams) -> PDFGateRequest:
        """Build a request to delete a stored document by ID."""
        url = self.url_builder.get_document_url(params.document_id)
        request = self._delete_request(url)

        return PDFGateRequest(request=request)

    def build_extract_pdf_form_data(
        self, params: ExtractPDFFormDataParams
    ) -> PDFGateRequest:
        """Build a request to extract PDF form data."""
        url = self.url_builder.extract_pdf_form_data_url()
        params_dict = {"documentId": params.document_id}
        request = self._json_post_request(url, json=params_dict)

        return PDFGateRequest(request=request)

    def build_protect_pdf(self, params: ProtectPDFParams) -> PDFGateRequest:
        """Build a request to encrypt a PDF by document ID."""
        url = self.url_builder.protect_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        params_without_nulls["jsonResponse"] = True
        request = self._json_post_request(url=url, json=params_without_nulls)
        timeout = int(
            timedelta(minutes=Config.PROTECT_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_compress_pdf(self, params: CompressPDFParams) -> PDFGateRequest:
        """Build a request to compress a PDF by document ID."""
        url = self.url_builder.compress_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        params_without_nulls["jsonResponse"] = True
        request = self._json_post_request(url=url, json=params_without_nulls)
        timeout = int(
            timedelta(minutes=Config.COMPRESS_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_watermark_pdf(self, params: WatermarkPDFParams) -> PDFGateRequest:
        """Build a request to watermark a PDF by document ID."""
        url = self.url_builder.watermark_pdf_url()
        params_dict = pdfgate_params_to_params_dict(params)
        params_dict["jsonResponse"] = True

        files: dict[str, FormDataFileParam] = {}
        if params.type == WatermarkType.IMAGE and params.watermark is not None:
            files.update(
                self._build_file_param(params_dict.pop("watermark"), "watermark")
            )
        # A custom font file (TTF/OTF) may be uploaded to override the built-in font.
        if params.font_file is not None:
            files.update(
                self._build_file_param(params_dict.pop("fontFile"), "fontFile")
            )

        if files:
            request = self._multipart_post_request(
                url=url, data=params_dict, files=files
            )
        else:
            request = self._json_post_request(url=url, json=params_dict)
        timeout = int(
            timedelta(minutes=Config.WATERMARK_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_create_envelope(self, params: CreateEnvelopeParams) -> PDFGateRequest:
        """Build a request to create a signing envelope."""
        url = self.url_builder.envelope_url()
        body = pdfgate_params_to_params_dict(params)
        request = self._json_post_request(url=url, json=body)
        return PDFGateRequest(request=request)

    def build_get_envelope(self, params: GetEnvelopeParams) -> PDFGateRequest:
        """Build a request to fetch a signing envelope."""
        url = self.url_builder.get_envelope_url(params.envelope_id)
        request = self._get_request(url=url)
        return PDFGateRequest(request=request)

    def build_send_envelope(self, params: SendEnvelopeParams) -> PDFGateRequest:
        """Build a request to send a signing envelope to its recipients."""
        url = self.url_builder.send_envelope_url(params.envelope_id)
        request = self._json_post_request(url=url, json={})
        return PDFGateRequest(request=request)

    def build_void_envelope(self, params: VoidEnvelopeParams) -> PDFGateRequest:
        """Build a request to void (cancel) a signing envelope."""
        url = self.url_builder.void_envelope_url(params.envelope_id)
        body = {"reason": params.reason} if params.reason else {}
        request = self._json_post_request(url=url, json=body)
        return PDFGateRequest(request=request)

    def build_delete_envelope(self, params: DeleteEnvelopeParams) -> PDFGateRequest:
        """Build a request to permanently delete an envelope by ID."""
        url = self.url_builder.get_envelope_url(params.envelope_id)
        request = self._delete_request(url)
        return PDFGateRequest(request=request)

    def build_create_webhook(self, params: CreateWebhookParams) -> PDFGateRequest:
        """Build a request to register a webhook endpoint."""
        url = self.url_builder.webhook_url()
        body = pdfgate_params_to_params_dict(params)
        request = self._json_post_request(url=url, json=body)
        return PDFGateRequest(request=request)

    def build_get_webhook(self, params: GetWebhookParams) -> PDFGateRequest:
        """Build a request to fetch a webhook by ID."""
        url = self.url_builder.get_webhook_url(params.webhook_id)
        request = self._get_request(url=url)
        return PDFGateRequest(request=request)

    def build_delete_webhook(self, params: DeleteWebhookParams) -> PDFGateRequest:
        """Build a request to delete a webhook by ID."""
        url = self.url_builder.get_webhook_url(params.webhook_id)
        request = self._delete_request(url)
        return PDFGateRequest(request=request)

    def build_upload_file(self, params: UploadFileParams) -> PDFGateRequest:
        """Build a request to upload a PDF file to the PDFGate storage"""
        url = self.url_builder.upload_file_url()
        params_dict = pdfgate_params_to_params_dict(params)
        if params.file:
            upload_file_param = self._build_file_param(params_dict.pop("file"), "file")
            request = self._multipart_post_request(
                url=url, data=params_dict, files=upload_file_param
            )
        else:
            request = self._json_post_request(url=url, json=params_dict)

        return PDFGateRequest(request=request)
