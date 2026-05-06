import os
from pathlib import Path
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from dashscope import Generation
import chromadb
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import json
import re
import asyncio
from typing import Optional

# ====================== 全局初始化配置 ======================
app = FastAPI(title="SceneTalk Backend")
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 向量数据库（对话记忆）
chroma_client = chromadb.PersistentClient(path="./chroma_db")
memory_collection = chroma_client.get_or_create_collection(name="scene_talk_memory")

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

# 场景映射（和前端下拉选项一一对应）
SCENE_MAP = {
    "0": "free_talk",       # 英语自由交流
    "1": "restaurant",      # 餐厅点餐用餐
    "2": "interview",       # 职场英文面试
    "3": "hotel",           # 酒店入住办理
    "4": "home_life",       # 日常居家交流
    "5": "directions",      # 出行问路乘车
    "6": "shopping",        # 商场购物逛街
    "7": "medical",         # 看病就医问诊
    "8": "campus",          # 校园师生交流
    "9": "social",          # 日常社交寒暄
    "10": "travel",         # 旅游景点沟通
    "11": "workplace",      # 职场工作沟通
    "12": "service",        # 生活办事咨询
    "13": "phone_chat",     # 电话微信沟通
    "14": "hobbies",        # 兴趣爱好闲聊
    "15": "transport",      # 机场高铁出行
    "16": "housing"         # 租房看房沟通
}

# 单词笔记文件配置
NOTES_FILE = Path(__file__).parent / "word_notes.json"
if not NOTES_FILE.exists():
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

