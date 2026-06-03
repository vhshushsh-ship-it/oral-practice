"""个人数据看板 - 统计聚合 API"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import APIRouter, Depends
from config import CHAT_BASE_DIR, NOTES_BASE_DIR, SCENE_MAP
from routers.auth_dependency import get_current_user
from db import get_db, release_db
import aiomysql

router = APIRouter(prefix="/api/stats", tags=["stats"])

SCENE_LABELS = {
    "free_talk": "自由对话", "restaurant": "餐厅", "interview": "面试",
    "hotel": "酒店", "home_life": "居家", "directions": "问路",
    "shopping": "购物", "medical": "医疗", "campus": "校园",
    "social": "社交", "travel": "旅游", "workplace": "职场",
    "service": "生活服务", "phone_chat": "电话聊天", "hobbies": "兴趣爱好",
    "transport": "交通出行", "housing": "租房看房",
}


def _get_scene_label(scene_key: str) -> str:
    return SCENE_LABELS.get(scene_key, scene_key)


# ====================== 概览统计 ======================
@router.get("/overview")
async def get_overview(user_id: str = Depends(get_current_user)):
    """总览卡片数据"""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    # ---- 对话统计 ----
    total_messages = 0
    practiced_scenes = set()
    today_messages = 0
    user_chat_dir = CHAT_BASE_DIR / user_id
    if user_chat_dir.exists():
        for f in user_chat_dir.iterdir():
            if f.suffix == ".json":
                scene_key = f.stem
                practiced_scenes.add(scene_key)
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        history = json.load(fh)
                    total_messages += len(history)
                    # 估算今日消息（基于每条消息的 timestamp 字段）
                    for msg in history:
                        ts = msg.get("timestamp", 0)
                        if ts:
                            msg_date = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                            if msg_date == today_str:
                                today_messages += 1
                except Exception:
                    pass

    # 如果没有 timestamp 字段，退一步用文件修改时间
    if today_messages == 0:
        for f in (user_chat_dir / d for d in os.listdir(user_chat_dir) if (user_chat_dir / d).is_dir() if user_chat_dir.exists()):
            pass  # already handling flat structure

    # ---- 单词统计 ----
    word_count = 0
    notes_file = NOTES_BASE_DIR / f"{user_id}.json"
    if notes_file.exists():
        try:
            with open(notes_file, "r", encoding="utf-8") as f:
                notes = json.load(f)
            word_count = len(notes)
        except Exception:
            pass

    # ---- 听力统计 ----
    exam_count = 0
    avg_accuracy = 0.0
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT COUNT(*) AS cnt, AVG(accuracy) AS avg_acc FROM listening_exam_record WHERE user_id = %s",
                (user_id,),
            )
            row = await cur.fetchone()
            if row:
                exam_count = row["cnt"] or 0
                avg_accuracy = round(float(row["avg_acc"] or 0), 1)
    finally:
        await release_db(db)

    # 估算练习时长（保守：每条消息约 30 秒）
    estimated_minutes = round(total_messages * 0.5)

    return {
        "totalMessages": total_messages,
        "practiceMinutes": estimated_minutes,
        "sceneCount": len(practiced_scenes),
        "wordCount": word_count,
        "examCount": exam_count,
        "avgAccuracy": avg_accuracy,
        "todayMessages": today_messages,
    }


# ====================== 口语分析 ======================
@router.get("/speaking")
async def get_speaking_stats(user_id: str = Depends(get_current_user)):
    """场景练习分布 & 趋势"""
    user_chat_dir = CHAT_BASE_DIR / user_id
    scene_stats = []  # [{scene, label, messageCount}]
    daily_counts: dict[str, int] = {}  # date -> count

    if user_chat_dir.exists():
        for f in user_chat_dir.iterdir():
            if f.suffix == ".json":
                scene_key = f.stem
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        history = json.load(fh)
                except Exception:
                    continue

                msg_count = len(history)
                if msg_count > 0:
                    scene_stats.append({
                        "scene": scene_key,
                        "label": _get_scene_label(scene_key),
                        "messageCount": msg_count,
                    })

                # 每日趋势（用文件修改时间作为近似）
                for msg in history:
                    ts = msg.get("timestamp", 0)
                    if ts:
                        date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

    # 按消息数降序排列
    scene_stats.sort(key=lambda x: x["messageCount"], reverse=True)

    # daily 转数组并按日期排序
    daily_trend = [{"date": k, "count": v} for k, v in daily_counts.items()]
    daily_trend.sort(key=lambda x: x["date"])

    # 如果没有 timestamp，按文件时间生成趋势
    if not daily_trend and scene_stats:
        for f in user_chat_dir.iterdir():
            if f.suffix == ".json":
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                date_str = mtime.strftime("%Y-%m-%d")
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        history = json.load(fh)
                    daily_counts[date_str] = daily_counts.get(date_str, 0) + len(history)
                except Exception:
                    pass
        daily_trend = [{"date": k, "count": v} for k, v in daily_counts.items()]
        daily_trend.sort(key=lambda x: x["date"])

    # 最近 30 天
    if len(daily_trend) > 30:
        daily_trend = daily_trend[-30:]

    return {
        "sceneStats": scene_stats,
        "dailyTrend": daily_trend,
        "totalScenes": len(SCENE_MAP),
        "practicedScenes": len(scene_stats),
    }


# ====================== 听力分析 ======================
@router.get("/listening")
async def get_listening_stats(user_id: str = Depends(get_current_user)):
    """听力考试成绩分析"""
    db = await get_db()
    records = []
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT er.id, er.set_id, er.total_questions, er.correct_count,
                       er.accuracy, er.created_at,
                       ls.name AS set_name, ls.type AS level
                FROM listening_exam_record er
                LEFT JOIN listening_set ls ON ls.id = er.set_id
                WHERE er.user_id = %s
                ORDER BY er.created_at ASC
            """, (user_id,))
            rows = list(await cur.fetchall())
    finally:
        await release_db(db)

    for r in rows:
        records.append({
            "id": r["id"],
            "setId": r["set_id"],
            "setName": r.get("set_name", ""),
            "level": r.get("level", ""),
            "totalQuestions": r["total_questions"],
            "correctCount": r["correct_count"],
            "accuracy": float(r["accuracy"]),
            "createdAt": str(r["created_at"]) if r.get("created_at") else "",
        })

    # 按级别统计
    cet4_records = [r for r in records if r["level"] == "cet4"]
    cet6_records = [r for r in records if r["level"] == "cet6"]

    def _level_summary(recs):
        if not recs:
            return {"count": 0, "avgAccuracy": 0, "bestAccuracy": 0}
        accs = [r["accuracy"] for r in recs]
        return {
            "count": len(recs),
            "avgAccuracy": round(sum(accs) / len(accs), 1),
            "bestAccuracy": round(max(accs), 1),
        }

    # 薄弱题型分析
    weak_sections = []
    try:
        db2 = await get_db()
        async with db2.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("""
                SELECT ls.section_type, COUNT(*) AS total,
                       SUM(CASE WHEN ea.is_correct = 1 THEN 1 ELSE 0 END) AS correct
                FROM listening_exam_answer ea
                JOIN listening_question lq ON lq.id = ea.question_id
                JOIN listening_section ls ON ls.id = lq.section_id
                WHERE ea.user_id = %s AND lq.section_id IS NOT NULL
                GROUP BY ls.section_type
            """, (user_id,))
            section_rows = list(await cur.fetchall())
        await release_db(db2)

        section_labels = {
            "news_report": "新闻短篇",
            "long_conversation": "长对话",
            "passage": "短文理解",
        }
        for sr in section_rows:
            stype = sr["section_type"]
            total = sr["total"]
            correct = sr["correct"]
            acc = round(correct / total * 100, 1) if total > 0 else 0
            weak_sections.append({
                "type": stype,
                "label": section_labels.get(stype, stype),
                "total": total,
                "correct": correct,
                "accuracy": acc,
            })
    except Exception:
        pass

    return {
        "records": records,
        "cet4": _level_summary(cet4_records),
        "cet6": _level_summary(cet6_records),
        "weakSections": weak_sections,
        "totalExams": len(records),
        "overallAvgAccuracy": round(sum(r["accuracy"] for r in records) / len(records), 1) if records else 0,
    }


