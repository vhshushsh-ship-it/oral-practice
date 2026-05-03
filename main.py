
import os
import chromadb
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import dashscope
from dotenv import load_dotenv
from dashscope import Generation

# ================= 配置 =================
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

LLM_MODEL = "qwen-turbo"

# Chroma
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="user_memory")

# ================= 录音 =================
def record_audio(filename="input.wav", duration=5, fs=16000):
    print("🎤 Speak now...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wav.write(filename, fs, audio)
    return filename

# ================= 语音识别（暂用占位） =================
def speech_to_text(file_path):
    # ⚠️ DashScope也有ASR（paraformer），这里先简化
    print("⚠️ 当前用文本模拟语音输入")
    return input("👉 Type what you said (模拟语音): ")

# ================= Agent核心 =================
def agent_reply(user_text, scene="restaurant"):

    system_prompt = f"""
You are an English conversation coach in a {scene} scenario.

You must:
1. Stay in role (e.g., waiter, interviewer)
2. Detect grammar mistakes
3. Correct the sentence
4. Give a more natural version
5. Ask user to repeat

Format:

[Roleplay Reply]
...

[Correction]
...

[Better Sentence]
...

[Try Again]
...
"""

    response = Generation.call(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        result_format="message"
    )

    return response.output.choices[0].message["content"]

# ================= 记忆系统 =================
def save_memory(text):
    collection.add(
        documents=[text],
        ids=[str(hash(text))]
    )

# ================= 主流程 =================
def run():

    print("🎭 SceneTalk AI (DashScope版)")
    print("选择场景: 1. 餐厅 2. 面试 3. 酒店")

    scene_map = {
        "1": "restaurant",
        "2": "job interview",
        "3": "hotel check-in"
    }

    scene_choice = input("👉 选择场景: ")
    scene = scene_map.get(scene_choice, "restaurant")

    while True:
        audio_file = record_audio()

        user_text = speech_to_text(audio_file)

        print(f"\n🧑 You: {user_text}")

        reply = agent_reply(user_text, scene=scene)

        print(f"\n🤖 AI:\n{reply}\n")

        save_memory(user_text)


if __name__ == "__main__":
    run()