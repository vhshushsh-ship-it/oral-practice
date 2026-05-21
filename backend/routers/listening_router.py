import time
import json
import aiomysql
from fastapi import APIRouter, HTTPException, Query
from db import get_db, release_db
from models.schemas import ExamSubmitBody, SentenceAnalysisBody

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
async def submit_exam(body: ExamSubmitBody):
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
                "INSERT INTO listening_exam_record(id, set_id, total_questions, correct_count, accuracy) VALUES(%s,%s,%s,%s,%s)",
                (exam_id, body.set_id, total, correct_count, accuracy),
            )
            for d in details:
                ans_id = f"{exam_id}-{d['questionId']}"
                await cur.execute(
                    "INSERT INTO listening_exam_answer(id, exam_record_id, question_id, user_answer, is_correct) VALUES(%s,%s,%s,%s,%s)",
                    (ans_id, exam_id, d["questionId"], d["userAnswer"], d["isCorrect"]),
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


@router.get("/exam/history")
async def get_exam_history():
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT er.id, er.set_id, er.total_questions, er.correct_count,
                       er.accuracy, er.created_at,
                       ls.name AS set_name
                FROM listening_exam_record er
                LEFT JOIN listening_set ls ON ls.id = er.set_id
                ORDER BY er.created_at DESC
            """)
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
async def get_exam_detail(exam_id: str):
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM listening_exam_record WHERE id = %s",
                (exam_id,),
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
                WHERE ea.exam_record_id = %s
                ORDER BY lq.sort_order, lq.question_number
            """, (exam_id,))
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
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT connected_speech, sense_groups_segmented, sense_groups_explanation FROM listening_sentence_analysis WHERE sentence_text = %s OR %s LIKE CONCAT('%%', sentence_text, '%%') ORDER BY CHAR_LENGTH(sentence_text) DESC LIMIT 1",
                (body.text, body.text),
            )
            row = await cur.fetchone()
            if row:
                return {
                    "connected_speech": json.loads(row["connected_speech"]) if isinstance(row["connected_speech"], str) else row["connected_speech"],
                    "sense_groups": {
                        "segmented": row["sense_groups_segmented"],
                        "explanation": row["sense_groups_explanation"],
                    },
                }
    finally:
        await release_db(db)

    # Not found in DB
    raise HTTPException(status_code=404, detail="该句子暂无分析数据")