# ====================== 词汇分析 ======================
@router.get("/vocabulary")
async def get_vocabulary_stats(user_id: str = Depends(get_current_user)):
    """词汇积累趋势"""
    notes_file = NOTES_BASE_DIR / f"{user_id}.json"
    if not notes_file.exists():
        return {
            "totalWords": 0,
            "weeklyTrend": [],
            "recentWords": [],
        }

    try:
        with open(notes_file, "r", encoding="utf-8") as f:
            notes = json.load(f)
    except Exception:
        return {"totalWords": 0, "weeklyTrend": [], "recentWords": []}

    # 按周聚合
    weekly_counts: dict[str, int] = {}
    for item in notes:
        ts = item.get("createTime", 0)
        if ts:
            dt = datetime.fromtimestamp(ts / 1000)
            # ISO week
            week_key = dt.strftime("%Y-W%W")
            weekly_counts[week_key] = weekly_counts.get(week_key, 0) + 1

    weekly_trend = [{"week": k, "count": v} for k, v in weekly_counts.items()]
    weekly_trend.sort(key=lambda x: x["week"])
    if len(weekly_trend) > 12:
        weekly_trend = weekly_trend[-12:]

    # 最近收藏
    sorted_notes = sorted(notes, key=lambda x: x.get("createTime", 0), reverse=True)
    recent = sorted_notes[:8]
    recent_words = []
    for item in recent:
        recent_words.append({
            "word": item.get("word", ""),
            "phonetic": item.get("phonetic", ""),
            "meaning": item.get("meaning", ""),
            "createTime": item.get("createTime", 0),
        })

    return {
        "totalWords": len(notes),
        "weeklyTrend": weekly_trend,
        "recentWords": recent_words,
    }


