"""pdfgate_sdk_python.pdfgate

Client for interacting with the PDFGate API.
"""

from dataclasses import asdict
from datetime import timedelta
from enum import Enum
from typing import Any, Union, cast
import requests

from pdfgate_sdk_python.dict_keys_converter import convert_camel_keys_to_snake, snake_to_camel
from pdfgate_sdk_python.http_client import PDFGateHTTPClientAsync, PDFGateHTTPClientSync
from pdfgate_sdk_python.request_builder import RequestBuilder, get_domain_from_api_key
from pdfgate_sdk_python.url_builder import URLBuilder

from .errors import PDFGateError, ParamsValidationError
from .params import CompressPDFByDocumentIdParams, CompressPDFParams, ExtractPDFFormDataByDocumentIdParams, ExtractPDFFormDataParams, FlattenPDFParams, GeneratePDFParams, GetDocumentParams, GetFileParams, ProtectPDFByDocumentIdParams, ProtectPDFParams
from .responses import PDFGateDocument

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
        self.domain = get_domain_from_api_key(api_key)
        self.api_key = api_key
        self.request_builder = RequestBuilder(api_key=api_key)
        self.sync_client = PDFGateHTTPClientSync(api_key=api_key)
        self.async_client = PDFGateHTTPClientAsync(api_key=api_key)

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
        request = self.request_builder.build_get_document(params)
        response = self.sync_client.try_make_request(request)
        json_response = response.json()

        return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

    async def get_document_async(self, params: GetDocumentParams) -> PDFGateDocument:
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
        request = self.request_builder.build_get_document(params)
        response = await self.async_client.try_make_request_async(request)
        json_response = response.json()

        return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

    def get_file(self, params: GetFileParams) -> bytes:
        """Download a raw PDF file by its document ID.

        Returns:
            The raw bytes of the file.
        """
        request = self.request_builder.build_get_file(params.document_id)
        response = self.sync_client.try_make_request(request=request)

        return response.content

    async def get_file_async(self, params: GetFileParams) -> bytes:
        """Download a raw PDF file by its document ID.

        Returns:
            The raw bytes of the file.
        """
        request = self.request_builder.build_get_file(params.document_id)
        response = await self.async_client.try_make_request_async(request=request)

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
            return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

        return response.content

    def flatten_pdf(self, params: FlattenPDFParams) -> Union[bytes, PDFGateDocument]:
        """Flatten a PDF document.

        Depending on the `json_response` flag in `params`, this method either
        returns the raw PDF bytes or a `PDFGateDocument` instance.
        """
        headers = self.get_base_headers()
        url = URLBuilder.flatten_pdf_url(self.domain)
        params_dict = asdict(params)
        params_without_nulls: dict[str, Any] = {}
        for k, v in params_dict.items():
            if v is not None:
                params_without_nulls[snake_to_camel(k)] = v

        file_param = {"file": params_without_nulls.pop("file", None)}

        request = requests.Request("POST", url=url, headers=headers, files=file_param, data=params_without_nulls).prepare()
        timeout = int(timedelta(minutes=3).total_seconds())
        response = try_make_request(request, timeout=timeout)

        if params.json_response:
            json_response = response.json()
            return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

        return response.content

    def extract_pdf_form_data(self, params: ExtractPDFFormDataParams) -> Any:
        headers = self.get_base_headers()
        url = URLBuilder.extract_pdf_form_data_url(self.domain)
        if isinstance(params, ExtractPDFFormDataByDocumentIdParams):
            params_dict = {"documentId": params.document_id}
            request = requests.Request("POST", url=url, headers=headers, data=params_dict).prepare()
        else:
            request = requests.Request("POST", url=url, headers=headers, files={"file": params.file}).prepare()

        response = try_make_request(request)

        json_response = response.json()

        return convert_camel_keys_to_snake(json_response)

    def protect_pdf(self, params: ProtectPDFParams) -> Union[bytes, PDFGateDocument]:
        """Protect a PDF document by applying encryption.

        Sends a POST request to the `/document/protect` endpoint.

        Args:
            params:
                Parameters for the request, provided as a `ProtectPDFByDocumentIdParams` instance.

        Returns:
            A `PDFGateDocument` parsed from the JSON response.
        """
        headers = self.get_base_headers()
        url = URLBuilder.protect_pdf_url(self.domain)

        params_dict = asdict(params)
        params_without_nulls: dict[str, Any] = {}
        for k, v in params_dict.items():
            if v is not None:
                params_without_nulls[snake_to_camel(k)] = v.value if isinstance(v, Enum) else v

        if isinstance(params, ProtectPDFByDocumentIdParams):
            request = requests.Request("POST", url=url, headers=headers, data=params_without_nulls).prepare()
        else:
            file_param = {"file": params_without_nulls.pop("file", None)}
            request = requests.Request("POST", url=url, headers=headers, data=params_without_nulls, files=file_param).prepare()

        timeout = int(timedelta(minutes=3).total_seconds())
        response = try_make_request(request, timeout=timeout)

        if params.json_response:
            json_response = response.json()
            return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

        return response.content

    def compress_pdf(self, params: CompressPDFParams) -> Union[bytes, PDFGateDocument]:
        """Compress a PDF document to reduce its size without changing its visual content.
        """
        headers = self.get_base_headers()
        url = URLBuilder.compress_pdf_url(self.domain)

        params_dict = asdict(params)
        params_without_nulls: dict[str, Any] = {}
        for k, v in params_dict.items():
            if v is not None:
                params_without_nulls[snake_to_camel(k)] = v.value if isinstance(v, Enum) else v

        if isinstance(params, CompressPDFByDocumentIdParams):
            request = requests.Request("POST", url=url, headers=headers, data=params_without_nulls).prepare()
        else:
            file_param = {"file": params_without_nulls.pop("file", None)}
            request = requests.Request("POST", url=url, headers=headers, data=params_without_nulls, files=file_param).prepare()

        timeout = int(timedelta(minutes=3).total_seconds())
        response = try_make_request(request, timeout=timeout)

        if params.json_response:
            json_response = response.json()
            return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

        return response.content