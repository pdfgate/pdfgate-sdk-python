"""Parameter types and enums used by PDFGate API calls."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, NamedTuple, Optional


class PageSizeType(Enum):
    """Supported page sizes for generated PDFs."""

    A0 = "a0"
    A1 = "a1"
    A2 = "a2"
    A3 = "a3"
    A4 = "a4"
    A5 = "a5"
    A6 = "a6"
    LEDGER = "ledger"
    TABLOID = "tabloid"
    LEGAL = "legal"
    LETTER = "letter"


class FileOrientation(Enum):
    """Orientation options for generated PDFs."""

    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class EmulateMediaType(Enum):
    """Media types for CSS emulation during rendering."""

    SCREEN = "screen"
    PRINT = "print"


class PdfStandardFont(Enum):
    """Standard built-in fonts supported by the renderer."""

    TIMES_ROMAN = "times-roman"
    TIMES_BOLD = "times-bold"
    TIMES_ITALIC = "times-italic"
    TIMES_BOLD_ITALIC = "times-bolditalic"
    HELVETICA = "helvetica"
    HELVETICA_BOLD = "helvetica-bold"
    HELVETICA_OBLIQUE = "helvetica-oblique"
    HELVETICA_BOLD_OBLIQUE = "helvetica-boldoblique"
    COURIER = "courier"
    COURIER_BOLD = "courier-bold"
    COURIER_OBLIQUE = "courier-oblique"
    COURIER_BOLD_OBLIQUE = "courier-boldoblique"


@dataclass
class PdfPageMargin:
    """Margins to apply to a PDF page."""

    top: Optional[str] = None
    bottom: Optional[str] = None
    left: Optional[str] = None
    right: Optional[str] = None


@dataclass
class ClickSelectorChain:
    """Sequence of selectors to click in order."""

    selectors: list[str]


@dataclass
class ClickSelectorChainSetup:
    """Configuration for click selector chains."""

    ignore_failing_chains: Optional[bool] = None
    chains: Optional[list["ClickSelectorChain"]] = None


class FileParam(NamedTuple):
    """Binary file payload for multipart uploads."""

    name: str
    data: bytes
    type: Optional[str] = None

    @classmethod
    def pdf(cls, name: str, data: bytes) -> "FileParam":
        return cls(name=name, data=data, type="application/pdf")


@dataclass
class PDFGateParams:
    """Marker base class for all parameter dataclasses."""

    pass


@dataclass
class GetDocumentParams(PDFGateParams):
    """Parameters for fetching a document's metadata."""

    document_id: str
    pre_signed_url_expires_in: Optional[int] = None


@dataclass
class GetFileParams(PDFGateParams):
    """Parameters for downloading a document's file content."""

    document_id: str


@dataclass
class UploadFileParams(PDFGateParams):
    """Parameters for uploading a raw PDF file to PDFGate"""

    file: Optional[FileParam] = None
    url: Optional[str] = None
    metadata: Optional[Any] = None
    pre_signed_url_expires_in: Optional[int] = None


@dataclass
class GeneratePDFAuthentication:
    """ "Authentication credentials for accessing protected web content."""

    username: str
    password: str


@dataclass
class Viewport:
    """Viewport dimensions for rendering."""

    width: int
    height: int


@dataclass
class GeneratePDFParams(PDFGateParams):
    """Parameters for generating a PDF from HTML or a URL."""

    html: Optional[str] = None
    url: Optional[str] = None
    pre_signed_url_expires_in: Optional[int] = None
    page_size_type: Optional[PageSizeType] = None
    width: Optional[int] = None
    height: Optional[int] = None
    orientation: Optional[FileOrientation] = None
    header: Optional[str] = None
    footer: Optional[str] = None
    margin: Optional[PdfPageMargin] = None
    timeout: Optional[int] = None
    javascript: Optional[str] = None
    css: Optional[str] = None
    emulate_media_type: Optional[EmulateMediaType] = None
    http_headers: Optional[dict[str, str]] = None
    metadata: Optional[Any] = None
    wait_for_selector: Optional[str] = None
    click_selector: Optional[str] = None
    click_selector_chain_setup: Optional[ClickSelectorChainSetup] = None
    wait_for_network_idle: Optional[bool] = None
    enable_form_fields: Optional[bool] = None
    delay: Optional[int] = None
    load_images: Optional[bool] = None
    scale: Optional[float] = None
    page_ranges: Optional[str] = None
    print_background: Optional[bool] = None
    user_agent: Optional[str] = None
    authentication: Optional[GeneratePDFAuthentication] = None
    viewport: Optional[Viewport] = None


@dataclass
class FlattenPDFParams(PDFGateParams):
    """Parameters for flattening a PDF by document ID."""

    document_id: Optional[str] = None
    pre_signed_url_expires_in: Optional[int] = None
    metadata: Optional[Any] = None


@dataclass
class ExtractPDFFormDataParams(PDFGateParams):
    """Parameters for extracting form data by document ID."""

    document_id: str


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""

    AES_256 = "AES256"
    AES_128 = "AES128"


@dataclass
class ProtectPDFParams(PDFGateParams):
    """Parameters for protecting a PDF by document ID."""

    document_id: Optional[str] = None
    algorithm: Optional[EncryptionAlgorithm] = None
    user_password: Optional[str] = None
    owner_password: Optional[str] = None
    disable_print: Optional[bool] = None
    disable_copy: Optional[bool] = None
    disable_editing: Optional[bool] = None
    encrypt_metadata: Optional[bool] = None
    pre_signed_url_expires_in: Optional[int] = None
    metadata: Optional[Any] = None


@dataclass
class CompressPDFParams(PDFGateParams):
    """Parameters for compressing a PDF by document ID."""

    document_id: Optional[str] = None
    linearize: Optional[bool] = None
    pre_signed_url_expires_in: Optional[int] = None
    metadata: Optional[Any] = None


class WatermarkType(Enum):
    TEXT = "text"
    IMAGE = "image"


@dataclass
class EnvelopeRecipient(PDFGateParams):
    """A recipient on a document within an envelope."""

    email: str
    name: str
    role: Optional[str] = None


@dataclass
class EnvelopeDocument(PDFGateParams):
    """A document to include in an envelope."""

    source_document_id: str
    name: str
    recipients: list["EnvelopeRecipient"]


@dataclass
class CreateEnvelopeParams(PDFGateParams):
    """Parameters for creating a signing envelope."""

    documents: list["EnvelopeDocument"]
    requester_name: str
    metadata: Optional[dict] = None


@dataclass
class SendEnvelopeParams(PDFGateParams):
    """Parameters for sending a signing envelope to its recipients."""

    envelope_id: str


@dataclass
class WatermarkPDFParams(PDFGateParams):
    """Parameters for watermarking a PDF by document ID."""

    type: WatermarkType
    document_id: Optional[str] = None
    text: Optional[str] = None
    watermark: Optional[FileParam] = None
    font: Optional[PdfStandardFont] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    opacity: Optional[float] = None
    x_position: Optional[int] = None
    y_position: Optional[int] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    rotate: Optional[float] = None
    pre_signed_url_expires_in: Optional[int] = None
    metadata: Optional[Any] = None
