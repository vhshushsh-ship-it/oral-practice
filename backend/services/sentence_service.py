import json
from datetime import datetime
from pathlib import Path
from config import SENTENCE_BASE_DIR


def _get_sentences_path(user_id: str) -> Path:
    """获取用户句子收藏文件路径"""
    SENTENCE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return SENTENCE_BASE_DIR / f"{user_id}.json"


def _init_sentences_file(path: Path) -> None:
    """初始化空的句子收藏文件"""
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def read_sentences(user_id: str) -> list:
    """读取用户所有收藏句子"""
    path = _get_sentences_path(user_id)
    _init_sentences_file(path)
    with open(path, "r", encoding="utf-8") as f:
        sentences = json.load(f)
    # 补齐旧数据缺失字段
    for item in sentences:
        if "createTime" not in item:
            item["createTime"] = int(datetime.now().timestamp() * 1000)
        if "translation" not in item:
            item["translation"] = ""
    return sentences


def write_sentences(sentences: list, user_id: str) -> None:
    """写入用户句子收藏（全量覆盖）"""
    path = _get_sentences_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sentences, f, ensure_ascii=False, indent=2)


def add_sentence(item: dict, user_id: str) -> tuple[str, str]:
    """添加句子收藏，依据 text 去重"""
    sentences = read_sentences(user_id)
    if any(s["text"] == item["text"] for s in sentences):
        return ("exists", "句子已收藏")
    if "createTime" not in item:
        item["createTime"] = int(datetime.now().timestamp() * 1000)
    sentences.append(item)
    write_sentences(sentences, user_id)
    return ("success", "收藏成功")


def delete_sentence(index: int, user_id: str) -> tuple[str, str]:
    """按索引删除句子收藏"""
    sentences = read_sentences(user_id)
    if index < 0 or index >= len(sentences):
        return ("error", "索引无效")
    sentences.pop(index)
    write_sentences(sentences, user_id)
    return ("success", "删除成功")


def clear_sentences(user_id: str) -> tuple[str, str]:
    """清空用户所有句子收藏"""
    write_sentences([], user_id)
    return ("success", "清空成功")
