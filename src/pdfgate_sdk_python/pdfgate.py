"""pdfgate_sdk_python.pdfgate

Client for interacting with the PDFGate API.
"""

from dataclasses import asdict
from datetime import timedelta
from typing import Any, Union, cast
import requests

from .errors import PDFGateError, ParamsValidationError
from .params import GeneratePDFParams, GetDocumentParams, GetFileParams, snake_to_camel
from .responses import PDFGateDocument, convert_keys_to_snake_case
from .constants import PRODUCTION_API_DOMAIN, SANDBOX_API_DOMAIN

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

class URLBuilder:
    """Helper class to build URLs for the PDFGate API."""

    @staticmethod
    def get_document_url(domain: str, document_id: str) -> str:
        """Build the URL for accessing a document.

        Args:
            domain:
                Base API domain.
            document_id:
                ID of the document.

        Returns:
            Full URL to access the document.
        """
        return f"{domain}/document/{document_id}"

    @staticmethod
    def get_file_url(domain: str, document_id: str) -> str:
        """Build the URL for downloading a document.

        Args:
            domain:
                Base API domain.
            document_id:
                ID of the document.

        Returns:
            Full URL to download the document.
        """
        return f"{domain}/file/{document_id}"

    @staticmethod
    def generate_pdf_url(domain: str) -> str:
        """Build the URL for generating a PDF.

        Args:
            domain:
                Base API domain.
        """
        return f"{domain}/v1/generate/pdf"

def try_make_request(request: requests.PreparedRequest, timeout: int = 60) -> requests.Response:
    try:
        with requests.Session() as session:
            response = session.send(request, timeout=timeout)

        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response is None:
            raise PDFGateError(f"HTTP Error without response: {e}") from e
        
        status_code = e.response.status_code
        content_type = e.response.headers.get('Content-Type', '')
        message = e.response.text
        if 'application/json' in content_type:
            try:
                error_info = e.response.json()
                message = error_info.get("message", e.response.text)
            except ValueError:
                message = e.response.text

        raise PDFGateError(f"HTTP Error: status {status_code} - message: {message}") from e
    except requests.RequestException as e:
        # Timeout, ConnectionError, etc.
        raise PDFGateError(f"Request failed: {e}") from e

    return response


class PDFGate:
    """Client for the PDFGate API.

    Attributes:
        api_key (str):
            API key used for authentication.
        domain (str):
            Base API domain derived from the API key.
    """
    def __init__(self, api_key: str):
        """Initialize a PDFGate client.

        Args:
            api_key: The API key to use. Must start with 'live_' or 'test_'.

        Raises:
            PDFGateError: If the API key is invalid.
        """
        self.api_key = api_key
        self.domain = get_domain_from_api_key(api_key)

    def get_base_headers(self) -> dict[str, str]:
        """Return HTTP headers for API requests.

        Returns:
            A dict of headers including the Authorization bearer token.
        """
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_document(self, params: GetDocumentParams) -> PDFGateDocument:
        """Retrieve a document from the PDFGate API.

        Sends a GET request to the `/document/{document_id}` endpoint. If
        `params.pre_signed_url_expires_in` is provided it will be sent as the
        `preSignedUrlExpiresIn` query parameter.

        Args:
            params:
                Parameters for the request, provided as a `GetDocumentParams` instance.

        Returns:
            A `PDFGateDocument` parsed from the JSON response.

        Raises:
            PDFGateError: If the HTTP request fails (including non-2xx responses) or if
                there is a network/connection error. The error includes status code
                and message when available.
        """
        headers = self.get_base_headers()

        params_dict: dict[str, int] = {}
        if params.pre_signed_url_expires_in is not None:
            params_dict["preSignedUrlExpiresIn"] = params.pre_signed_url_expires_in
        
        url = URLBuilder.get_document_url(self.domain, params.document_id)
        request = requests.Request("GET", url=url, headers=headers, params=params_dict).prepare()
        response = try_make_request(request)
        json_response = response.json()

        return cast(PDFGateDocument, convert_keys_to_snake_case(json_response))

    def get_file(self, params: GetFileParams) -> bytes:
        """Download a raw PDF file by its document ID.

        Returns:
            The raw bytes of the file.
        """
        headers = self.get_base_headers()

        url = URLBuilder.get_file_url(self.domain, params.document_id)
        request = requests.Request("GET", url=url, headers=headers).prepare()
        response = try_make_request(request)

        return response.content

    def generate_pdf(self, params: GeneratePDFParams) -> Union[bytes, PDFGateDocument]:
        """Generate a PDF document.

        Depending on the `json_response` flag in `params`, this method either
        returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        if not params.html and not params.url:
            raise ParamsValidationError("Either the 'html' or 'url' parameters must be provided to generate a PDF.")

        headers = self.get_base_headers()
        url = URLBuilder.generate_pdf_url(self.domain)
        params_dict = asdict(params)
        params_without_nulls: dict[str, Any] = {}
        for k, v in params_dict.items():
            if v is not None:
                params_without_nulls[snake_to_camel(k)] = v

        request = requests.Request("POST", url=url, headers=headers, json=params_without_nulls).prepare()
        timeout = int(timedelta(minutes=15).total_seconds())
        response = try_make_request(request, timeout=timeout)

        if params.json_response:
            json_response = response.json()
            return cast(PDFGateDocument, convert_keys_to_snake_case(json_response))

        return response.content