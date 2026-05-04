from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from utils import save_uploaded_audio, asr, is_exit, save_memory, agent_reply, get_initial_message
import os

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
async def chat(audio: UploadFile = File(...), scene: str = Form(...)):
    audio_path = save_uploaded_audio(audio)
    user_text = asr(audio_path)
    
    if not user_text:
        os.remove(audio_path)
        return {"user_text": "", "ai_text": "Sorry, I didn't catch that. Could you repeat?", "is_exit": False}
    
    if is_exit(user_text):
        os.remove(audio_path)
        return {"user_text": user_text, "ai_text": "Goodbye! See you next time.", "is_exit": True}
    
    try:
        ai_text = agent_reply(user_text, scene).strip()
        ai_text = ai_text[:200] if len(ai_text) > 200 else ai_text
        ai_text = ai_text or "Sorry, could you say that again?"
    except Exception as e:
        print("❌ Agent错误:", e)
        ai_text = "Sorry, something went wrong."
    
    save_memory(scene, user_text, ai_text)
    os.remove(audio_path)
    return {"user_text": user_text, "ai_text": ai_text, "is_exit": False}

@app.post("/chat_text")
async def chat_text(user_text: str = Form(...), scene: str = Form(...)):
    if not user_text:
        return {"user_text": "", "ai_text": "Sorry, I didn't catch that. Could you repeat?", "is_exit": False}
    
    if is_exit(user_text):
        return {"user_text": user_text, "ai_text": "Goodbye! See you next time.", "is_exit": True}

    try:
        ai_text = agent_reply(user_text, scene).strip()
        ai_text = ai_text[:200] if len(ai_text) > 200 else ai_text
        ai_text = ai_text or "Sorry, could you say that again?"
    except Exception as e:
        print("❌ Agent错误:", e)
        ai_text = "Sorry, something went wrong."

    save_memory(scene, user_text, ai_text)
    return {"user_text": user_text, "ai_text": ai_text, "is_exit": False}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)