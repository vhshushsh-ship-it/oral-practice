import os
from pathlib import Path
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from dashscope import Generation
import chromadb
from datetime import datetime
from pydub import AudioSegment
import json

# ====================== 全局配置 ======================
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 向量数据库（对话记忆）
chroma_client = chromadb.PersistentClient(path="./chroma_db")
memory_collection = chroma_client.get_or_create_collection(name="scene_talk_memory")

# 单词缓存配置
CACHE_FILE = "word_cache.json"
if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# ====================== 音频处理工具 ======================
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

# ====================== 语音识别(ASR) ======================
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

# ====================== 对话工具 ======================
def is_exit(text):
    exit_keywords = ["exit", "quit", "bye", "goodbye", "stop", "end", "退出", "结束"]
    return any(word in text.lower() for word in exit_keywords) if text else False

# 保存对话记忆
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

# AI对话回复
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

# 场景初始化话术
def get_initial_message(scene):
    initial_messages = {
        "restaurant": "Hello! Welcome. What would you like to order?",
        "interview": "Hello. Please introduce yourself.",
        "hotel": "Welcome. Do you have a reservation?"
    }
    return initial_messages.get(scene, "Hello! How can I help you?")

# 翻译工具
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

# ====================== 单词缓存工具 ======================
def load_cache():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cache(word, data):
    cache = load_cache()
    cache[word.lower()] = data
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)