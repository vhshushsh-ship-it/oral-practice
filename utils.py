import os
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from dashscope import Generation
import chromadb
from datetime import datetime
from pydub import AudioSegment

import json


load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
memory_collection = chroma_client.get_or_create_collection(name="scene_talk_memory")

def save_uploaded_audio(upload_file, save_dir="./temp_audio"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = f"input_{int(datetime.now().timestamp() * 1000)}.wav"
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path

def convert_audio(input_path, output_path, target_sr=16000):
    # 自动转成16000Hz单声道WAV
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_frame_rate(target_sr).set_channels(1)
    audio.export(output_path, format="wav")
    return output_path

# def asr(file_path):
#     # 先转换格式
#     converted_path = file_path.replace(".wav", "_converted.wav")
#     try:
#         convert_audio(file_path, converted_path)
#     except Exception as e:
#         print("❌ 音频转换失败:", e)
#         return ""

#     # 调用ASR
#     recognition = Recognition(
#         model="paraformer-realtime-v2",
#         format="wav",
#         sample_rate=16000,
#         language_hints=["en"],
#         callback=None,
#     )
#     result = recognition.call(converted_path)
#     os.remove(converted_path) # 清理临时文件
#     if result.status_code != HTTPStatus.OK:
#         return ""
#     sentences = result.get_sentence()
#     return " ".join([item.get("text", "") for item in sentences]).strip() if sentences else ""
def asr(file_path):
    # 新增：自动转换为16000Hz单声道WAV
    converted_path = file_path.replace(".wav", "_converted.wav")
    try:
        convert_audio(file_path, converted_path)
    except Exception as e:
        print("❌ 音频转换失败:", e)
        return ""

    # 调用ASR识别
    recognition = Recognition(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000,
        language_hints=["en"],
        callback=None,
    )
    result = recognition.call(converted_path)
    
    # 清理临时转换文件
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
        flat_docs = [item for sublist in docs for item in sublist] if isinstance(docs, list) else docs
        return "\n".join(flat_docs[-limit:]) if flat_docs else ""
    except Exception as e:
        print("❌ 读取记忆失败:", e)
        return ""

# def agent_reply(user_text, scene="restaurant"):
#     memory_context = get_memory_context()
#     system_prompts = {
#         "restaurant": "You are a waiter. Speak naturally, help order food, keep it short (1-2 sentences).",
#         "interview": "You are an interviewer. Ask challenging questions, keep it professional.",
#         "hotel": "You are a receptionist. Help check in, be polite and short."
#     }
#     system_prompt = system_prompts.get(scene, "You are a helpful English speaker.")
#     if memory_context:
#         system_prompt += f"\n\nConversation memory:\n{memory_context}"
#     response = Generation.call(
#         model="qwen-turbo",
#         messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
#         result_format="message"
#     )
#     return response.output.choices[0].message["content"]

from dashscope import Generation
import json

def agent_reply(user_text, scene, conversation_history=None):
    # ---------------------- 1. 场景角色定义（强化场景感，贴合口语练习） ----------------------
    scene_roles = {
        "restaurant": """你是餐厅的服务员，正在和顾客对话，你需要：
1. 全程使用英文，语气友好专业，符合餐厅服务员的身份
2. 记住对话历史，根据顾客之前的对话回答，比如顾客点过的餐品、需求
3. 对话连贯，符合真实餐厅点餐场景，比如顾客点了苹果，你可以问是否需要切片、打包
4. 不要跳出角色，不要说和场景无关的内容
5. 回答简洁自然，适合口语练习，用短句，不要复杂从句
""",
        "interview": """你是英语面试官，正在面试应聘者，你需要：
1. 全程使用英文，语气正式礼貌，符合面试官身份
2. 记住对话历史，根据应聘者的回答继续提问，比如问完自我介绍后问工作经历
3. 对话连贯，符合真实面试场景，不要跳出角色
4. 问题循序渐进，适合口语练习，不要太难的问题
""",
        "hotel": """你是酒店前台，正在和顾客办理入住，你需要：
1. 全程使用英文，语气友好专业，符合酒店前台身份
2. 记住对话历史，根据顾客的需求回答，比如顾客说过的入住日期、房型
3. 对话连贯，符合真实酒店办理场景，不要跳出角色
4. 回答简洁自然，适合口语练习
"""
    }

    # 初始化对话历史（如果没有传的话）
    if conversation_history is None:
        conversation_history = []
    
    # ---------------------- 2. 构建带历史的完整Prompt ----------------------
    # 先加上场景角色设定
    prompt = scene_roles.get(scene, scene_roles["restaurant"]) + "\n"
    # 把对话历史按顺序加入，每一轮用户和AI的对话都带上
    for msg in conversation_history:
        if msg["role"] == "user":
            prompt += f"顾客：{msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"服务员：{msg['content']}\n"
    # 加上当前用户的最新输入
    prompt += f"顾客：{user_text}\n服务员："

    # ---------------------- 3. 调用大模型生成回答 ----------------------
    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            max_tokens=200,
            temperature=0.7 # 0.7 让回答自然不生硬，适合口语场景
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
    """英文对话实时翻译成中文（增强版）"""
    if not text.strip():
        return ""
    
    prompt = f"""
    你是一个专业的翻译助手，请将以下英文对话翻译成自然流畅的中文，只输出翻译结果，不要额外解释：
    原文：{text}
    翻译：
    """
    try:
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": prompt}],
            result_format="message",
            max_tokens=200,
            temperature=0.1
        )
        if response.status_code != 200:
            print(f"❌ 翻译接口调用失败: {response.code}, {response.message}")
            return "翻译出错，请重试"
        
        translation = response.output.choices[0].message["content"].strip()
        translation = translation.replace("翻译：", "").strip()
        return translation
    except Exception as e:
        print(f"❌ 翻译函数异常: {str(e)}")
        return "翻译出错，请重试"