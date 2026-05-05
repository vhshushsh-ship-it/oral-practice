import os
from pathlib import Path
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from dashscope import Generation
import chromadb
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import json
import re
import asyncio

# ====================== 初始化配置 ======================
app = FastAPI(title="SceneTalk Backend")
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 向量数据库配置
chroma_client = chromadb.PersistentClient(path="./chroma_db")
memory_collection = chroma_client.get_or_create_collection(name="scene_talk_memory")

# CORS跨域配置（修复语音上传问题）
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

# 单词缓存配置
CACHE_FILE = "word_cache.json"
if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# ====================== 核心工具函数 ======================
def save_uploaded_audio(upload_file, save_dir="./temp_audio"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = f"input_{int(datetime.now().timestamp() * 1000)}.wav"
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path

def convert_audio(input_path, output_path, target_sr=16000):
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(target_sr).set_channels(1)
    audio.export(output_path, format="wav")
    return output_path

def asr(file_path):
    converted_path = file_path.replace(".wav", "_converted.wav")
    try:
        convert_audio(file_path, converted_path)
    except Exception as e:
        print("❌ 音频转换失败:", e)
        return ""

    recognition = Recognition(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000,
        language_hints=["en"],
        callback=None,
    )
    result = recognition.call(converted_path)
    
    if os.path.exists(converted_path):
        os.remove(converted_path)

    if result.status_code != HTTPStatus.OK:
        return ""
    sentences = result.get_sentence()
    return " ".join([item.get("text", "") for item in sentences]).strip() if sentences else ""

def is_exit(text):
    exit_keywords = ["exit", "quit", "bye", "goodbye", "stop", "end", "退出", "结束"]
    return any(word in text.lower() for word in exit_keywords) if text else False

# ✅ 修复：函数定义需要 3 个参数 scene, user_text, ai_text
def save_memory(scene, user_text, ai_text):
    memory_text = f"[scene={scene}] user: {user_text} | ai: {ai_text}"
    memory_id = f"{scene}_{int(datetime.now().timestamp() * 1000)}"
    try:
        memory_collection.add(ids=[memory_id], documents=[memory_text])
    except Exception as e:
        print("❌ 记忆保存失败:", e)

def get_memory_context(limit=5):
    try:
        data = memory_collection.get(limit=limit)
        docs = data.get("documents", [])
        return "\n".join(docs[-limit:]) if docs else ""
    except Exception as e:
        print("❌ 读取记忆失败:", e)
        return ""

def agent_reply(user_text, scene, conversation_history=None):
    scene_roles = {
        "restaurant": """你是餐厅的服务员，正在和顾客对话，你需要：
1. 全程使用英文，语气友好专业，符合餐厅服务员的身份
2. 记住对话历史，根据顾客之前的对话回答
3. 对话连贯，符合真实餐厅点餐场景
4. 回答简洁自然，适合口语练习
""",
        "interview": """你是英语面试官，正在面试应聘者：
1. 全程使用英文，语气正式礼貌
2. 根据回答循序渐进提问
3. 适合口语练习
""",
        "hotel": """你是酒店前台，办理入住：
1. 全程使用英文，友好专业
2. 贴合酒店场景
3. 简洁自然
"""
    }

    if conversation_history is None:
        conversation_history = []
    
    prompt = scene_roles.get(scene, scene_roles["restaurant"]) + "\n"
    for msg in conversation_history:
        if msg["role"] == "user":
            prompt += f"顾客：{msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"服务员：{msg['content']}\n"
    prompt += f"顾客：{user_text}\n服务员："

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            max_tokens=200,
            temperature=0.7
        )
        return response.output.choices[0].message["content"].strip()
    except Exception as e:
        print("❌ 模型调用错误:", e)
        return "Sorry, I didn't catch that. Could you repeat?"

def get_initial_message(scene):
    initial_messages = {
        "restaurant": "Hello! Welcome. What would you like to order?",
        "interview": "Hello. Please introduce yourself.",
        "hotel": "Welcome. Do you have a reservation?"
    }
    return initial_messages.get(scene, "Hello! How can I help you?")

def translate_text(text: str) -> str:
    if not text.strip():
        return ""
    
    prompt = f"""翻译英文为自然中文，只输出结果：{text}"""
    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            temperature=0.1
        )
        return response.output.choices[0].message["content"].strip()
    except Exception as e:
        print(f"❌ 翻译失败: {e}")
        return "翻译出错"

# ====================== 缓存工具函数 ======================
def load_cache():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(word, data):
    cache = load_cache()
    cache[word.lower()] = data
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

# ====================== 业务接口 ======================
# 1. 初始化对话
@app.post("/init")
async def init_conversation(scene_choice: str = Form(...)):
    scene = SCENE_MAP.get(scene_choice, "restaurant")
    return {"scene": scene, "initial_message": get_initial_message(scene)}

# 2. ✅ 修复：语音对话接口（save_memory 传全 3 个参数）
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
        
        # ✅ 核心修复：传入 scene + user_text + ai_text
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
        # 保存文本对话记忆
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

# ====================== AI单词查询接口（纯AI+缓存） ======================
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