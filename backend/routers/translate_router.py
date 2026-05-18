from fastapi import APIRouter, Form
from services.ai_service import translate_text, translate_to_english

router = APIRouter(tags=["translate"])


@router.post("/translate")
async def translate(text: str = Form(...)):
    return {"translation": translate_text(text)}


@router.post("/translate_to_en")
async def translate_to_en(text: str = Form(...)):
    return {"translation": translate_to_english(text)}