# ====================== 打卡 & 成就 ======================
@router.get("/streak")
async def get_streak(user_id: str = Depends(get_current_user)):
    """连续打卡和成就"""
    active_dates: set[str] = set()

    # 从对话记录聚合活跃日期
    user_chat_dir = CHAT_BASE_DIR / user_id
    if user_chat_dir.exists():
        for f in user_chat_dir.iterdir():
            if f.suffix == ".json":
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    active_dates.add(mtime.strftime("%Y-%m-%d"))
                    with open(f, "r", encoding="utf-8") as fh:
                        history = json.load(fh)
                    for msg in history:
                        ts = msg.get("timestamp", 0)
                        if ts:
                            active_dates.add(datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d"))
                except Exception:
                    pass

    # 从考试记录聚合
    db = await get_db()
    try:
        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT DISTINCT DATE(created_at) AS exam_date FROM listening_exam_record WHERE user_id = %s",
                (user_id,),
            )
            rows = list(await cur.fetchall())
            for r in rows:
                if r["exam_date"]:
                    active_dates.add(str(r["exam_date"]))
    finally:
        await release_db(db)

    # 计算连续天数
    sorted_dates = sorted(active_dates, reverse=True)
    streak = 0
    today = datetime.now().strftime("%Y-%m-%d")
    check_date = datetime.now()

    # 今天或昨天必须有活动才能算连续
    if sorted_dates and (sorted_dates[0] == today or sorted_dates[0] == (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")):
        if sorted_dates[0] != today:
            check_date = datetime.now() - timedelta(days=1)
        for date_str in sorted_dates:
            expected = check_date.strftime("%Y-%m-%d")
            if date_str == expected:
                streak += 1
                check_date -= timedelta(days=1)
            elif date_str < expected:
                break

    # 成就计算
    total_messages = 0
    total_scenes = set()
    if user_chat_dir.exists():
        for f in user_chat_dir.iterdir():
            if f.suffix == ".json":
                total_scenes.add(f.stem)
                try:
                    with open(f, "r", encoding="utf-8") as fh:
                        history = json.load(fh)
                    total_messages += len(history)
                except Exception:
                    pass

    notes_file = NOTES_BASE_DIR / f"{user_id}.json"
    word_count = 0
    if notes_file.exists():
        try:
            with open(notes_file, "r", encoding="utf-8") as f:
                word_count = len(json.load(f))
        except Exception:
            pass

    achievements = [
        {
            "id": "first_chat",
            "name": "初次对话",
            "description": "完成第一轮对话",
            "icon": "💬",
            "unlocked": total_messages >= 2,
        },
        {
            "id": "chat_100",
            "name": "百轮对话",
            "description": "累计完成 100 轮对话",
            "icon": "🗣️",
            "unlocked": total_messages >= 100,
        },
        {
            "id": "chat_500",
            "name": "对话达人",
            "description": "累计完成 500 轮对话",
            "icon": "🌟",
            "unlocked": total_messages >= 500,
        },
        {
            "id": "exam_5",
            "name": "听力新手",
            "description": "完成 5 次模拟考试",
            "icon": "🎧",
            "unlocked": len(sorted_dates) >= 5,
        },
        {
            "id": "word_50",
            "name": "词汇收集者",
            "description": "收藏 50 个单词",
            "icon": "📝",
            "unlocked": word_count >= 50,
        },
        {
            "id": "scene_10",
            "name": "场景探索者",
            "description": "练习过 10 个不同场景",
            "icon": "🌐",
            "unlocked": len(total_scenes) >= 10,
        },
        {
            "id": "scene_all",
            "name": "全场景制霸",
            "description": "完成全部 17 个场景的练习",
            "icon": "👑",
            "unlocked": len(total_scenes) >= 17,
        },
        {
            "id": "streak_7",
            "name": "坚持一周",
            "description": "连续打卡 7 天",
            "icon": "🔥",
            "unlocked": streak >= 7,
        },
    ]

    return {
        "streak": streak,
        "activeDates": sorted(active_dates),
        "achievements": achievements,
        "totalActiveDays": len(active_dates),
    }
