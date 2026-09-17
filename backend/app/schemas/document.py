from pydantic import BaseModel
from typing import Optional


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    status: str
    page_count: int
    chunk_count: int

    class Config:
        from_attributes = True