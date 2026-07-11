from fastapi import APIRouter, status, HTTPException
from schemas.note import NoteCreate, NoteResponse, NoteUpdate, NotePatch

router = APIRouter(prefix="/notes", tags=["Notes"])

notes = []

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_notes(note:  NoteCreate) -> list:
    new_note = {
        "id": len(notes) + 1,
        "title": note.title,
        "content": note.content
    }
    notes.append(new_note)
    return new_note

