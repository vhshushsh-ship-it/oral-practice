import os
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from dashscope import Generation
import chromadb
from datetime import datetime

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

def asr(file_path):
    recognition = Recognition(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000,
        language_hints=["en"],
        callback=None,
    )
    result = recognition.call(file_path)
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

def agent_reply(user_text, scene="restaurant"):
    memory_context = get_memory_context()
    system_prompts = {
        "restaurant": "You are a waiter. Speak naturally, help order food, keep it short (1-2 sentences).",
        "interview": "You are an interviewer. Ask challenging questions, keep it professional.",
        "hotel": "You are a receptionist. Help check in, be polite and short."
    }
    system_prompt = system_prompts.get(scene, "You are a helpful English speaker.")
    if memory_context:
        system_prompt += f"\n\nConversation memory:\n{memory_context}"
    response = Generation.call(
        model="qwen-turbo",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
        result_format="message"
    )
    return response.output.choices[0].message["content"]

def get_initial_message(scene):
    initial_messages = {
        "restaurant": "Hello! Welcome. What would you like to order?",
        "interview": "Hello. Please introduce yourself.",
        "hotel": "Welcome. Do you have a reservation?"
    }
    return initial_messages.get(scene, "Hello! How can I help you?")