# 单词缓存文件配置
CACHE_FILE = "word_cache.json"
if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# ====================== 核心工具函数 ======================
def clean_ai_reply(text: str) -> str:
    if not text:
        return text
    role_pattern = r'(?:\*+|#)?\s*(?:Waiter|服务员|Interviewer|面试官|Receptionist|前台|AI|Assistant|assistant)\s*[:：]\s*'
    cleaned = re.sub(f'^{role_pattern}', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(f'\n\s*{role_pattern}', '\n', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

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
        "free_talk": """你是一个友好的英语聊天伙伴，全程用英文和用户交流，话题不限，可以和用户聊任何他感兴趣的内容，保持自然、口语化，像朋友一样对话，不要太正式。""",
        "restaurant": """你是餐厅的服务员，全程英文，友好专业，贴合点餐场景，短句口语化。绝对禁止在回答的任何位置添加Waiter:、服务员：等任何角色标识、前缀，只输出纯对话内容，不要任何格式标记。""",
        "interview": """你是英语面试官，全程英文，正式礼貌，循序渐进提问。绝对禁止在回答的任何位置添加Interviewer:、面试官：等任何角色标识、前缀，只输出纯对话内容，不要任何格式标记。""",
        "hotel": """你是酒店前台，全程英文，专业友好，贴合入住场景。绝对禁止在回答的任何位置添加Receptionist:、前台：等任何角色标识、前缀，只输出纯对话内容，不要任何格式标记。""",
        "home_life": """你是用户的居家朋友，全程用英文交流，聊日常居家话题（做饭、打扫、追剧、作息等），保持轻松自然，口语化，像真实朋友对话一样。""",
        "directions": """你是热心的路人/工作人员，全程用英文和用户练习问路、乘车、问路线的场景，贴合出行场景，口语化，友好易懂，回答要清晰简单。""",
        "shopping": """你是商场的店员/导购，全程用英文和用户交流，贴合购物场景（问商品、砍价、问价格/尺寸、退换货等），友好专业，口语化，不要太生硬。""",
        "medical": """你是医生/护士，全程用英文和用户练习看病问诊场景（描述症状、问病情、听医嘱等），专业友好，语气温和，口语化，不要用太复杂的医学术语。""",
        "campus": """你是学校的老师/同学，全程用英文和用户交流，贴合校园场景（上课提问、聊作业、校园活动、师生沟通等），语气自然，口语化，符合校园对话的轻松氛围。""",
        "social": """你是用户的朋友，全程用英文和用户练习日常社交寒暄（打招呼、聊天气、聊近况、互相问候等），轻松自然，像真实的朋友对话一样，不要太正式。""",
        "travel": """你是景点的工作人员/当地向导，全程用英文和用户交流，贴合旅游场景（问路、问景点、买票、聊旅行经历等），友好热情，口语化，回答要实用易懂。""",
        "workplace": """你是职场的同事/领导/客户，全程用英文和用户练习职场沟通（开会、汇报工作、和同事对接、和客户沟通等），正式礼貌，专业得体，口语化，符合职场对话的分寸。""",
        "service": """你是生活服务场所的工作人员（银行、邮局、营业厅等），全程用英文和用户练习办事咨询（办业务、问流程、咨询问题等），专业友好，口语化，回答要清晰易懂。""",
        "phone_chat": """你是用户的朋友/家人/同事，全程用英文和用户练习电话/微信沟通（打电话、语音聊天、约时间、聊日常等），语气自然，像真实的线上聊天一样，不要太生硬。""",
        "hobbies": """你是用户的同好伙伴，全程用英文和用户聊兴趣爱好（运动、游戏、音乐、电影、手工等），保持热情，轻松自然，口语化，主动聊相关话题。""",
        "transport": """你是机场/高铁站的工作人员/乘务员，全程用英文和用户练习出行沟通（值机、安检、问路、问车次/航班、行李问题等），专业友好，口语化，回答要实用清晰。""",
        "housing": """你是房东/中介/室友，全程用英文和用户练习租房看房沟通（问房源、谈价格、聊入住问题、签合同相关等），贴合租房场景，口语化，语气自然。""",
        "dictionary": """你是专业英语词典，仅返回纯JSON，无任何多余文字"""
    }

    if conversation_history is None:
        conversation_history = []
    
    prompt = scene_roles.get(scene, scene_roles["restaurant"]) + "\n"
    for msg in conversation_history:
        if msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"You: {msg['content']}\n"
    prompt += f"User: {user_text}\nYou: "

    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            max_tokens=200,
            temperature=0.7
        )
        raw_reply = response.output.choices[0].message["content"].strip()
        cleaned_reply = clean_ai_reply(raw_reply)
        return cleaned_reply
    except Exception as e:
        print("❌ 模型调用错误:", e)
        return "Sorry, I didn't catch that. Could you repeat?"

def get_initial_message(scene):
    initial_messages = {
        "free_talk": "Hi there! Feel free to talk about anything you like, I'm here to chat in English!",
        "restaurant": "Hello! Welcome. What would you like to order?",
        "interview": "Hello. Please introduce yourself.",
        "hotel": "Welcome. Do you have a reservation?",
        "home_life": "Hey! What's something you usually do at home? I'd love to chat about daily life!",
        "directions": "Hi there! Need help finding a place or asking for directions?",
        "shopping": "Welcome! Looking for something specific today, or just browsing?",
        "medical": "Hello. I'm here to help you practice talking to a doctor. What's on your mind?",
        "campus": "Hi! Let's chat about school life, classes, or anything related to campus!",
        "social": "Hey! Let's practice casual small talk, like greeting people or chatting about your day!",
        "travel": "Welcome! Planning a trip? Let's practice talking about travel and tourist spots!",
        "workplace": "Hi! Let's practice professional conversations for work, like meetings or emails!",
        "service": "Hello! Need help practicing talking to staff at banks, post offices, or other services?",
        "phone_chat": "Hi! Let's practice phone or WeChat conversations, like making plans or catching up!",
        "hobbies": "Hey! What do you like to do in your free time? Let's chat about hobbies!",
        "transport": "Hi! Let's practice talking about airports, trains, or commuting!",
        "housing": "Hello! Let's practice conversations about renting apartments or talking to landlords!"
    }
    return initial_messages.get(scene, "Hello! How can I help you?")

