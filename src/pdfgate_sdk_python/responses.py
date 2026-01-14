from datetime import datetime
from enum import Enum
from typing import Any, Optional, TypedDict

class DocumentStatus(Enum):
    COMPLETED = "completed"
    PROCESSING = "processing"
    EXPIRED = "expired"
    FAILED = "failed"

class DocumentType(Enum):
    FROM_HTML = "from_html"
    FLATTENED = "flattened"
    WATERMARKED = "watermarked"
    ENCRYPTED = "encrypted"
    COMPRESSED = "compressed"
    SIGNED = "signed"

class PDFGateDocument(TypedDict, total=False):
    id: str
    status: DocumentStatus
    created_at: datetime
    expires_at: datetime
    type: Optional[DocumentType]
    file_url: Optional[str]
    size: Optional[int]
    metadata: Optional[dict[str, Any]]
    derived_from: Optional[str]