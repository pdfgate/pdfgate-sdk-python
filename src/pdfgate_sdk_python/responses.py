from datetime import datetime
from enum import Enum
import re
from typing import Any, Optional, TypedDict, Union


def camel_to_snake(name: str) -> str:
    """Convert a string from camelCase to snake_case."""
    # Inserts an underscore before any uppercase letter that is followed by a
    # lowercase letter or digit.
    # This is needed for cases like: TestHTTPResponse -> TestHTTP_Response
    s1 = re.sub('(.)([A-Z][a-z0-9]+)', r'\1_\2', name)
    # Inserts an underscore before any uppercase letter that is preceded by a lowercase letter or digit
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def convert_keys_to_snake_case(data: Union[dict[Any, Any], list[Any], Any]) -> Union[dict[Any, Any], list[Any], Any]:
    """Recursively converts all keys in a dictionary or list to snake_case."""
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items(): # type: ignore
            new_key = camel_to_snake(key) # type: ignore
            new_dict[new_key] = convert_keys_to_snake_case(value) # type: ignore
        return new_dict # type: ignore
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data] # type: ignore
    else:
        return data

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