import json
from datetime import datetime
from config import memory_collection, NOTES_FILE, CACHE_FILE


# ====================== ChromaDB 记忆 ======================
def save_memory(scene: str, user_text: str, ai_text: str) -> None:
    """保存对话记忆到 ChromaDB"""
    memory_text = f"[scene={scene}] user: {user_text} | ai: {ai_text}"
    memory_id = f"{scene}_{int(datetime.now().timestamp() * 1000)}"
    try:
        memory_collection.add(ids=[memory_id], documents=[memory_text])
    except Exception as e:
        print("❌ 记忆保存失败:", e)


def get_memory_context(limit: int = 5) -> str:
    """从 ChromaDB 获取最近的对话记忆"""
    try:
        data = memory_collection.get(limit=limit)
        docs = data.get("documents", [])
        return "\n".join(docs[-limit:]) if docs else ""
    except Exception as e:
        print("❌ 读取记忆失败:", e)
        return ""


# ====================== 单词缓存 ======================
def load_cache() -> dict:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(word: str, data: dict) -> None:
    cache = load_cache()
    cache[word.lower()] = data
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ====================== 单词笔记持久化 ======================
def read_notes() -> list:
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        notes = json.load(f)
    for item in notes:
        if "createTime" not in item:
            item["createTime"] = int(datetime.now().timestamp() * 1000)
        if "meanings" not in item:
            item["meanings"] = []
        if "meaning" not in item and item.get("meanings"):
            item["meaning"] = item["meanings"][0].get("definition", "暂无释义")
    return notes


def write_notes(notes: list) -> None:
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(item: dict) -> tuple[str, str]:
    notes = read_notes()
    if any(n["word"] == item["word"] for n in notes):
        return ("exists", "单词已存在")
    notes.append(item)
    write_notes(notes)
    return ("success", "保存成功")


def delete_note(word: str) -> tuple[str, str]:
    notes = read_notes()
    new_notes = [n for n in notes if n["word"] != word]
    write_notes(new_notes)
    return ("success", "删除成功")


def clear_notes() -> tuple[str, str]:
    write_notes([])
    return ("success", "清空成功")
