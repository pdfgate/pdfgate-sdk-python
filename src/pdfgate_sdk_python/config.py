"""Configuration values for API domains and default timeouts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Holds constant configuration values for the SDK."""

    PRODUCTION_API_DOMAIN: str = "https://api.pdfgate.com"
    SANDBOX_API_DOMAIN: str = "https://api-sandbox.pdfgate.com"

    DEFAULT_TIMEOUT_SECONDS: int = 60
    GENERATE_PDF_TIMEOUT_MINUTES: int = 15
    FLATTEN_PDF_TIMEOUT_MINUTES: int = 3
    COMPRESS_PDF_TIMEOUT_MINUTES: int = 3
    PROTECT_PDF_TIMEOUT_MINUTES: int = 3
    WATERMARK_PDF_TIMEOUT_MINUTES: int = 3
