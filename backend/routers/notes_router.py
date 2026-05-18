from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Query, Body
from services.storage_service import read_notes, add_note, delete_note, clear_notes

router = APIRouter(tags=["notes"])


@router.post("/notes/add")
async def add_word_note(
    word: Optional[str] = Query(None),
    phonetic: Optional[str] = Query(None),
    meaning: Optional[str] = Query(None),
    body: Optional[dict] = Body(None),
):
    try:
        if body:
            word_data = body
            word = word_data.get("word")
            phonetic = word_data.get("phonetic", "")
            meaning = word_data.get("meaning", "")
            meanings = word_data.get("meanings", [])
            create_time = word_data.get("createTime", int(datetime.now().timestamp() * 1000))
        else:
            meanings = []
            create_time = int(datetime.now().timestamp() * 1000)

        item = {
            "word": word,
            "phonetic": phonetic,
            "meaning": meaning,
            "meanings": meanings,
            "createTime": create_time,
        }
        status, message = add_note(item)
        return {"status": status, "message": message}
    except Exception as e:
        print("添加单词失败:", e)
        return {"status": "error", "message": "保存失败"}


@router.post("/notes/delete")
async def delete_word_note(word: str = Query(...)):
    try:
        status, message = delete_note(word)
        return {"status": status, "message": message}
    except Exception as e:
        print("删除单词失败:", e)
        return {"status": "error", "message": "删除失败"}


@router.post("/notes/clear")
async def clear_all_notes():
    try:
        status, message = clear_notes()
        return {"status": status, "message": message}
    except Exception as e:
        print("清空失败:", e)
        return {"status": "error", "message": "清空失败"}


@router.get("/notes/all")
async def get_all_notes():
    try:
        notes = read_notes()
        return {"notes": notes}
    except Exception as e:
        print("读取笔记失败:", e)
        return {"notes": []}
