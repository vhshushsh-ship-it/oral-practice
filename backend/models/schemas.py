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


class SentenceAnalysisBody(BaseModel):
    text: str


class GrammarCheckBody(BaseModel):
    text: str


# ====================== 认证相关 ======================

class UserRegisterRequest(BaseModel):
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    password: str = Field(..., min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ====================== 邮箱验证码认证 ======================

class SendCodeRequest(BaseModel):
    """发送验证码请求 — 仅用于注册"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    purpose: str = Field(default="register", pattern=r'^register$')  # 仅允许 register


class VerifyCodeRequest(BaseModel):
    """验证码校验 + 注册请求 — 含密码"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    code: str = Field(..., pattern=r'^\d{6}$')
    password: str = Field(..., min_length=6, max_length=128)
    confirm_password: str = Field(..., min_length=6, max_length=128)
