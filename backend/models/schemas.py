from pydantic import BaseModel, Field
from typing import Optional


class ConversationMessage(BaseModel):
    role: str
    content: str


class WordMeaningItem(BaseModel):
    part_of_speech: str = ""
    definition: str = ""
    example: str = ""


class WordData(BaseModel):
    word: str
    phonetic: str = ""
    meanings: list[dict] = []


class WordNoteItem(BaseModel):
    word: str
    phonetic: str = ""
    meaning: str = ""
    meanings: list[dict] = []
    createTime: int = 0


class ChatSaveRequest(BaseModel):
    scene: str
    history: list[dict]


class WordNoteAddBody(BaseModel):
    word: Optional[str] = None
    phonetic: Optional[str] = ""
    meaning: Optional[str] = ""
    meanings: Optional[list[dict]] = []
    createTime: Optional[int] = None


class ExamAnswerItem(BaseModel):
    question_id: str
    selected_option: str


class ExamSubmitBody(BaseModel):
    set_id: str
    answers: list[ExamAnswerItem]
