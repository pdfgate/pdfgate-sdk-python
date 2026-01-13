import pytest
import responses
from pdfgate_sdk_python.constants import PRODUCTION_API_DOMAIN
from pdfgate_sdk_python.errors import PDFGateError
from pdfgate_sdk_python.params import GetDocumentParams
from pdfgate_sdk_python.pdfgate import PDFGate, URLBuilder


VALID_API_KEY = "live_1234567890abcdef"

def test_invalid_api_key_raises():
    with pytest.raises(PDFGateError, match="Invalid API key format"):
        PDFGate("wrong_prefix_213123")

@responses.activate
def test_get_document_raises_pdfgate_error_on_http_error():
    document_id = "doc1"
    responses.add(
        responses.GET,
        URLBuilder.get_document_url(PRODUCTION_API_DOMAIN, document_id),
        json={
            "statusCode": 400,
            "message": "preSignedUrlExpiresIn: preSignedUrlExpiresIn must not be greater than 86400",
            "error": "Bad Request"
        },
        status=400
    )
    client = PDFGate(api_key=VALID_API_KEY)
    invalid_pre_signed_url_expires_in = 90000  # Invalid value greater than 86400
    params = GetDocumentParams(
        document_id=document_id,
        pre_signed_url_expires_in=invalid_pre_signed_url_expires_in
    )

    error_message_pattern = r"HTTP Error.*400.*preSignedUrlExpiresIn must not be greater than.*"
    with pytest.raises(PDFGateError, match=error_message_pattern):
        client.get_document(params)