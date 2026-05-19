import os
from http import HTTPStatus
from dashscope.audio.asr import Recognition
from services.audio_service import convert_audio


def asr(file_path: str) -> str:
    """语音识别：将音频文件转为英文文本"""
    converted_path = file_path.replace(".wav", "_converted.wav")
    try:
        convert_audio(file_path, converted_path)
    except Exception as e:
        print("[ASR ERROR]", e)
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


def is_exit(text: str) -> bool:
    """检查用户输入是否为退出指令"""
    exit_keywords = ["exit", "quit", "bye", "goodbye", "stop", "end", "退出", "结束"]
    return any(word in text.lower() for word in exit_keywords) if text else False
