from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Any
import httpx
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN, SANDBOX_API_DOMAIN
from pdfgate_sdk_python.dict_keys_converter import snake_to_camel
from pdfgate_sdk_python.errors import PDFGateError
from pdfgate_sdk_python.params import (
    ExtractPDFFormDataByDocumentIdParams,
    ExtractPDFFormDataParams,
    FlattenPDFBinaryParams,
    FlattenPDFParams,
    GeneratePDFParams,
    GetDocumentParams,
    PDFGateParams,
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
        return PRODUCTION_API_DOMAIN
    elif api_key.startswith("test_"):
        return SANDBOX_API_DOMAIN
    else:
        raise PDFGateError(
            "Invalid API key format. Expected to start with 'live_' or 'test_'."
        )


def pdfgate_params_to_params_dict(instance: PDFGateParams) -> dict[str, Any]:
    params_dict = asdict(instance)
    params_without_nulls: dict[str, Any] = {}
    for k, v in params_dict.items():
        if v is not None:
            params_without_nulls[snake_to_camel(k)] = v

    return params_without_nulls


@dataclass
class PDFGateRequest:
    request: httpx.Request
    timeout: int = int(timedelta(seconds=60).total_seconds())


class RequestBuilder:
    def __init__(self, api_key: str):
        domain = get_domain_from_api_key(api_key)
        self.url_builder = URLBuilder(domain)
        self.api_key = api_key

    def get_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _get_request(self, url: str, params: dict[str, Any] = {}) -> httpx.Request:
        return httpx.Request("GET", url=url, headers=self.get_headers(), params=params)

    def _json_post_request(self, url: str, json: dict[str, Any]) -> httpx.Request:
        return httpx.Request("POST", url=url, headers=self.get_headers(), json=json)

    def _multipart_post_request(
        self, url: str, data: dict[str, Any] = {}, files: dict[str, Any] = {}
    ) -> httpx.Request:
        return httpx.Request(
            "POST", url=url, headers=self.get_headers(), data=data, files=files
        )

    def build_get_file(self, document_id: str) -> PDFGateRequest:
        url = self.url_builder.get_file_url(document_id)
        request = self._get_request(url)

        return PDFGateRequest(request=request)

    def build_get_document(self, params: GetDocumentParams) -> PDFGateRequest:
        params_dict: dict[str, int] = {}
        if params.pre_signed_url_expires_in is not None:
            params_dict["preSignedUrlExpiresIn"] = params.pre_signed_url_expires_in

        url = self.url_builder.get_document_url(params.document_id)
        request = self._get_request(url, params_dict)

        return PDFGateRequest(request=request)

    def build_generate_pdf(self, params: GeneratePDFParams) -> PDFGateRequest:
        url = self.url_builder.generate_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        request = self._json_post_request(url, json=params_without_nulls)
        timeout = int(timedelta(minutes=15).total_seconds())

        return PDFGateRequest(request=request, timeout=timeout)

    def build_flatten_pdf(self, params: FlattenPDFParams) -> PDFGateRequest:
        url = self.url_builder.flatten_pdf_url()
        params_without_nulls = pdfgate_params_to_params_dict(params)
        if isinstance(params, FlattenPDFBinaryParams) and params.file is not None:
            files = {"file": params_without_nulls.pop("file")}
        else:
            files = {}

        request = self._multipart_post_request(
            url, data=params_without_nulls, files=files
        )
        timeout = int(timedelta(minutes=3).total_seconds())

        return PDFGateRequest(request=request, timeout=timeout)

    def build_extract_pdf_form_data(
        self, params: ExtractPDFFormDataParams
    ) -> PDFGateRequest:
        url = self.url_builder.extract_pdf_form_data_url()
        if isinstance(params, ExtractPDFFormDataByDocumentIdParams):
            params_dict = {"documentId": params.document_id}
            request = self._multipart_post_request(url, data=params_dict)
        else:
            request = self._multipart_post_request(url, files={"file": params.file})

        return PDFGateRequest(request=request)
