import time
import json
import asyncio
import aiomysql
from fastapi import APIRouter, HTTPException, Query, Depends
from db import get_db, release_db
from models.schemas import ExamSubmitBody, SentenceAnalysisBody, GrammarCheckBody
from routers.auth_dependency import get_current_user
from services.ai_service import analyze_sentence_deepseek


router = APIRouter(prefix="/api/listening", tags=["listening"])


@router.get("/sets")
async def get_sets(level: str | None = Query(None)):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            if level:
                await cur.execute("""
                    SELECT ls.id, ls.name, ls.type, ls.year, ls.month,
                           COUNT(DISTINCT lse.id) AS sentence_count,
                           COUNT(DISTINCT lq.id) AS question_count
                    FROM listening_set ls
                    LEFT JOIN listening_sentence lse ON lse.set_id = ls.id
                    LEFT JOIN listening_question lq ON lq.set_id = ls.id
                    WHERE ls.type = %s
                    GROUP BY ls.id
                    ORDER BY ls.year DESC, ls.month DESC
                """, (level,))
            else:
                await cur.execute("""
                    SELECT ls.id, ls.name, ls.type, ls.year, ls.month,
                           COUNT(DISTINCT lse.id) AS sentence_count,
                           COUNT(DISTINCT lq.id) AS question_count
                    FROM listening_set ls
                    LEFT JOIN listening_sentence lse ON lse.set_id = ls.id
                    LEFT JOIN listening_question lq ON lq.set_id = ls.id
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
                # Fetch items for this section
                await cur.execute(
                    "SELECT id, name, sort_order FROM listening_item WHERE section_id = %s ORDER BY sort_order",
                    (sec["id"],),
                )
                items = list(await cur.fetchall())

                if items:
                    all_sentences = []
                    for item in items:
                        await cur.execute(
                            "SELECT id, set_id, en, zh, audio_url, question_ref, sort_order FROM listening_sentence WHERE item_id = %s ORDER BY sort_order",
                            (item["id"],),
                        )
                        item["sentences"] = list(await cur.fetchall())
                        all_sentences.extend(item["sentences"])
                    sec["items"] = items
                    sec["sentences"] = all_sentences
                else:
                    # Fallback for data without items
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

            await cur.execute(
                "SELECT COUNT(*) AS cnt FROM listening_question WHERE set_id = %s",
                (set_id,),
            )
            q_row = await cur.fetchone()
            set_dict["question_count"] = q_row["cnt"] if q_row else 0
    finally:
        await release_db(db)

    return {"set": set_dict}


@router.get("/sets/{set_id}/questions")
async def get_questions(set_id: str):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id FROM listening_set WHERE id = %s",
                (set_id,),
            )
            if not await cur.fetchone():
                raise HTTPException(status_code=404, detail="Set not found")

            await cur.execute("""
                SELECT lq.id, lq.set_id, lq.section_id, lq.item_id,
                       lq.question_number, lq.question_text, lq.question_text_zh,
                       lq.option_a, lq.option_b, lq.option_c, lq.option_d,
                       lq.sort_order,
                       ls.name AS section_name,
                       li.name AS item_name
                FROM listening_question lq
                LEFT JOIN listening_section ls ON ls.id = lq.section_id
                LEFT JOIN listening_item li ON li.id = lq.item_id
                WHERE lq.set_id = %s
                ORDER BY lq.sort_order, lq.question_number
            """, (set_id,))
            questions = list(await cur.fetchall())
    finally:
        await release_db(db)

    return {"set_id": set_id, "questions": questions}


@router.post("/exam/submit")
async def submit_exam(body: ExamSubmitBody, user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id FROM listening_set WHERE id = %s",
                (body.set_id,),
            )
            if not await cur.fetchone():
                raise HTTPException(status_code=404, detail="Set not found")

            await cur.execute(
                "SELECT id, question_number, question_text, question_text_zh, option_a, option_b, option_c, option_d, correct_answer, section_id FROM listening_question WHERE set_id = %s ORDER BY sort_order, question_number",
                (body.set_id,),
            )
            questions = list(await cur.fetchall())

            if not questions:
                raise HTTPException(status_code=400, detail="No questions found for this set")

            answer_map = {a.question_id: a.selected_option.upper() for a in body.answers}

            correct_count = 0
            details = []
            for q in questions:
                user_ans = answer_map.get(q["id"], "")
                is_correct = user_ans == q["correct_answer"]
                if is_correct:
                    correct_count += 1
                details.append({
                    "questionId": q["id"],
                    "questionNumber": q["question_number"],
                    "questionText": q["question_text"],
                    "optionA": q["option_a"],
                    "optionB": q["option_b"],
                    "optionC": q["option_c"],
                    "optionD": q["option_d"],
                    "correctAnswer": q["correct_answer"],
                    "userAnswer": user_ans,
                    "isCorrect": is_correct,
                })

            total = len(questions)
            accuracy = round(correct_count / total * 100, 2)
            exam_id = f"exam-{int(time.time() * 1000)}"

            await cur.execute(
                "INSERT INTO listening_exam_record(id, user_id, set_id, total_questions, correct_count, accuracy) VALUES(%s,%s,%s,%s,%s,%s)",
                (exam_id, user_id, body.set_id, total, correct_count, accuracy),
            )
            for d in details:
                ans_id = f"{exam_id}-{d['questionId']}"
                await cur.execute(
                    "INSERT INTO listening_exam_answer(id, user_id, exam_record_id, question_id, user_answer, is_correct) VALUES(%s,%s,%s,%s,%s,%s)",
                    (ans_id, user_id, exam_id, d["questionId"], d["userAnswer"], d["isCorrect"]),
                )
            await db.commit()

    finally:
        await release_db(db)

    return {
        "id": exam_id,
        "set_id": body.set_id,
        "totalQuestions": total,
        "correctCount": correct_count,
        "accuracy": accuracy,
        "createdAt": "",
        "details": details,
    }


@router.delete("/exam/history")
async def clear_exam_history(user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        async with db.cursor() as cur:
            await cur.execute("DELETE FROM listening_exam_answer WHERE user_id = %s", (user_id,))
            await cur.execute("DELETE FROM listening_exam_record WHERE user_id = %s", (user_id,))
            await db.commit()
    finally:
        await release_db(db)
    return {"message": "已清空所有记录"}


@router.delete("/exam/history/{exam_id}")
async def delete_exam_record(exam_id: str, user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        async with db.cursor() as cur:
            await cur.execute(
                "DELETE FROM listening_exam_answer WHERE exam_record_id = %s AND user_id = %s",
                (exam_id, user_id),
            )
            await cur.execute(
                "DELETE FROM listening_exam_record WHERE id = %s AND user_id = %s",
                (exam_id, user_id),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Exam record not found")
            await db.commit()
    finally:
        await release_db(db)
    return {"message": "删除成功"}


@router.get("/exam/history")
async def get_exam_history(user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT er.id, er.set_id, er.total_questions, er.correct_count,
                       er.accuracy, er.created_at,
                       ls.name AS set_name
                FROM listening_exam_record er
                LEFT JOIN listening_set ls ON ls.id = er.set_id
                WHERE er.user_id = %s
                ORDER BY er.created_at DESC
            """, (user_id,))
            rows = list(await cur.fetchall())
    finally:
        await release_db(db)

    records = []
    for r in rows:
        records.append({
            "id": r["id"],
            "set_id": r["set_id"],
            "set_name": r.get("set_name", ""),
            "totalQuestions": r["total_questions"],
            "correctCount": r["correct_count"],
            "accuracy": float(r["accuracy"]),
            "createdAt": str(r["created_at"]) if r.get("created_at") else "",
        })

    return {"records": records}


