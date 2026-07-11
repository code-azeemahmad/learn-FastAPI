from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(
        max_length=30,
    )
    content: str = Field(
        max_length=300
    )

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    
class NoteUpdate(BaseModel):
    title: str = Field(
        max_length=30,
    )
    content: str = Field(
        max_length=300
    )

class NotePatch(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=100
    )
    content: str | None = Field(
        default=None,
        max_length=300
    )

