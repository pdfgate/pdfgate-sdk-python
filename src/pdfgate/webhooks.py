"""Helpers for verifying PDFGate webhook requests."""

import hashlib
import hmac
import time
from typing import Union

from .config import Config
from .errors import WebhookSignatureVerificationError


def verify_signature(
    secret: str,
    signature_header: str,
    payload: Union[bytes, str],
) -> None:
    """Verify a PDFGate webhook signature.

    Args:
        secret:
            The webhook secret configured for the endpoint.
        signature_header:
            The raw ``x-pdfgate-signature`` header value.
        payload:
            The raw request body exactly as received.

    Raises:
        WebhookSignatureVerificationError:
            If the signature header is missing, malformed, expired, or invalid.
    """
    if not signature_header:
        raise WebhookSignatureVerificationError("Missing webhook signature header.")

    if isinstance(payload, bytes):
        payload_text = payload.decode("utf-8")
    else:
        payload_text = payload

    timestamp = None
    signatures: list[str] = []

    for part in signature_header.split(","):
        key, separator, value = part.strip().partition("=")
        if not separator:
            continue
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError as exc:
                raise WebhookSignatureVerificationError(
                    "Invalid webhook signature timestamp."
                ) from exc
        elif key == "v1":
            signatures.append(value)

    if timestamp is None or not signatures:
        raise WebhookSignatureVerificationError(
            "Missing timestamp or v1 signature in webhook signature header."
        )

    if abs(int(time.time()) - timestamp) > Config.WEBHOOK_SIGNATURE_TOLERANCE_SECONDS:
        raise WebhookSignatureVerificationError("Webhook signature has expired.")

    signed_payload = f"{timestamp}.{payload_text}"
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    for signature in signatures:
        if hmac.compare_digest(signature, expected_signature):
            return None

    raise WebhookSignatureVerificationError("Invalid webhook signature.")
