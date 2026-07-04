import asyncio
import json

from fastapi import APIRouter, Query, Body, Depends, HTTPException
from services.sentence_service import read_sentences, add_sentence, delete_sentence, clear_sentences
from services.ai_service import analyze_sentence_deepseek
from routers.auth_dependency import get_current_user
from db import get_db, release_db

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


@router.post("/sentences/analyze")
async def analyze_sentence_item(
    body: dict = Body(...),
    user_id: str = Depends(get_current_user),
):
    """用户私有句子分析 — 缓存优先，未命中则调用 DeepSeek 实时生成"""
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="句子内容不能为空")

    force = body.get("force", False)

    # 1. 查用户私有缓存（非 force 模式）
    if not force:
        db = await get_db()
        try:
            import aiomysql
            async with db.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT connected_speech, sense_groups_segmented, sense_groups_explanation "
                    "FROM user_sentence_analysis WHERE user_id = %s AND sentence_text = %s LIMIT 1",
                    (user_id, text),
                )
                row = await cur.fetchone()
                if row:
                    cs = json.loads(row["connected_speech"]) if isinstance(row["connected_speech"], str) else row["connected_speech"]
                    if isinstance(cs, list) and len(cs) > 0:
                        return {
                            "connected_speech": cs,
                            "sense_groups": {
                                "segmented": row["sense_groups_segmented"],
                                "explanation": row["sense_groups_explanation"],
                            },
                        }
        finally:
            await release_db(db)

    # 2. 缓存未命中 → 实时调用 DeepSeek
    try:
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, analyze_sentence_deepseek, text),
            timeout=150.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="句子分析超时，请稍后重试")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"句子分析失败: {str(e)}")

    # 3. 写入用户私有缓存（best-effort，失败不影响返回）
    db2 = await get_db()
    try:
        async with db2.cursor() as cur:
            await cur.execute(
                "INSERT INTO user_sentence_analysis "
                "(user_id, sentence_text, connected_speech, sense_groups_segmented, sense_groups_explanation) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "connected_speech = VALUES(connected_speech), "
                "sense_groups_segmented = VALUES(sense_groups_segmented), "
                "sense_groups_explanation = VALUES(sense_groups_explanation)",
                (
                    user_id,
                    text,
                    json.dumps(result["connected_speech"], ensure_ascii=False),
                    result["sense_groups"]["segmented"],
                    result["sense_groups"]["explanation"],
                ),
            )
            await db2.commit()
    except Exception as e:
        print(f"[USER ANALYZE CACHE] 写入私有缓存失败: {e}")
    finally:
        await release_db(db2)

    # 4. 返回
    return {
        "connected_speech": result["connected_speech"],
        "sense_groups": {
            "segmented": result["sense_groups"]["segmented"],
            "explanation": result["sense_groups"]["explanation"],
        },
    }
