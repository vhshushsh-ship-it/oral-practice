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

# 解决 Windows 报错
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ================= 配置 =================
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

# 初始化 TTS
# engine = pyttsx3.init()
# engine.setProperty("rate", 170)

# ================= 语音播报 =================
def speak(text):
    try:
        engine = pyttsx3.init()   # ✅ 每次重新创建
        engine.setProperty("rate", 170)

        engine.say(text)
        engine.runAndWait()

        engine.stop()  # ✅ 释放资源

    except Exception as e:
        print("❌ TTS错误:", e)

# ================= 录音 =================
def record_audio(filename="input.wav", duration=4, fs=16000):
    print("🎤 开始说话...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()
    wav.write(filename, fs, audio)
    return filename

# ================= ASR =================
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

    # ✅ 防止 None
    if not sentences:
        return ""

    text = " ".join([item.get("text", "") for item in sentences]).strip()
    return text

# ================= 退出判断 =================
def is_exit(text):
    if not text:
        return False

    text = text.lower()

    exit_keywords = [
        "exit", "quit", "bye", "goodbye",
        "stop", "end", "退出", "结束"
    ]

    return any(word in text for word in exit_keywords)

# ================= Agent =================
def agent_reply(user_text, scene="restaurant"):
    system_prompt = f"""
You are a real person in a {scene} scenario.

Rules:
- Speak naturally like a human
- Keep it short (1-2 sentences)
- If user makes a mistake:
  briefly correct it naturally
- Continue the conversation

Example:
User: I very like coffee
You: Oh, you mean "I really like coffee"? Nice! What kind do you like?
"""

    response = Generation.call(
        model="qwen-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        result_format="message"
    )

    return response.output.choices[0].message["content"]

# ================= 主程序 =================
if __name__ == "__main__":
    scene = "restaurant"

    print("🎭 SceneTalk AI 已启动")
    print("👉 说 'exit' / 'bye' / '结束' 可以退出\n")

    while True:
        audio_file = record_audio()

        text = asr(audio_file)

        if not text:
            print("❌ 没识别到内容，请再说一次\n")
            continue

        print("🧑 You:", text)

        # ✅ 退出
        if is_exit(text):
            print("👋 对话结束")
            speak("Goodbye! See you next time.")
            break

        reply = agent_reply(text, scene=scene)

        print("🤖 AI:", reply, "\n")

        speak(reply)