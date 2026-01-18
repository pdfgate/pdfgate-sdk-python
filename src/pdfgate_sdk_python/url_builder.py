class URLBuilder:
    """Helper class to build URLs for the PDFGate API."""

    def __init__(self, domain: str):
        self.domain = domain

    def get_document_url(self, document_id: str) -> str:
        """Build the URL for accessing a document.

        Args:
            domain:
                Base API domain.
            document_id:
                ID of the document.

        Returns:
            Full URL to access the document.
        """
        return f"{self.domain}/document/{document_id}"

    def get_file_url(self, document_id: str) -> str:
        """Build the URL for downloading a document.

        Args:
            domain:
                Base API domain.
            document_id:
                ID of the document.

        Returns:
            Full URL to download the document.
        """
        return f"{self.domain}/file/{document_id}"

    def generate_pdf_url(self) -> str:
        """Build the URL for generating a PDF.

        Args:
            domain:
                Base API domain.
        """
        return f"{self.domain}/v1/generate/pdf"

    def flatten_pdf_url(self) -> str:
        """Build the URL for flattening a PDF.

        Args:
            domain:
                Base API domain.
        """
        return f"{self.domain}/forms/flatten"

    @staticmethod
    def extract_pdf_form_data_url(domain: str) -> str:
        """Build the URL for extracting PDF form data.

        Args:
            domain:
                Base API domain.
        """
        return f"{domain}/forms/extract-data"

    @staticmethod
    def protect_pdf_url(domain: str) -> str:
        """Build the URL for encrypting a PDF.

        Args:
            domain:
                Base API domain.
        """
        return f"{domain}/protect/pdf"

    @staticmethod
    def compress_pdf_url(domain: str) -> str:
        """Build the URL for compressing a PDF.

        Args:
            domain:
                Base API domain.
        """
        return f"{domain}/compress/pdf"
