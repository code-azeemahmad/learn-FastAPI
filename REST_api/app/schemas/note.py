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
    
