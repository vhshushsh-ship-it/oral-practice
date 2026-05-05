import os
import json
import re
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware

# 从工具文件导入所有需要的函数
from utils import (
    save_uploaded_audio,
    asr,
    is_exit,
    save_memory,
    agent_reply,
    get_initial_message,
    translate_text,
    load_cache,
    save_cache
)

# ====================== FastAPI 初始化 ======================
app = FastAPI(title="SceneTalk Backend")

# CORS跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 场景映射
SCENE_MAP = {"1": "restaurant", "2": "interview", "3": "hotel"}

# 单词笔记文件配置
NOTES_FILE = Path(__file__).parent / "word_notes.json"
if not NOTES_FILE.exists():
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# ====================== 业务接口 ======================
# 1. 初始化对话
@app.post("/init")
async def init_conversation(scene_choice: str = Form(...)):
    scene = SCENE_MAP.get(scene_choice, "restaurant")
    return {"scene": scene, "initial_message": get_initial_message(scene)}

# 2. 语音对话接口
@app.post("/chat")
async def chat(
    audio: UploadFile = File(...), 
    scene: str = Form(...), 
    conversation_history: str = Form("[]")
):
    try:
        audio_path = save_uploaded_audio(audio)
        user_text = asr(audio_path)
        
        if is_exit(user_text):
            return {"user_text": user_text, "ai_text": "Goodbye!"}
        
        history = json.loads(conversation_history)
        ai_reply = agent_reply(user_text, scene, history)
        
        # 保存对话记忆
        save_memory(scene, user_text, ai_reply)
        
        # 清理临时音频
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        return {"user_text": user_text, "ai_text": ai_reply}

    except Exception as e:
        print(f"【语音接口报错】: {str(e)}")
        return {"user_text": "语音识别失败", "ai_text": "Sorry, I can't recognize your voice."}

# 3. 文本对话接口
@app.post("/chat_text")
async def chat_text(
    user_text: str = Form(...), 
    scene: str = Form(...), 
    conversation_history: str = Form("[]")
):
    try:
        history = json.loads(conversation_history)
        ai_reply_text = agent_reply(user_text, scene, history)
        save_memory(scene, user_text, ai_reply_text)
        return {"user_text": user_text, "ai_text": ai_reply_text}
    except Exception as e:
        print(f"文本对话失败: {e}")
        return {"user_text": user_text, "ai_text": "Sorry, I can't reply now."}

# 4. 翻译接口
@app.post("/translate")
async def translate(text: str = Form(...)):
    return {"translation": translate_text(text)}

# ====================== 单词笔记接口 ======================
@app.post("/notes/add")
async def add_word_note(word: str = Query(...), phonetic: str = Query(...), meaning: str = Query(...)):
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

@app.post("/notes/clear")
async def clear_all_notes():
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return {"status": "success", "message": "清空成功"}
    except Exception as e:
        print("清空失败:", e)
        return {"status": "error", "message": "清空失败"}

@app.get("/notes/all")
async def get_all_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            return {"notes": json.load(f)}
    except:
        return {"notes": []}

# ====================== AI单词查询接口 ======================
@app.post("/word/query")
async def query_word(word: str = Query(...)):
    word = word.lower().strip()
    cache = load_cache()

    if word in cache:
        return cache[word]

    prompt = f"""
你是专业英语词典，只返回纯JSON，无任何多余文字：
{{
  "word": "{word}",
  "phonetic": "美式音标",
  "meanings": [
    {{
      "part_of_speech": "n./v./adj./adv.",
      "definition": "中文释义",
      "example": "英文句子|中文翻译"
    }}
  ]
}}
"""
    max_retries = 2

    for attempt in range(max_retries):
        try:
            raw = agent_reply(prompt, "dictionary", [])
            json_match = re.search(r"\{.*\}", raw, re.DOTALL)
            if not json_match:
                raise ValueError("未返回JSON")
                
            clean = json_match.group(0)
            clean = re.sub(r",\s*([}\]])", r"\1", clean)
            clean = clean.replace("'", '"')
            
            data = json.loads(clean)
            if not all(k in data for k in ["word", "phonetic", "meanings"]):
                raise ValueError("缺少字段")
            
            save_cache(word, data)
            return data

        except Exception as e:
            print(f"AI第{attempt+1}次失败：{e}")
            if attempt == max_retries - 1:
                return {"error": "查询失败，请重试"}
            await asyncio.sleep(0.5)

# ====================== 启动服务 ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)