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
    VOIDED = "voided"


class EnvelopeDocumentStatus(Enum):
    PENDING = "pending"
    EXPIRED = "expired"
    VOIDED = "voided"
    SENT_FOR_SIGNING = "sent_for_signing"
    SIGNING_IN_PROGRESS = "signing_in_progress"
    SIGNING_FAILED = "signing_failed"
    COMPLETED = "completed"


class DocumentRecipientStatus(Enum):
    PENDING = "pending"
    EXPIRED = "expired"
    VOIDED = "voided"
    SIGNED = "signed"


class WebhookStatus(Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class WebhookEventType(Enum):
    """Events that a webhook can subscribe to."""

    ENVELOPE_SENT = "envelope.sent"
    ENVELOPE_COMPLETED = "envelope.completed"
    ENVELOPE_EXPIRED = "envelope.expired"
    ENVELOPE_VOIDED = "envelope.voided"
    ENVELOPE_DELETED = "envelope.deleted"
    ENVELOPE_RECIPIENT_SIGNED = "envelope.recipient.signed"
    ENVELOPE_RECIPIENT_ACTIVATED = "envelope.recipient.activated"
    ENVELOPE_DOCUMENT_COMPLETED = "envelope.document.completed"
    RECIPIENT_SIGNATURE_ENROLLED = "recipient.signature.enrolled"
    """A recipient completed the enrolment of a stored signature (automatic signing)."""
    RECIPIENT_SIGNATURE_REVOKED = "recipient.signature.revoked"
    """An active stored signature was removed from a recipient."""


class StoredSignatureStatus(Enum):
    """State of a recipient's stored signature (automatic signing)."""

    PENDING = "pending"
    """The enrolment link was sent but the recipient has not completed it."""
    ACTIVE = "active"
    """The signature can be applied to documents."""
    REVOKED = "revoked"
    """The signature was removed."""


class SignatureAdoptionMethod(Enum):
    """How a recipient created their stored signature."""

    TYPE_SIGNATURE = "type_signature"
    DRAW_SIGNATURE = "draw_signature"
    UPLOAD_SIGNATURE = "upload_signature"


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
    """A recipient within an envelope document response.

    ``activated_at`` is the time it became the recipient's turn to sign.
    Absent until the recipient is activated. ``auto_sign`` tells whether the
    recipient is signed automatically with their stored signature and
    ``send_signed_copy`` whether the recipient is emailed the signed document
    when the document completes.
    """

    recipient_id: str
    email: str
    embedded: bool
    auto_sign: bool
    send_signed_copy: bool
    status: DocumentRecipientStatus
    signing_order: int
    signed_at: str
    viewed_at: str
    activated_at: str
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
    expires_at: str
    completed_at: str
    expired_at: str
    voided_at: str
    void_reason: str
    metadata: Optional[dict[str, Any]]


class RecipientStoredSignature(TypedDict, total=False):
    """Automatic signing: the reusable signature a recipient stored through the
    enrolment link, or the state of the enrolment.

    ``requested_at`` is when the enrolment link was last sent,
    ``adoption_method`` how the recipient created the signature,
    ``enrolled_at`` when the recipient completed the enrolment, ``revoked_at``
    when the signature was removed, ``last_used_at`` when the signature was
    last applied to a document and ``use_count`` how many documents it was
    applied to. ``image`` is the signature as a PNG data URL, returned only by
    ``get_recipient`` while the signature is active.
    """

    status: StoredSignatureStatus
    requested_at: str
    adoption_method: SignatureAdoptionMethod
    enrolled_at: str
    revoked_at: str
    last_used_at: str
    use_count: int
    image: str


class PDFGateRecipient(TypedDict, total=False):
    """Typed dictionary representing a stored PDFGate recipient.

    ``signature`` is the stored signature of the recipient or the state of its
    enrolment (automatic signing). Absent until an enrolment was requested.
    """

    id: str
    email: str
    name: str
    metadata: Optional[dict[str, Any]]
    created_at: str
    updated_at: str
    last_used_at: str
    signature: RecipientStoredSignature


class RecipientListResponse(TypedDict, total=False):
    """Typed dictionary representing a list of stored recipients."""

    recipients: list[PDFGateRecipient]


class EmbedLinkResponse(TypedDict, total=False):
    """Typed dictionary representing an embedded signing link."""

    url: str
    expires_at: str


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
