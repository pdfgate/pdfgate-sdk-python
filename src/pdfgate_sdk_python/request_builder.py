
from typing import Any
import httpx
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN, SANDBOX_API_DOMAIN
from pdfgate_sdk_python.errors import PDFGateError
from pdfgate_sdk_python.params import GetDocumentParams
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
        raise PDFGateError("Invalid API key format. Expected to start with 'live_' or 'test_'.")

class RequestBuilder:

    def __init__(self, api_key: str):
        domain = get_domain_from_api_key(api_key)
        self.url_builder = URLBuilder(domain)
        self.api_key = api_key

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def _get_request(self, url: str, params: dict[str, Any] = {}) -> httpx.Request:
        return httpx.Request("GET", url=url, headers=self.get_headers(), params=params)

    def build_get_file(self, document_id: str) -> httpx.Request:
        url = self.url_builder.get_file_url(document_id)
        request = self._get_request(url)

        return request

    def build_get_document(self, params: GetDocumentParams) -> httpx.Request:
        params_dict: dict[str, int] = {}
        if params.pre_signed_url_expires_in is not None:
            params_dict["preSignedUrlExpiresIn"] = params.pre_signed_url_expires_in

        url = self.url_builder.get_document_url(params.document_id)
        request = self._get_request(url, params_dict)

        return request
