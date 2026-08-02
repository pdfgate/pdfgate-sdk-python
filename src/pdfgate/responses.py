"""Response models for PDFGate API results."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, TypedDict


class DocumentStatus(Enum):
    COMPLETED = "completed"
    PROCESSING = "processing"
    EXPIRED = "expired"
    FAILED = "failed"


class DocumentType(Enum):
    """Document types reported by the PDFGate API."""

    FROM_HTML = "from_html"
    UPLOADED = "uploaded"
    FLATTENED = "flattened"
    WATERMARKED = "watermarked"
    ENCRYPTED = "encrypted"
    COMPRESSED = "compressed"
    SIGNED = "signed"
    SIGNATURE_AUDIT_LOG = "signature_audit_log"
    DOCUMENT_FIELDS_ADDED = "document_fields_added"
    SIGNING_TEMPLATE = "signing_template"


class EnvelopeStatus(Enum):
    DRAFT = "draft"
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"


class EnvelopeDocumentStatus(Enum):
    PENDING = "pending"
    EXPIRED = "expired"
    SENT_FOR_SIGNING = "sent_for_signing"
    SIGNING_IN_PROGRESS = "signing_in_progress"
    SIGNING_FAILED = "signing_failed"
    COMPLETED = "completed"


class DocumentRecipientStatus(Enum):
    PENDING = "pending"
    EXPIRED = "expired"
    SIGNED = "signed"


class WebhookStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class WebhookEventType(Enum):
    """Events that a webhook can subscribe to."""

    ENVELOPE_SENT = "envelope.sent"
    ENVELOPE_COMPLETED = "envelope.completed"
    ENVELOPE_EXPIRED = "envelope.expired"
    ENVELOPE_DOCUMENT_COMPLETED = "envelope.document.completed"


class DocumentFieldType(Enum):
    SIGNATURE = "signature"
    TEXT = "text"
    NUMBER = "number"
    TEXT_AREA = "textarea"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    CHECKBOX = "checkbox"
    RADIO_BUTTON = "radio"
    SELECT = "select"


class EnvelopeFieldResponse(TypedDict, total=False):
    """A field within an envelope recipient response."""

    name: str
    type: DocumentFieldType
    value: Any
    checked: bool
    timezone: str
    source: str
    user_value: str
    user_timezone: str


class EnvelopeRecipientResponse(TypedDict, total=False):
    """A recipient within an envelope document response."""

    email: str
    status: DocumentRecipientStatus
    signed_at: str
    viewed_at: str
    fields: list[EnvelopeFieldResponse]
    signing_link: str
    preview_link: str


class EnvelopeDocumentResponse(TypedDict, total=False):
    """A document within an envelope response."""

    source_document_id: str
    signed_document_id: str
    audit_log_document_id: str
    recipients: list[EnvelopeRecipientResponse]
    status: EnvelopeDocumentStatus
    completed_at: str


class PDFGateEnvelope(TypedDict, total=False):
    """Typed dictionary representing a PDFGate envelope response."""

    id: str
    status: EnvelopeStatus
    documents: list[EnvelopeDocumentResponse]
    created_at: str
    completed_at: str
    expired_at: str
    metadata: Optional[dict[str, Any]]


class PDFGateDocument(TypedDict, total=False):
    """Typed dictionary representing a PDFGate document response."""

    id: str
    status: DocumentStatus
    created_at: datetime
    expires_at: datetime
    type: Optional[DocumentType]
    file_url: Optional[str]
    size: Optional[int]
    metadata: Optional[dict[str, Any]]
    derived_from: Optional[str]


class WebhookResponse(TypedDict, total=False):
    """Typed dictionary representing a PDFGate webhook."""

    id: str
    url: str
    event_types: list[WebhookEventType]
    status: WebhookStatus
    description: Optional[str]
    secret: Optional[str]
    created_at: str
    updated_at: Optional[str]


class WebhookResource(TypedDict):
    kind: str
    id: str


class WebhookEvent(TypedDict, total=False):
    """Typed dictionary representing a PDFGate Webhook Event response."""

    event_id: str
    event: str
    timestamp: str
    resource: WebhookResource
    data: dict[str, Any]