@router.get("/exam/history/{exam_id}")
async def get_exam_detail(exam_id: str, user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM listening_exam_record WHERE id = %s AND user_id = %s",
                (exam_id, user_id),
            )
            record = await cur.fetchone()
            if not record:
                raise HTTPException(status_code=404, detail="Exam record not found")

            await cur.execute("""
                SELECT ea.question_id, ea.user_answer, ea.is_correct,
                       lq.question_number, lq.question_text, lq.question_text_zh,
                       lq.option_a, lq.option_b, lq.option_c, lq.option_d,
                       lq.correct_answer
                FROM listening_exam_answer ea
                JOIN listening_question lq ON lq.id = ea.question_id
                WHERE ea.exam_record_id = %s AND ea.user_id = %s
                ORDER BY lq.sort_order, lq.question_number
            """, (exam_id, user_id))
            answers = list(await cur.fetchall())

    finally:
        await release_db(db)

    details = []
    for a in answers:
        details.append({
            "questionId": a["question_id"],
            "questionNumber": a["question_number"],
            "questionText": a["question_text"],
            "questionTextZh": a.get("question_text_zh", ""),
            "optionA": a["option_a"],
            "optionB": a["option_b"],
            "optionC": a["option_c"],
            "optionD": a["option_d"],
            "correctAnswer": a["correct_answer"],
            "userAnswer": a["user_answer"],
            "isCorrect": bool(a["is_correct"]),
        })

    return {
        "id": record["id"],
        "set_id": record["set_id"],
        "totalQuestions": record["total_questions"],
        "correctCount": record["correct_count"],
        "accuracy": float(record["accuracy"]),
        "createdAt": str(record["created_at"]) if record.get("created_at") else "",
        "details": details,
    }


