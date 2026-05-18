import json
import os
from fastapi import APIRouter, UploadFile, File, Form
from config import SCENE_MAP, CHAT_DIR, INITIAL_MESSAGES
from services.ai_service import agent_reply
from services.asr_service import asr, is_exit
from services.audio_service import save_uploaded_audio
from services.storage_service import save_memory

router = APIRouter(tags=["chat"])


@router.post("/init")
async def init_conversation(scene_choice: str = Form(...)):
    scene = SCENE_MAP.get(scene_choice, "free_talk")
    return {"scene": scene, "initial_message": INITIAL_MESSAGES.get(scene, "Hello! How can I help you?")}


@router.post("/chat/save")
async def save_chat_history(data: dict):
    scene = data.get("scene")
    history = data.get("history", [])
    file_path = CHAT_DIR / f"{scene}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return {"status": "success"}


@router.get("/chat/history")
async def get_chat_history(scene: str):
    file_path = CHAT_DIR / f"{scene}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []
    return {"history": history}


@router.get("/chat/clear")
async def clear_chat_history(scene: str):
    file_path = CHAT_DIR / f"{scene}.json"
    if file_path.exists():
        os.remove(file_path)
    return {"status": "success"}


@router.post("/chat")
async def chat(
    audio: UploadFile = File(...),
    scene: str = Form(...),
    conversation_history: str = Form("[]"),
):
    try:
        audio_path = save_uploaded_audio(audio)
        user_text = asr(audio_path)

        if is_exit(user_text):
            return {"user_text": user_text, "ai_text": "Goodbye!"}

        history = json.loads(conversation_history)
        ai_reply = agent_reply(user_text, scene, history)

        save_memory(scene, user_text, ai_reply)

        if os.path.exists(audio_path):
            os.remove(audio_path)

        return {"user_text": user_text, "ai_text": ai_reply}

    except Exception as e:
        print(f"【语音接口报错】: {str(e)}")
        return {"user_text": "语音识别失败", "ai_text": "Sorry, I can't recognize your voice."}


@router.post("/chat_text")
async def chat_text(
    user_text: str = Form(...),
    scene: str = Form(...),
    conversation_history: str = Form("[]"),
):
    try:
        history = json.loads(conversation_history)
        ai_reply_text = agent_reply(user_text, scene, history)
        save_memory(scene, user_text, ai_reply_text)
        return {"user_text": user_text, "ai_text": ai_reply_text}
    except Exception as e:
        print(f"文本对话失败: {e}")
        return {"user_text": user_text, "ai_text": "Sorry, I can't reply now."}
