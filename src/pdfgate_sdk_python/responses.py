from dataclasses import dataclass, fields
from datetime import datetime
from enum import Enum
from typing import Any, Mapping, Optional, Union, cast, get_args, get_origin

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

GetDocumentResponseValue = Union[str, int, dict[str, Any]]

def is_optional(field_type: Union[type[Any], str, Any]) -> bool:
    """Checks if a given type annotation is Optional (Union[T, None])."""
    # Optional[T] is a shortcut for Union[T, None].
    # Use get_origin to handle both typing.Union and the '|' syntax in Python 3.10+
    origin = get_origin(field_type)

    # Check if the type is a Union
    if origin is Union:
        # Get the arguments of the Union (e.g., [int, NoneType])
        args = get_args(field_type)
        # Check if NoneType is one of the arguments
        return type(None) in args
    
    # If it's not a Union, it's not Optional
    return False

def is_valid_value_of_enum(enum: type[Enum], value: Any) -> bool:
    try:
        enum(value)
        return True
    except (ValueError, TypeError):
        return False

def is_isoformat(value: str) -> bool:
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False

class PDFGateDocumentResponseValidator:
    @classmethod
    def validate(cls, data: Mapping[str, Optional[GetDocumentResponseValue]]) -> None:
        for field in fields(PDFGateDocument):
            if not is_optional(field.type) and data.get(field.name) is None:
                raise ValueError(f"Missing required field: {field.name}")

            field_type = PDFGateDocument.__annotations__[field.name]
            # print(f"field.name: {field.name}")
            # print(f"field.type: {field.type} type(field.type): {type(field.type)}")
            # print(f"PDFGateDocument.__annotations__[field.name]: {field.type} type(field_type): {type(field_type)}")
            # print(f"get_origin: {get_origin(field_type)}")
            # print(f"issubclass check: {issubclass(get_origin(field_type) or field_type, Enum)}")
            # print(f"is_valid_value_of_enum check: {is_valid_value_of_enum(field_type, data.get(field.name))}")
            if issubclass(get_origin(field_type) or field_type, Enum):
                if not is_valid_value_of_enum(field_type, data.get(field.name)):
                    raise ValueError(f"Field {field.name} must be of type {field_type.__name__}")
            elif issubclass(get_origin(field_type) or field_type, datetime):
                if not isinstance(data.get(field.name), str) or not is_isoformat(cast(str, data.get(field.name))):
                    raise ValueError(f"Field {field.name} must be of type datetime in ISO format string")
            elif not isinstance(data.get(field.name), field_type):
                raise ValueError(f"Field {field.name} must be of type {field_type.__name__}")

@dataclass
class PDFGateDocument:
    id: str
    status: DocumentStatus
    created_at: datetime
    expires_at: datetime
    type: Optional[DocumentType] = None
    file_url: Optional[str] = None
    size: Optional[int] = None
    metadata: Optional[dict[str, Any]] = None
    derived_from: Optional[str] = None

    @classmethod
    def from_json(cls, data: Mapping[str, Optional[GetDocumentResponseValue]]) -> "PDFGateDocument":
        PDFGateDocumentResponseValidator.validate(data)

        return cls(
            id = cast(str, data["id"]),
            status = DocumentStatus(data["status"]),
            type = DocumentType(data["document_type"]) if data.get("document_type") else None,
            file_url = cast(Union[str, None], data.get("file_url")),
            size = cast(Union[int, None], data.get("size")),
            metadata = cast(Union[dict[str, Any], None], data.get("metadata")),
            derived_from = cast(Union[str, None], data.get("derived_from")),
            created_at = datetime.fromisoformat(cast(str, data["created_at"])),
            expires_at = datetime.fromisoformat(cast(str, data["expires_at"]))
        )