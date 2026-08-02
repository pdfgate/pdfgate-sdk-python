"""URL construction for PDFGate API endpoints."""


class URLBuilder:
    """Helper class to build URLs for the PDFGate API."""

    def __init__(self, domain: str):
        """Create a URL builder using the provided API domain."""
        self.domain = domain

    def get_document_url(self, document_id: str) -> str:
        """Build the URL for accessing a document.

        Args:
            document_id:
                ID of the document.

        Returns:
            Full URL to access the document.
        """
        return f"{self.domain}/document/{document_id}"

    def get_file_url(self, document_id: str) -> str:
        """Build the URL for downloading a document.

        Args:
            document_id:
                ID of the document.

        Returns:
            Full URL to download the document.
        """
        return f"{self.domain}/file/{document_id}"

    def generate_pdf_url(self) -> str:
        """Build the URL for generating a PDF.

        Returns:
            Full URL to generate a PDF.
        """
        return f"{self.domain}/v1/generate/pdf"

    def flatten_pdf_url(self) -> str:
        """Build the URL for flattening a PDF.

        Returns:
            Full URL to flatten a PDF.
        """
        return f"{self.domain}/forms/flatten"

    def extract_pdf_form_data_url(self) -> str:
        """Build the URL for extracting PDF form data.

        Returns:
            Full URL to extract PDF form data.
        """
        return f"{self.domain}/forms/extract-data"

    def add_form_fields_url(self) -> str:
        """Build the URL for adding form fields to a PDF.

        Returns:
            Full URL to add form fields.
        """
        return f"{self.domain}/forms/fields"

    def protect_pdf_url(self) -> str:
        """Build the URL for encrypting a PDF.

        Returns:
            Full URL to encrypt a PDF.
        """
        return f"{self.domain}/protect/pdf"

    def compress_pdf_url(self) -> str:
        """Build the URL for compressing a PDF.

        Returns:
            Full URL to compress a PDF.
        """
        return f"{self.domain}/compress/pdf"

    def watermark_pdf_url(self) -> str:
        """Build the URL for watermarking a PDF.

        Returns:
            Full URL to watermark a PDF.
        """
        return f"{self.domain}/watermark/pdf"

    def upload_file_url(self) -> str:
        """Build the URL for uploading a PDF.

        Returns:
            Full URL to upload a PDF.
        """
        return f"{self.domain}/upload"

    def envelope_url(self) -> str:
        """Build the URL for creating an envelope.

        Returns:
            Full URL to create an envelope.
        """
        return f"{self.domain}/envelope"

    def get_envelope_url(self, envelope_id: str) -> str:
        """Build the URL for fetching an envelope.

        Args:
            envelope_id:
                ID of the envelope to fetch.

        Returns:
            Full URL to fetch an envelope.
        """
        return f"{self.domain}/envelope/{envelope_id}"

    def send_envelope_url(self, envelope_id: str) -> str:
        """Build the URL for sending an envelope.

        Args:
            envelope_id:
                ID of the envelope to send.

        Returns:
            Full URL to send an envelope.
        """
        return f"{self.domain}/envelope/{envelope_id}/send"

    def webhook_url(self) -> str:
        """Build the URL for creating a webhook.

        Returns:
            Full URL to create a webhook.
        """
        return f"{self.domain}/webhook"

    def get_webhook_url(self, webhook_id: str) -> str:
        """Build the URL for fetching or deleting a webhook.

        Args:
            webhook_id:
                ID of the webhook.

        Returns:
            Full URL to fetch or delete a webhook.
        """
        return f"{self.domain}/webhook/{webhook_id}"
