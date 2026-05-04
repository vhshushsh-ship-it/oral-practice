from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import dashscope
from dashscope.audio.asr import Recognition
from dashscope import Generation
import tempfile
import os
from http import HTTPStatus
from dotenv import load_dotenv

load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

app = FastAPI()

# ===== ASR =====
def speech_to_text(file_path):
    recognition = Recognition(
        model="paraformer-realtime-v2",
        format="wav",
        sample_rate=16000,
        language_hints=["en"],
    )
    result = recognition.call(file_path)

    if result.status_code != HTTPStatus.OK:
        return ""

    sentences = result.get_sentence()
    if not sentences:
        return ""

    return " ".join([s["text"] for s in sentences]).strip()

# ===== Agent =====
def agent_reply(user_text):
    response = Generation.call(
        model="qwen-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly English speaking partner."},
            {"role": "user", "content": user_text}
        ],
        result_format="message"
    )

    return response.output.choices[0].message["content"]

# ===== API =====
@app.post("/chat")
async def chat(audio: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    text = speech_to_text(tmp_path)

    if not text:
        return JSONResponse({"text": "", "reply": "Sorry, I didn't catch that."})

    reply = agent_reply(text)

    return {
        "text": text,
        "reply": reply
    }