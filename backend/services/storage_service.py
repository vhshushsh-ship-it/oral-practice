import json
from datetime import datetime
from pathlib import Path
from config import memory_collection, NOTES_BASE_DIR, CACHE_FILE


# ====================== ChromaDB 记忆 ======================
def save_memory(scene: str, user_text: str, ai_text: str, user_id: str = "") -> None:
    """保存对话记忆到 ChromaDB（按用户隔离）"""
    memory_text = f"user: {user_text} | ai: {ai_text}"
    memory_id = f"{user_id}_{scene}_{int(datetime.now().timestamp() * 1000)}" if user_id else f"{scene}_{int(datetime.now().timestamp() * 1000)}"
    metadata = {"scene": scene}
    if user_id:
        metadata["user_id"] = user_id
    try:
        memory_collection.add(
            ids=[memory_id],
            documents=[memory_text],
            metadatas=[metadata],
        )
    except Exception as e:
        print("[MEMORY SAVE ERROR]", e)


def search_memories(scene: str, query_text: str, user_id: str = "", n_results: int = 3) -> list[str]:
    """用语义相似度搜索该场景下最相关的历史对话（按用户隔离）"""
    try:
        if user_id:
            results = memory_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"$and": [{"scene": scene}, {"user_id": user_id}]},
            )
        else:
            results = memory_collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where={"scene": scene},
            )
        docs = results.get("documents", [[]])
        return [d for d in docs[0] if d] if docs and docs[0] else []
    except Exception as e:
        # Fallback: old records may lack user_id metadata
        if user_id:
            try:
                results = memory_collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where={"scene": scene},
                )
                docs = results.get("documents", [[]])
                return [d for d in docs[0] if d] if docs and docs[0] else []
            except Exception:
                pass
        print("[MEMORY SEARCH ERROR]", e)
        return []


# ====================== 单词缓存（共享，无需用户隔离） ======================
def load_cache() -> dict:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(word: str, data: dict) -> None:
    cache = load_cache()
    cache[word.lower()] = data
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ====================== 单词笔记持久化（按用户隔离） ======================
def _get_notes_path(user_id: str) -> Path:
    NOTES_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return NOTES_BASE_DIR / f"{user_id}.json"


def _init_notes_file(path: Path) -> None:
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def read_notes(user_id: str = "") -> list:
    path = _get_notes_path(user_id) if user_id else _get_notes_path("default")
    _init_notes_file(path)
    with open(path, "r", encoding="utf-8") as f:
        notes = json.load(f)
    for item in notes:
        if "createTime" not in item:
            item["createTime"] = int(datetime.now().timestamp() * 1000)
        if "meanings" not in item:
            item["meanings"] = []
        if "meaning" not in item and item.get("meanings"):
            item["meaning"] = item["meanings"][0].get("definition", "暂无释义")
    return notes


def write_notes(notes: list, user_id: str = "") -> None:
    path = _get_notes_path(user_id) if user_id else _get_notes_path("default")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def add_note(item: dict, user_id: str = "") -> tuple[str, str]:
    notes = read_notes(user_id)
    if any(n["word"] == item["word"] for n in notes):
        return ("exists", "单词已存在")
    notes.append(item)
    write_notes(notes, user_id)
    return ("success", "保存成功")


def delete_note(word: str, user_id: str = "") -> tuple[str, str]:
    notes = read_notes(user_id)
    new_notes = [n for n in notes if n["word"] != word]
    write_notes(new_notes, user_id)
    return ("success", "删除成功")


def clear_notes(user_id: str = "") -> tuple[str, str]:
    write_notes([], user_id)
    return ("success", "清空成功")
