from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


def snake_to_camel(key: str) -> str:
    """Convert a snake_case string to camelCase."""
    parts = key.split('_')

    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


class PageSizeType(Enum):
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
  PORTRAIT = "portrait"
  LANDSCAPE = "landscape"

class EmulateMediaType(Enum):
  SCREEN = "screen"
  PRINT = "print"

class PdfStandardFont(Enum):
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
  top: Optional[str] = None
  bottom: Optional[str] = None
  left: Optional[str] = None
  right: Optional[str] = None

@dataclass
class ClickSelectorChain:
  selectors: list[str]

@dataclass
class ClickSelectorChainSetup:
  ignore_failing_chains: Optional[bool] = None
  chains: Optional[list["ClickSelectorChain"]] = None

@dataclass
class GetDocumentParams:
    document_id: str
    pre_signed_url_expires_in: Optional[int] = None

@dataclass
class GetFileParams:
    document_id: str

@dataclass
class GeneratePDFParams:
    html: Optional[str] = None
    url: Optional[str] = None
    json_response: Optional[bool] = False
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
    grayscale: Optional[bool] = None
    enable_form_fields: Optional[bool] = None
    delay: Optional[int] = None
    load_images: Optional[bool] = None
    scale: Optional[float] = None
    page_ranges: Optional[str] = None
    print_background: Optional[bool] = None
    user_agent: Optional[str] = None