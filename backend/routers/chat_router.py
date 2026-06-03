import json
import os
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import StreamingResponse
from config import SCENE_MAP, INITIAL_MESSAGES
from services.ai_service import agent_reply, agent_reply_stream
from services.asr_service import asr, is_exit
from services.audio_service import save_uploaded_audio
from services.storage_service import save_memory, search_memories
from services.chat_service import save_chat_session, get_chat_session, delete_chat_session
from db import get_db, release_db
from routers.auth_dependency import get_current_user

router = APIRouter(tags=["chat"])


@router.post("/init")
async def init_conversation(scene_choice: str = Form(...)):
    scene = SCENE_MAP.get(scene_choice, "free_talk")
    return {"scene": scene, "initial_message": INITIAL_MESSAGES.get(scene, "Hello! How can I help you?")}


@router.post("/chat/save")
async def save_chat_history(data: dict, user_id: str = Depends(get_current_user)):
    scene = data.get("scene")
    history = data.get("history", [])
    translations = data.get("translations", [])
    db = await get_db()
    try:
        await save_chat_session(db, user_id, scene, history, translations)
    finally:
        await release_db(db)
    return {"status": "success"}


@router.get("/chat/history")
async def get_chat_history(scene: str, user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        result = await get_chat_session(db, user_id, scene)
    finally:
        await release_db(db)
    return result


@router.get("/chat/clear")
async def clear_chat_history(scene: str, user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        await delete_chat_session(db, user_id, scene)
    finally:
        await release_db(db)
    return {"status": "success"}


def _sse_event(data: str) -> str:
    """Format a Server-Sent Event line."""
    return f"data: {data}\n\n"


@router.post("/chat")
async def chat(
    audio: UploadFile = File(...),
    scene: str = Form(...),
    conversation_history: str = Form("[]"),
    stream: str = Form("false"),
    user_id: str = Depends(get_current_user),
):
    try:
        audio_path = save_uploaded_audio(audio)
        user_text = asr(audio_path)

        if is_exit(user_text):
            if stream.lower() == "true":
                def exit_stream():
                    yield _sse_event(json.dumps({"token": "Goodbye!"}))
                    yield _sse_event("[DONE]")
                return StreamingResponse(exit_stream(), media_type="text/event-stream")
            return {"user_text": user_text, "ai_text": "Goodbye!"}

        history = json.loads(conversation_history)
        memories = search_memories(scene, user_text, user_id)

        if stream.lower() == "true":
            def generate():
                # 先发送 ASR 识别结果，让前端展示用户消息
                yield _sse_event(json.dumps({"user_text": user_text}))
                full_text = ""
                try:
                    for token in agent_reply_stream(user_text, scene, history, memory_context=memories):
                        full_text += token
                        yield _sse_event(json.dumps({"token": token}))
                    yield _sse_event("[DONE]")
                except Exception as e:
                    print(f"[STREAM ERROR] {e}")
                    if not full_text:
                        yield _sse_event(json.dumps({"token": "Sorry, I can't reply now."}))
                        yield _sse_event("[DONE]")
                finally:
                    if full_text:
                        save_memory(scene, user_text, full_text, user_id)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)

            return StreamingResponse(generate(), media_type="text/event-stream")

        # Non-streaming fallback
        ai_reply = agent_reply(user_text, scene, history, memory_context=memories)
        save_memory(scene, user_text, ai_reply, user_id)

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
    stream: str = Form("false"),
    user_id: str = Depends(get_current_user),
):
    try:
        history = json.loads(conversation_history)
        memories = search_memories(scene, user_text, user_id)

        if stream.lower() == "true":
            def generate():
                full_text = ""
                try:
                    for token in agent_reply_stream(user_text, scene, history, memory_context=memories):
                        full_text += token
                        yield _sse_event(json.dumps({"token": token}))
                    yield _sse_event("[DONE]")
                except Exception as e:
                    print(f"[STREAM ERROR] {e}")
                    if not full_text:
                        yield _sse_event(json.dumps({"token": "Sorry, I can't reply now."}))
                        yield _sse_event("[DONE]")
                finally:
                    if full_text:
                        save_memory(scene, user_text, full_text, user_id)

            return StreamingResponse(generate(), media_type="text/event-stream")

        # Non-streaming fallback
        ai_reply_text = agent_reply(user_text, scene, history, memory_context=memories)
        save_memory(scene, user_text, ai_reply_text, user_id)
        return {"user_text": user_text, "ai_text": ai_reply_text}
    except Exception as e:
        print(f"文本对话失败: {e}")
        return {"user_text": user_text, "ai_text": "Sorry, I can't reply now."}
