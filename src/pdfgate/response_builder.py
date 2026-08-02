"""Helpers for converting HTTP responses into SDK return types."""

from typing import Any, cast

import httpx

from pdfgate.dict_keys_converter import convert_camel_keys_to_snake
from pdfgate.responses import PDFGateDocument, PDFGateEnvelope, WebhookResponse


class ResponseBuilder:
    """Build SDK responses from HTTP responses."""

    @staticmethod
    def build_json_response(response: httpx.Response) -> Any:
        """Convert an HTTP response into a generic JSON object."""
        json_response = response.json()

        return convert_camel_keys_to_snake(json_response)

    @staticmethod
    def build_envelope_response(response: httpx.Response) -> PDFGateEnvelope:
        """Convert an HTTP response into a `PDFGateEnvelope`."""
        return cast(PDFGateEnvelope, ResponseBuilder.build_json_response(response))

    @staticmethod
    def build_document_response(response: httpx.Response) -> PDFGateDocument:
        """Convert an HTTP response into a `PDFGateDocument`."""
        return cast(PDFGateDocument, ResponseBuilder.build_json_response(response))

    @staticmethod
    def build_webhook_response(response: httpx.Response) -> WebhookResponse:
        """Convert an HTTP response into a `WebhookResponse`."""
        return cast(WebhookResponse, ResponseBuilder.build_json_response(response))
