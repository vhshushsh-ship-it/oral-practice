import aiomysql
from fastapi import APIRouter, HTTPException
from db import get_db, release_db

router = APIRouter(prefix="/api/listening", tags=["listening"])


@router.get("/sets")
async def get_sets():
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT ls.id, ls.name, ls.type, ls.year, ls.month,
                       COUNT(lse.id) AS sentence_count
                FROM listening_set ls
                LEFT JOIN listening_sentence lse ON lse.set_id = ls.id
                GROUP BY ls.id
                ORDER BY ls.year DESC, ls.month DESC
            """)
            rows = list(await cur.fetchall())
    finally:
        await release_db(db)

    return {"sets": rows}


@router.get("/sets/{set_id}")
async def get_set_detail(set_id: str):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM listening_set WHERE id = %s",
                (set_id,),
            )
            set_row = await cur.fetchone()
            if not set_row:
                raise HTTPException(status_code=404, detail="Set not found")

            set_dict = dict(set_row)

            await cur.execute(
                "SELECT * FROM listening_section WHERE set_id = %s ORDER BY sort_order",
                (set_id,),
            )
            sections = list(await cur.fetchall())

            for sec in sections:
                await cur.execute(
                    "SELECT id, set_id, en, zh, audio_url, question_ref, sort_order FROM listening_sentence WHERE section_id = %s ORDER BY sort_order",
                    (sec["id"],),
                )
                sec["sentences"] = list(await cur.fetchall())

            await cur.execute(
                "SELECT id, set_id, en, zh, audio_url, question_ref, sort_order FROM listening_sentence WHERE set_id = %s AND section_id IS NULL ORDER BY sort_order",
                (set_id,),
            )
            ungrouped = list(await cur.fetchall())

            if ungrouped:
                sections.append({
                    "id": None,
                    "name": "全部句子",
                    "section_type": "none",
                    "sort_order": -1,
                    "sentences": ungrouped,
                })

            set_dict["sections"] = sections
    finally:
        await release_db(db)

    return {"set": set_dict}
