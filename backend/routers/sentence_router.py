from fastapi import APIRouter, Query, Body, Depends
from services.sentence_service import read_sentences, add_sentence, delete_sentence, clear_sentences
from routers.auth_dependency import get_current_user

router = APIRouter(tags=["sentences"])


@router.post("/sentences/add")
async def add_sentence_item(
    body: dict = Body(...),
    user_id: str = Depends(get_current_user),
):
    """添加句子收藏"""
    try:
        item = {
            "text": body.get("text", ""),
            "translation": body.get("translation", ""),
            "createTime": body.get("createTime"),
        }
        if not item["text"]:
            return {"status": "error", "message": "句子内容不能为空"}
        status, message = add_sentence(item, user_id)
        return {"status": status, "message": message}
    except Exception as e:
        print("添加句子失败:", e)
        return {"status": "error", "message": "保存失败"}


@router.post("/sentences/delete")
async def delete_sentence_item(
    index: int = Query(...),
    user_id: str = Depends(get_current_user),
):
    """按索引删除句子收藏"""
    try:
        status, message = delete_sentence(index, user_id)
        return {"status": status, "message": message}
    except Exception as e:
        print("删除句子失败:", e)
        return {"status": "error", "message": "删除失败"}


@router.post("/sentences/clear")
async def clear_all_sentences(user_id: str = Depends(get_current_user)):
    """清空所有句子收藏"""
    try:
        status, message = clear_sentences(user_id)
        return {"status": status, "message": message}
    except Exception as e:
        print("清空句子失败:", e)
        return {"status": "error", "message": "清空失败"}


@router.get("/sentences/all")
async def get_all_sentences(user_id: str = Depends(get_current_user)):
    """获取当前用户所有句子收藏"""
    try:
        sentences = read_sentences(user_id)
        return {"sentences": sentences}
    except Exception as e:
        print("读取句子失败:", e)
        return {"sentences": []}