@router.post("/analyze")
async def analyze(body: SentenceAnalysisBody):
    """公共句子分析 — 缓存优先，未命中则调用 DeepSeek 实时生成（全局复用）"""
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="句子内容不能为空")

    # 1. 查全局缓存
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT connected_speech, sense_groups_segmented, sense_groups_explanation "
                "FROM listening_sentence_analysis WHERE sentence_text = %s LIMIT 1",
                (text,),
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

    # 3. 写入全局缓存（best-effort，失败不影响返回）
    db2 = await get_db()
    try:
        async with db2.cursor() as cur:
            await cur.execute(
                "INSERT INTO listening_sentence_analysis "
                "(sentence_text, connected_speech, sense_groups_segmented, sense_groups_explanation) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "connected_speech = VALUES(connected_speech), "
                "sense_groups_segmented = VALUES(sense_groups_segmented), "
                "sense_groups_explanation = VALUES(sense_groups_explanation)",
                (
                    text,
                    json.dumps(result["connected_speech"], ensure_ascii=False),
                    result["sense_groups"]["segmented"],
                    result["sense_groups"]["explanation"],
                ),
            )
            await db2.commit()
    except Exception as e:
        print(f"[ANALYZE CACHE] 写入全局缓存失败: {e}")
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


@router.post("/grammar-check")
async def grammar_check(body: GrammarCheckBody):
    """AI grammar checking and scoring — cache-first, then DeepSeek Chat"""
    import traceback

    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="句子不能为空")

    # ---- Cache lookup ----
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT score, source_sent, error_index, error_info, fixed_sent FROM listening_grammar_cache WHERE sentence_text = %s",
                (text,),
            )
            row = await cur.fetchone()
            if row:
                return {
                    "score": row["score"],
                    "source_sent": row["source_sent"],
                    "error_index": json.loads(row["error_index"]) if isinstance(row["error_index"], str) else row["error_index"],
                    "error_info": json.loads(row["error_info"]) if isinstance(row["error_info"], str) else row["error_info"],
                    "fixed_sent": row["fixed_sent"],
                }
    finally:
        await release_db(db)

    # ---- Cache miss — call AI (with overall timeout) ----
    try:
        import asyncio
        from services.ai_service import check_grammar_deepseek
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, check_grammar_deepseek, text),
            timeout=100.0,  # generous timeout to accommodate 3 retries × 30s
        )
    except asyncio.TimeoutError:
        print(f"[GRAMMAR CHECK ERROR] Overall timeout after 100s")
        raise HTTPException(status_code=500, detail="语法检测超时，请稍后重试")
    except Exception as e:
        print(f"[GRAMMAR CHECK ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"语法检测失败: {type(e).__name__}: {e}")

    # ---- Save to cache ----
    db2 = await get_db()
    try:
        async with db2.cursor() as cur:
            await cur.execute(
                "INSERT IGNORE INTO listening_grammar_cache (sentence_text, score, source_sent, error_index, error_info, fixed_sent) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    text,
                    result["score"],
                    result["source_sent"],
                    json.dumps(result["error_index"], ensure_ascii=False),
                    json.dumps(result["error_info"], ensure_ascii=False),
                    result["fixed_sent"],
                ),
            )
            await db2.commit()
    except Exception as e:
        print(f"[GRAMMAR CHECK] Failed to cache result: {e}")
    finally:
        await release_db(db2)

    return result
