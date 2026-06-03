from fastapi import APIRouter, Query, Body, Depends
from services.grammar_service import (
    read_grammar_history,
    save_grammar_record,
    delete_grammar_record,
    clear_grammar_history,
)
from routers.auth_dependency import get_current_user

router = APIRouter(tags=["grammar"])


@router.post("/grammar/save")
async def save_grammar(
    body: dict = Body(...),
    user_id: str = Depends(get_current_user),
):
    """保存语法打分结果"""
    try:
        record = {
            "sourceSent": body.get("sourceSent", ""),
            "score": body.get("score", 0),
            "errorIndex": body.get("errorIndex", []),
            "errorInfo": body.get("errorInfo", []),
            "fixedSent": body.get("fixedSent", ""),
            "createdAt": body.get("createdAt"),
        }
        if not record["sourceSent"]:
            return {"status": "error", "message": "原始句子不能为空"}
        status, message = save_grammar_record(record, user_id)
        return {"status": status, "message": message}
    except Exception as e:
        print("保存语法记录失败:", e)
        return {"status": "error", "message": "保存失败"}


@router.get("/grammar/history")
async def get_grammar_history(user_id: str = Depends(get_current_user)):
    """获取当前用户所有语法打分历史"""
    try:
        records = read_grammar_history(user_id)
        return {"records": records}
    except Exception as e:
        print("读取语法历史失败:", e)
        return {"records": []}


@router.delete("/grammar/history/{index}")
async def delete_grammar(
    index: int,
    user_id: str = Depends(get_current_user),
):
    """按索引删除语法打分记录"""
    try:
        status, message = delete_grammar_record(index, user_id)
        return {"status": status, "message": message}
    except Exception as e:
        print("删除语法记录失败:", e)
        return {"status": "error", "message": "删除失败"}


@router.delete("/grammar/history")
async def clear_grammar(user_id: str = Depends(get_current_user)):
    """清空所有语法打分历史"""
    try:
        status, message = clear_grammar_history(user_id)
        return {"status": status, "message": message}
    except Exception as e:
        print("清空语法历史失败:", e)
        return {"status": "error", "message": "清空失败"}
