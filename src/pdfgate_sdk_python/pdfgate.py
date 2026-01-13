"""pdfgate_sdk_python.pdfgate

Client for interacting with the PDFGate API.
"""

from typing import cast
import requests

from .errors import PDFGateError
from .params import GetDocumentParams
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
        
        try:
            url = URLBuilder.get_document_url(self.domain, params.document_id)
            response = requests.get(url=url, headers=headers, params=params_dict)
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

        json_response = response.json()

        return cast(PDFGateDocument, convert_keys_to_snake_case(json_response))