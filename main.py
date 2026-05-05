from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from utils import save_uploaded_audio, asr, is_exit, save_memory, agent_reply, get_initial_message, translate_text
import os
import json
from pathlib import Path

# -------------- 1. 初始化FastAPI（只初始化一次，和原来的代码合并）--------------
app = FastAPI(title="SceneTalk Backend")

# 加CORS跨域，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 场景映射
SCENE_MAP = {"1": "restaurant", "2": "interview", "3": "hotel"}

# -------------- 2. 单词笔记文件配置（放在app初始化之后）--------------
NOTES_FILE = Path(__file__).parent / "word_notes.json"
# 确保笔记文件存在，不存在则创建空文件
if not NOTES_FILE.exists():
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# -------------- 3. 原有接口（场景初始化/聊天/翻译）--------------
@app.post("/init")
async def init_conversation(scene_choice: str = Form(...)):
    scene = SCENE_MAP.get(scene_choice, "restaurant")
    return {"scene": scene, "initial_message": get_initial_message(scene)}

@app.post("/chat")
async def chat(audio: UploadFile = File(...), scene: str = Form(...), conversation_history: str = Form("[]")):
    # 原有语音聊天逻辑（你的代码保留即可，这里简化示例）
    audio_path = save_uploaded_audio(audio)
    user_text = asr(audio_path)
    if is_exit(user_text):
        return {"user_text": user_text, "ai_text": "好的，再见！"}
    
    history = json.loads(conversation_history)
    ai_reply = agent_reply(user_text, scene, history)
    save_memory(audio_path)
    return {"user_text": user_text, "ai_text": ai_reply}

@app.post("/translate")
async def translate(text: str = Form(...)):
    translation = translate_text(text)
    return {"translation": translation}

# -------------- 单词笔记接口 --------------
# 1. 添加单词到文件（修复：声明为Query参数）
@app.post("/notes/add")
async def add_word_note(
    word: str = Query(...), 
    phonetic: str = Query(...), 
    meaning: str = Query(...)
):
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
        if any(item["word"] == word for item in notes):
            return {"status": "exists", "message": "单词已存在"}
        notes.append({"word": word, "phonetic": phonetic, "meaning": meaning})
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        return {"status": "success", "message": "保存成功"}
    except Exception as e:
        print("添加单词失败:", e)
        return {"status": "error", "message": "保存失败"}

# 2. 删除单个单词（修复：声明为Query参数）
@app.post("/notes/delete")
async def delete_word_note(word: str = Query(...)):
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
        new_notes = [item for item in notes if item["word"] != word]
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(new_notes, f, ensure_ascii=False, indent=2)
        return {"status": "success", "message": "删除成功"}
    except Exception as e:
        print("删除单词失败:", e)
        return {"status": "error", "message": "删除失败"}

# 3. 清空所有单词（无需参数，保持不变）
@app.post("/notes/clear")
async def clear_all_notes():
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return {"status": "success", "message": "清空成功"}
    except Exception as e:
        print("清空笔记失败:", e)
        return {"status": "error", "message": "清空失败"}
    
# 接口4：获取所有单词笔记（可选，用于前端同步）
@app.get("/notes/all")
async def get_all_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
        return {"notes": notes}
    except Exception as e:
        print("获取笔记失败:", e)
        return {"notes": []}

# -------------- 5. 启动服务（和原来的代码保持一致）--------------
if __name__ == "__main__":
    import uvicorn
    # 启动服务，固定本机地址
    uvicorn.run(app, host="127.0.0.1", port=8000)