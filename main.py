from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import save_uploaded_audio, asr, is_exit, save_memory, agent_reply, get_initial_message, translate_text
import os
import json

app = FastAPI(title="SceneTalk Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCENE_MAP = {"1": "restaurant", "2": "interview", "3": "hotel"}

@app.post("/init")
async def init_conversation(scene_choice: str = Form(...)):
    scene = SCENE_MAP.get(scene_choice, "restaurant")
    return {"scene": scene, "initial_message": get_initial_message(scene)}



@app.post("/chat")
async def chat(audio: UploadFile = File(...), scene: str = Form(...), conversation_history: str = Form("[]")):
    audio_path = save_uploaded_audio(audio)
    user_text = asr(audio_path)
    
    if not user_text:
        os.remove(audio_path)
        return {"user_text": "", "ai_text": "Sorry, I didn't catch that. Could you repeat?", "is_exit": False}
    
    if is_exit(user_text):
        os.remove(audio_path)
        return {"user_text": user_text, "ai_text": "Goodbye! See you next time.", "is_exit": True}
    
    # 解析前端传来的对话历史（JSON字符串转成列表）
    try:
        history = json.loads(conversation_history)
    except:
        history = []
    
    # 调用带记忆的agent_reply函数
    try:
        ai_text = agent_reply(user_text, scene, history).strip()
        ai_text = ai_text[:200] if len(ai_text) > 200 else ai_text
        ai_text = ai_text or "Sorry, could you say that again?"
    except Exception as e:
        print("❌ Agent错误:", e)
        ai_text = "Sorry, something went wrong."
    
    save_memory(scene, user_text, ai_text)
    os.remove(audio_path)
    return {"user_text": user_text, "ai_text": ai_text, "is_exit": False}


# @app.post("/chat_text")
# async def chat_text(user_text: str = Form(...), scene: str = Form(...)):
#     if not user_text:
#         return {"user_text": "", "ai_text": "Sorry, I didn't catch that. Could you repeat?", "is_exit": False}
    
#     if is_exit(user_text):
#         return {"user_text": user_text, "ai_text": "Goodbye! See you next time.", "is_exit": True}

#     try:
#         ai_text = agent_reply(user_text, scene).strip()
#         ai_text = ai_text[:200] if len(ai_text) > 200 else ai_text
#         ai_text = ai_text or "Sorry, could you say that again?"
#     except Exception as e:
#         print("❌ Agent错误:", e)
#         ai_text = "Sorry, something went wrong."

#     save_memory(scene, user_text, ai_text)
#     return {"user_text": user_text, "ai_text": ai_text, "is_exit": False}

@app.post("/chat_text")
async def chat_text(user_text: str = Form(...), scene: str = Form(...), conversation_history: str = Form("[]")):
    if not user_text:
        return {"user_text": "", "ai_text": "Sorry, I didn't catch that. Could you repeat?", "is_exit": False}
    
    if is_exit(user_text):
        return {"user_text": user_text, "ai_text": "Goodbye! See you next time.", "is_exit": True}

    # 解析对话历史
    try:
        history = json.loads(conversation_history)
    except:
        history = []
    
    # 调用带记忆的agent_reply函数
    try:
        ai_text = agent_reply(user_text, scene, history).strip()
        ai_text = ai_text[:200] if len(ai_text) > 200 else ai_text
        ai_text = ai_text or "Sorry, could you say that again?"
    except Exception as e:
        print("❌ Agent错误:", e)
        ai_text = "Sorry, something went wrong."

    save_memory(scene, user_text, ai_text)
    return {"user_text": user_text, "ai_text": ai_text, "is_exit": False}

# 实时翻译接口（修正版）
@app.post("/translate")
async def api_translate(text: str = Form(...)):
    if not text or not text.strip():
        return {"translation": ""}
    try:
        translation = translate_text(text)
        return {"translation": translation}
    except Exception as e:
        print("❌ 翻译接口异常:", e)
        return {"translation": "翻译出错，请重试"}

# ====================== 修复点：新增启动代码 ======================
if __name__ == "__main__":
    import uvicorn
    # 启动服务，固定本机地址
    uvicorn.run(app, host="127.0.0.1", port=8000)