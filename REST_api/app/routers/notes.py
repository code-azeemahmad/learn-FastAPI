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


@router.get("/", response_model=list[NoteResponse]) # return a list where every element looks like NoteResponse
def get_notes() -> list[NoteResponse]:
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int) -> NoteResponse:

    for note in notes:
        if note["id"] == note_id:
            return note
    else:
        raise HTTPException(    # Exceptions are meant to be raised.
            status_code=404,
            detail="Note not found!"
        )

