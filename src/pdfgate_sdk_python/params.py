from dataclasses import dataclass
from typing import Optional

@dataclass
class GetDocumentParams:
    document_id: str
    pre_signed_url_expires_in: Optional[int] = None