"""
一次性数据迁移脚本：将旧的共享数据迁移到默认"legacy"用户下。

运行方式：
    cd backend && python scripts/migrate_to_auth.py

功能：
1. 在 MySQL 中创建一个 legacy 用户（如果不存在）
2. 将所有 user_id IS NULL 的考试记录分配给 legacy 用户
3. 将旧的 chat_records/*.json 移动到 chat_records/{legacy_user_id}/
4. 将旧的 word_notes.json 移动到 word_notes/{legacy_user_id}.json
"""
import os
import sys
import json
import shutil
import asyncio

# Add parent dir to path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from config import DATA_DIR, CHAT_BASE_DIR, NOTES_BASE_DIR
from db import get_db, release_db


async def migrate():
    LEGACY_EMAIL = "legacy@scenetalk.local"

    print("=" * 50)
    print("SceneTalk 数据迁移脚本 — 旧数据 → 用户隔离")
    print("=" * 50)

    # 1. 创建 legacy 用户
    db = await get_db()
    try:
        import aiomysql
        import uuid
        import bcrypt

        async with db.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM users WHERE email = %s", (LEGACY_EMAIL,))
            existing = await cur.fetchone()
            if existing:
                legacy_id = existing["id"]
                print(f"[1/4] Legacy 用户已存在: {legacy_id}")
            else:
                legacy_id = f"user-{uuid.uuid4().hex[:12]}"
                pwd_hash = bcrypt.hashpw(
                    "legacy_migration_do_not_login".encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                await cur.execute(
                    "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
                    (legacy_id, LEGACY_EMAIL, pwd_hash),
                )
                await db.commit()
                print(f"[1/4] 已创建 legacy 用户: {legacy_id} ({LEGACY_EMAIL})")

            # 2. 迁移 MySQL 考试记录
            await cur.execute(
                "UPDATE listening_exam_record SET user_id = %s WHERE user_id IS NULL",
                (legacy_id,),
            )
            updated_records = cur.rowcount
            await cur.execute(
                "UPDATE listening_exam_answer SET user_id = %s WHERE user_id IS NULL",
                (legacy_id,),
            )
            updated_answers = cur.rowcount
            await db.commit()
            print(f"[2/4] MySQL 迁移完成: {updated_records} 条考试记录, {updated_answers} 条答案")

    finally:
        await release_db(db)

    # 3. 迁移聊天记录 JSON 文件
    old_chat_dir = DATA_DIR / "chat_records"
    new_chat_dir = CHAT_BASE_DIR / legacy_id
    new_chat_dir.mkdir(parents=True, exist_ok=True)
    chat_count = 0

    if old_chat_dir.exists():
        for f in old_chat_dir.iterdir():
            if f.is_file() and f.suffix == ".json":
                target = new_chat_dir / f.name
                if not target.exists():
                    shutil.move(str(f), str(target))
                    chat_count += 1
    print(f"[3/4] 聊天记录迁移完成: {chat_count} 个场景文件")

    # 4. 迁移单词笔记 JSON 文件
    old_notes = DATA_DIR / "word_notes.json"
    new_notes = NOTES_BASE_DIR / f"{legacy_id}.json"
    if old_notes.exists() and not new_notes.exists():
        NOTES_BASE_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_notes), str(new_notes))
        print(f"[4/4] 单词笔记迁移完成")
    else:
        print(f"[4/4] 单词笔记无需迁移")

    print("=" * 50)
    print("✅ 迁移完成！Legacy 用户 ID:", legacy_id)
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(migrate())
