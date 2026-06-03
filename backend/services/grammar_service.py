import json
from datetime import datetime, timezone
from pathlib import Path
from config import GRAMMAR_BASE_DIR


def _get_grammar_path(user_id: str) -> Path:
    """获取用户语法打分历史文件路径"""
    GRAMMAR_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return GRAMMAR_BASE_DIR / f"{user_id}.json"


def _init_grammar_file(path: Path) -> None:
    """初始化空的语法历史文件"""
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def read_grammar_history(user_id: str) -> list:
    """读取用户所有语法打分历史"""
    path = _get_grammar_path(user_id)
    _init_grammar_file(path)
    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)
    # 补齐旧数据缺失字段
    for r in records:
        if "createdAt" not in r:
            r["createdAt"] = ""
    return records


def save_grammar_record(record: dict, user_id: str) -> tuple[str, str]:
    """保存一条语法打分记录"""
    records = read_grammar_history(user_id)
    if "createdAt" not in record:
        record["createdAt"] = datetime.now(timezone.utc).isoformat()
    records.append(record)
    path = _get_grammar_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return ("success", "保存成功")


def delete_grammar_record(index: int, user_id: str) -> tuple[str, str]:
    """按索引删除语法打分记录"""
    records = read_grammar_history(user_id)
    if index < 0 or index >= len(records):
        return ("error", "索引无效")
    records.pop(index)
    path = _get_grammar_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    return ("success", "删除成功")


def clear_grammar_history(user_id: str) -> tuple[str, str]:
    """清空用户所有语法打分历史"""
    path = _get_grammar_path(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    return ("success", "清空成功")
