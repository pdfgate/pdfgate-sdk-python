"""Custom exception types for the PDFGate SDK."""


class PDFGateError(Exception):
    """Base error for SDK failures."""


class ParamsValidationError(PDFGateError):
    """Raised when required parameters are missing or invalid."""
