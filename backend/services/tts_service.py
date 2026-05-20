import asyncio
import tempfile
import os
from pathlib import Path


async def generate_tts_audio(text: str, rate: float = 1.0) -> bytes:
    """使用 edge-tts 生成 MP3 音频，返回音频字节"""
    import edge_tts

    # 映射语速: 1.0 → "+0%", 0.75 → "-25%", 1.5 → "+50%"
    rate_str = f"{int((rate - 1.0) * 100):+d}%"

    voice = "en-US-AriaNeural"
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await communicate.save(tmp_path)
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(tmp_path)
