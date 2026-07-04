import json
import aiomysql


async def save_chat_session(
    db: aiomysql.Connection,
    user_id: str,
    scene: str,
    history: list,
    translations: list,
) -> None:
    """保存用户某个场景的完整对话记录（UPSERT）"""
    data = json.dumps({"history": history, "translations": translations}, ensure_ascii=False)
    async with db.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO chat_sessions (user_id, scene, data)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE data = VALUES(data), updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, scene, data),
        )
        await db.commit()


async def get_chat_session(
    db: aiomysql.Connection,
    user_id: str,
    scene: str,
) -> dict:
    """获取用户某个场景的对话记录，返回 {"history": [...], "translations": [...]}"""
    async with db.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            "SELECT data FROM chat_sessions WHERE user_id = %s AND scene = %s",
            (user_id, scene),
        )
        row = await cur.fetchone()
    if row:
        data = row["data"]
        if isinstance(data, str):
            data = json.loads(data)
        # 兼容旧格式：纯数组
        if isinstance(data, list):
            return {"history": data, "translations": []}
        return {
            "history": data.get("history", []),
            "translations": data.get("translations", []),
        }
    return {"history": [], "translations": []}


async def delete_chat_session(
    db: aiomysql.Connection,
    user_id: str,
    scene: str,
) -> None:
    """删除用户某个场景的全部对话记录"""
    async with db.cursor() as cur:
        await cur.execute(
            "DELETE FROM chat_sessions WHERE user_id = %s AND scene = %s",
            (user_id, scene),
        )
        await db.commit()
