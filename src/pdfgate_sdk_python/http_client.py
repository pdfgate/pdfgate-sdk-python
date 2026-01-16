
from typing import NoReturn
import httpx

from pdfgate_sdk_python.errors import PDFGateError
from pdfgate_sdk_python.request_builder import PDFGateRequest


class PDFGateHTTPClientBase:

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self) -> dict[str, str]:
        """Return HTTP headers for API requests.

        Returns:
            A dict of headers including the Authorization bearer token.
        """
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def raise_error_from_http_status_error(self, e: httpx.HTTPStatusError) -> NoReturn:
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

class PDFGateHTTPClientSync(PDFGateHTTPClientBase):

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
    
    def try_make_request(self, request: PDFGateRequest) -> httpx.Response:
        try:
            with httpx.Client(timeout=request.timeout) as client:
                response = client.send(request.request)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self.raise_error_from_http_status_error(e)
        except httpx.RequestError as e:
            raise PDFGateError(f"Request failed: {e}") from e

        return response

class PDFGateHTTPClientAsync(PDFGateHTTPClientBase):

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
    
    async def try_make_request_async(self, request: PDFGateRequest) -> httpx.Response:
        try:
            async with httpx.AsyncClient(timeout=request.timeout) as client:
                response = await client.send(request.request)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self.raise_error_from_http_status_error(e)
        except httpx.RequestError as e:
            raise PDFGateError(f"Request failed: {e}") from e

        return response