"""Public package initialization for pdfgate."""

# SPDX-FileCopyrightText: 2026-present Fernando Gasperi <fgasperijabalera@gmail.com>
#
# SPDX-License-Identifier: MIT

from .pdfgate import PDFGate
from .params import (
    PageSizeType,
    FileOrientation,
    EmulateMediaType,
    PdfStandardFont,
    PdfPageMargin,
    ClickSelectorChain,
    ClickSelectorChainSetup,
    PDFGateParams,
    GetDocumentParams,
    UploadFileParams,
    GetFileParams,
    GeneratePDFAuthentication,
    Viewport,
    GeneratePDFParams,
    FlattenPDFParams,
    FileParam,
    ExtractPDFFormDataParams,
    EncryptionAlgorithm,
    ProtectPDFParams,
    CompressPDFParams,
    WatermarkType,
    WatermarkPDFParams,
)
from .responses import (
    DocumentStatus,
    DocumentType,
    PDFGateDocument,
)

__all__ = [
    "PDFGate",
    "PageSizeType",
    "FileOrientation",
    "EmulateMediaType",
    "PdfStandardFont",
    "PdfPageMargin",
    "ClickSelectorChain",
    "ClickSelectorChainSetup",
    "PDFGateParams",
    "GetDocumentParams",
    "GetFileParams",
    "GeneratePDFAuthentication",
    "Viewport",
    "GeneratePDFParams",
    "FlattenPDFParams",
    "FileParam",
    "ExtractPDFFormDataParams",
    "EncryptionAlgorithm",
    "ProtectPDFParams",
    "CompressPDFParams",
    "WatermarkType",
    "WatermarkPDFParams",
    "DocumentStatus",
    "DocumentType",
    "PDFGateDocument",
    "UploadFileParams",
]
