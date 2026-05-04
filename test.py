import os
from dotenv import load_dotenv
import dashscope
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from dashscope import Generation
import pyttsx3
import asyncio
import chromadb
from datetime import datetime

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# engine = pyttsx3.init()

chroma_client = chromadb.PersistentClient(path="./chroma_db")
memory_collection = chroma_client.get_or_create_collection(name="scene_talk_memory")

def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 170)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print("❌ TTS错误:", e)

def record_audio(filename="input.wav", duration=4, fs=16000):
    print("🎤 开始说话...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    wav.write(filename, fs, audio)
    return filename

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
    if not sentences:
        return ""

    text = " ".join([item.get("text", "") for item in sentences]).strip()
    return text

def is_exit(text):
    if not text:
        return False
    text = text.lower()
    exit_keywords = ["exit", "quit", "bye", "goodbye", "stop", "end", "退出", "结束"]
    return any(word in text for word in exit_keywords)

def save_memory(scene, user_text, ai_text):
    memory_text = f"[scene={scene}] user: {user_text} | ai: {ai_text}"
    memory_id = f"{scene}_{int(datetime.now().timestamp() * 1000)}"
    try:
        memory_collection.add(
            ids=[memory_id],
            documents=[memory_text]
        )
    except Exception as e:
        print("❌ 记忆保存失败:", e)

def get_memory_context(limit=5):
    try:
        data = memory_collection.get(limit=limit)
        docs = data.get("documents", [])
        if not docs:
            return ""

        flat_docs = []
        for item in docs:
            if isinstance(item, list):
                flat_docs.extend(item)
            elif isinstance(item, str):
                flat_docs.append(item)

        return "\n".join(flat_docs[-limit:])

    except Exception as e:
        print("❌ 读取记忆失败:", e)
        return ""

def agent_reply(user_text, scene="restaurant"):
    memory_context = get_memory_context(limit=5)

    if scene == "restaurant":
        system_prompt = """
You are a waiter in a restaurant.

Speak naturally and casually.
Help the customer order food.

If user makes mistakes:
- correct naturally in conversation

Keep it short (1-2 sentences).
"""
    elif scene == "interview":
        system_prompt = """
You are a job interviewer.

Ask challenging questions.
Sometimes interrupt or ask follow-ups.

If user makes mistakes:
- briefly correct and continue

Keep it professional and realistic.
"""
    elif scene == "hotel":
        system_prompt = """
You are a hotel receptionist.

Help the guest check in.

If user makes mistakes:
- correct naturally

Keep it polite and short.
"""
    else:
        system_prompt = "You are a helpful English speaker."

    if memory_context:
        system_prompt += f"\n\nConversation memory:\n{memory_context}\n"

    response = Generation.call(
        model="qwen-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        result_format="message"
    )

    return response.output.choices[0].message["content"]

def choose_scene():
    print("请选择场景：")
    print("1. 餐厅点餐")
    print("2. 英语面试")
    print("3. 酒店入住")

    scene_map = {
        "1": "restaurant",
        "2": "interview",
        "3": "hotel"
    }

    choice = input("👉 输入 1/2/3：").strip()
    return scene_map.get(choice, "restaurant")

if __name__ == "__main__":
    scene = choose_scene()
    print(f"🎯 当前场景：{scene}\n")

    print("🎭 SceneTalk AI 已启动")
    print("👉 说 'exit' / 'bye' / '结束' 可以退出\n")

    if scene == "restaurant":
        speak("Hello! Welcome. What would you like to order?")
    elif scene == "interview":
        speak("Hello. Please introduce yourself.")
    elif scene == "hotel":
        speak("Welcome. Do you have a reservation?")

    while True:
        audio_file = record_audio()
        text = asr(audio_file)

        if not text:
            print("❌ 没识别到内容，请再说一次\n")
            speak("Sorry, I didn't catch that. Could you repeat?")
            continue

        print("🧑 You:", text)

        if is_exit(text):
            print("👋 对话结束")
            speak("Goodbye! See you next time.")
            break

        try:
            reply = agent_reply(text, scene=scene).strip()
            if not reply:
                reply = "Sorry, could you say that again?"
            if len(reply) > 200:
                reply = reply[:200]
        except Exception as e:
            print("❌ Agent错误:", e)
            reply = "Sorry, something went wrong."

        print("🤖 AI:", reply, "\n")

        save_memory(scene, text, reply)
        speak(reply)