def translate_text(text: str) -> str:
    if not text.strip():
        return ""
    
    prompt = f"翻译英文为自然中文，仅输出结果：{text}"
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

# ====================== 单词缓存工具函数 ======================
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
        
        save_memory(scene, user_text, ai_reply)
        
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

# ====================== 单词笔记接口（兼容新旧格式）======================
# ✅ 新增：支持JSON body接收完整单词数据
@app.post("/notes/add")
async def add_word_note(
    word: Optional[str] = Query(None),
    phonetic: Optional[str] = Query(None),
    meaning: Optional[str] = Query(None),
    body: Optional[dict] = Body(None)
):
    try:
        # 兼容两种格式：Query参数（旧）和 JSON Body（新）
        if body:
            word_data = body
            word = word_data.get("word")
            phonetic = word_data.get("phonetic", "")
            meaning = word_data.get("meaning", "")
            meanings = word_data.get("meanings", [])
            create_time = word_data.get("createTime", int(datetime.now().timestamp() * 1000))
        else:
            # 旧格式兼容
            meanings = []
            create_time = int(datetime.now().timestamp() * 1000)

        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes = json.load(f)
        
        if any(item["word"] == word for item in notes):
            return {"status": "exists", "message": "单词已存在"}
        
        # 保存完整数据
        notes.append({
            "word": word,
            "phonetic": phonetic,
            "meaning": meaning,
            "meanings": meanings,
            "createTime": create_time
        })
        
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
            notes = json.load(f)
            # 给旧数据补充完整字段
            for item in notes:
                if "createTime" not in item:
                    item["createTime"] = int(datetime.now().timestamp() * 1000)
                if "meanings" not in item:
                    item["meanings"] = []
                if "meaning" not in item and item.get("meanings"):
                    item["meaning"] = item["meanings"][0].get("definition", "暂无释义")
            return {"notes": notes}
    except Exception as e:
        print("读取笔记失败:", e)
        return {"notes": []}

# ====================== AI单词查询接口 ======================
@app.post("/word/query")
async def query_word(word: str = Query(...)):
    word = word.lower().strip()
    if not word:
        return {"error": "请输入有效单词"}
    
    cache = load_cache()
    if word in cache:
        print(f"✅ 缓存命中：{word}，直接返回")
        return cache[word]

    print(f"🔍 调用AI查询单词：{word}")
    prompt = f"""
你是专业英语词典，严格只返回纯JSON格式，不要加任何多余的文字、注释、markdown：
{{
  "word": "{word}",
  "phonetic": "美式音标，比如/əˈmeɪkə/",
  "meanings": [
    {{
      "part_of_speech": "词性缩写，比如adj./n./v.",
      "definition": "中文核心释义",
      "example": "英文例句|中文翻译"
    }}
  ]
}}
"""
    max_retries = 2

    for attempt in range(max_retries):
        try:
            raw_result = agent_reply(prompt, "dictionary", [])
            json_match = re.search(r"\{[\s\S]*\}", raw_result)
            if not json_match:
                raise ValueError("AI未返回JSON格式")
            
            clean_json = json_match.group(0)
            clean_json = re.sub(r",\s*([}\]])", r"\1", clean_json)
            clean_json = clean_json.replace("'", '"')
            
            word_data = json.loads(clean_json)
            if not all(key in word_data for key in ["word", "phonetic", "meanings"]):
                raise ValueError("JSON缺少必填字段")
            
            save_cache(word, word_data)
            print(f"✅ 单词{word}已缓存到本地")
            return word_data

        except Exception as e:
            print(f"AI第{attempt+1}次查询失败：{str(e)}")
            if attempt == max_retries - 1:
                return {"error": "单词查询失败，请重试"}
            await asyncio.sleep(0.3)

# ====================== 启动服务 ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)