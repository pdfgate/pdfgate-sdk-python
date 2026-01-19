"""Request construction utilities for PDFGate API calls."""

from dataclasses import asdict, dataclass
from datetime import timedelta
from enum import Enum
from typing import Any
import httpx
from pdfgate_sdk_python.config import Config
from pdfgate_sdk_python.dict_keys_converter import snake_to_camel
from pdfgate_sdk_python.errors import PDFGateError
from pdfgate_sdk_python.params import (
    CompressPDFByDocumentIdParams,
    CompressPDFParams,
    ExtractPDFFormDataByDocumentIdParams,
    ExtractPDFFormDataParams,
    FlattenPDFByFileParams,
    FlattenPDFParams,
    GeneratePDFParams,
    GetDocumentParams,
    PDFGateParams,
    ProtectPDFByDocumentIdParams,
    ProtectPDFParams,
)
from pdfgate_sdk_python.url_builder import URLBuilder


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
    params_dict = asdict(instance)
    params_without_nulls: dict[str, Any] = {}
    for k, v in params_dict.items():
        if v is not None:
            params_without_nulls[snake_to_camel(k)] = (
                v.value if isinstance(v, Enum) else v
            )

    return params_without_nulls


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
        request = self._json_post_request(url, json=params_without_nulls)
        timeout = int(
            timedelta(minutes=Config.GENERATE_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_flatten_pdf(self, params: FlattenPDFParams) -> PDFGateRequest:
        """Build a request to flatten a PDF from file or document ID."""
        url = self.url_builder.flatten_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        if isinstance(params, FlattenPDFByFileParams) and params.file is not None:
            files = {"file": params_without_nulls.pop("file")}
        else:
            files = {}

        request = self._multipart_post_request(
            url, data=params_without_nulls, files=files
        )
        timeout = int(
            timedelta(minutes=Config.FLATTEN_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_extract_pdf_form_data(
        self, params: ExtractPDFFormDataParams
    ) -> PDFGateRequest:
        """Build a request to extract PDF form data."""
        url = self.url_builder.extract_pdf_form_data_url()
        if isinstance(params, ExtractPDFFormDataByDocumentIdParams):
            params_dict = {"documentId": params.document_id}
            request = self._multipart_post_request(url, data=params_dict)
        else:
            request = self._multipart_post_request(url, files={"file": params.file})

        return PDFGateRequest(request=request)

    def build_protect_pdf(self, params: ProtectPDFParams) -> PDFGateRequest:
        """Build a request to encrypt a PDF from file or document ID."""
        url = self.url_builder.protect_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        if isinstance(params, ProtectPDFByDocumentIdParams):
            request = self._multipart_post_request(url=url, data=params_without_nulls)
        else:
            file_param = {"file": params_without_nulls.pop("file", None)}
            request = self._multipart_post_request(
                url=url,
                data=params_without_nulls,
                files=file_param,
            )
        timeout = int(
            timedelta(minutes=Config.PROTECT_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)

    def build_compress_pdf(self, params: CompressPDFParams) -> PDFGateRequest:
        """Build a request to compress a PDF from file or document ID."""
        url = self.url_builder.compress_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        if isinstance(params, CompressPDFByDocumentIdParams):
            request = self._multipart_post_request(url=url, data=params_without_nulls)
        else:
            file_param = {"file": params_without_nulls.pop("file", None)}
            request = self._multipart_post_request(
                url=url,
                data=params_without_nulls,
                files=file_param,
            )
        timeout = int(
            timedelta(minutes=Config.COMPRESS_PDF_TIMEOUT_MINUTES).total_seconds()
        )

        return PDFGateRequest(request=request, timeout=timeout)
