import os
import wave
import struct
from datetime import datetime
from config import DATA_DIR


def save_uploaded_audio(upload_file, save_dir=None) -> str:
    """保存上传的音频文件到临时目录"""
    if save_dir is None:
        save_dir = DATA_DIR / "temp_audio"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    filename = f"input_{int(datetime.now().timestamp() * 1000)}.wav"
    file_path = os.path.join(save_dir, filename)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path


def _read_wav(file_path: str) -> tuple:
    """读取 WAV 文件，返回 (sample_rate, channels, sample_width, samples list)"""
    with wave.open(file_path, "rb") as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    fmt = {1: "b", 2: "h", 4: "i"}[sample_width]
    fmt = f"<{n_frames * channels}{fmt}"
    samples = list(struct.unpack(fmt, raw))
    return sample_rate, channels, sample_width, samples


def _write_wav(file_path: str, sample_rate: int, channels: int, sample_width: int, samples: list) -> None:
    """写入 WAV 文件"""
    fmt = {1: "b", 2: "h", 4: "i"}[sample_width]
    fmt = f"<{len(samples)}{fmt}"
    raw = struct.pack(fmt, *samples)

    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(raw)


def convert_audio(input_path: str, output_path: str, target_sr: int = 16000) -> str:
    """将音频转换为目标采样率的单声道 16-bit WAV，使用线性插值重采样"""
    src_sr, channels, sample_width, samples = _read_wav(input_path)

    # 转换为单声道（取所有声道的平均值）
    if channels > 1:
        mono = []
        for i in range(0, len(samples), channels):
            ch_sum = sum(samples[i + ch] for ch in range(channels))
            mono.append(ch_sum // channels)
        samples = mono
        channels = 1

    # 线性插值重采样到目标采样率（复用前端同款算法）
    if src_sr != target_sr:
        ratio = src_sr / target_sr
        new_len = round(len(samples) / ratio)
        resampled = []
        for i in range(new_len):
            idx = i * ratio
            floor = int(idx)
            ceil = min(floor + 1, len(samples) - 1)
            t = idx - floor
            resampled.append(int(samples[floor] * (1 - t) + samples[ceil] * t))
        samples = resampled

    # 统一输出 16-bit
    if sample_width != 2:
        max_val = 2 ** (8 * sample_width - 1)
        scale = 32767 / max_val
        samples = [int(max(-32768, min(32767, s * scale))) for s in samples]
        sample_width = 2

    _write_wav(output_path, target_sr, 1, 2, samples)
    return output_path
