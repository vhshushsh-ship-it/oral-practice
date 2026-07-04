import aiomysql
import os

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "oral123")
MYSQL_DB = os.getenv("MYSQL_DB", "listening")

_pool: aiomysql.Pool | None = None


async def _get_pool() -> aiomysql.Pool:
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB,
            charset="utf8mb4",
            autocommit=True,
        )
    return _pool


async def get_db() -> aiomysql.Connection:
    pool = await _get_pool()
    return await pool.acquire()


async def release_db(conn: aiomysql.Connection) -> None:
    pool = await _get_pool()
    await pool.release(conn)


async def init_db() -> None:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # ====================== 用户认证表 ======================
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(50) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    email_verified TINYINT(1) NOT NULL DEFAULT 0,
                    password_hash VARCHAR(255) NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            # Migration: add email_verified column (for tables created before the schema update)
            try:
                await cur.execute("ALTER TABLE users ADD COLUMN email_verified TINYINT(1) NOT NULL DEFAULT 0 AFTER email")
            except Exception:
                pass  # Column already exists — fine
            # Migration: make password_hash nullable (for tables created before the schema update)
            try:
                await cur.execute("ALTER TABLE users MODIFY password_hash VARCHAR(255) NULL")
            except Exception:
                pass  # Already nullable — fine
            # ====================== 验证码表 ======================
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS verification_codes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    code VARCHAR(6) NOT NULL,
                    purpose ENUM('register', 'login') NOT NULL,
                    expires_at DATETIME NOT NULL,
                    used TINYINT(1) NOT NULL DEFAULT 0,
                    attempts INT NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_email_purpose (email, purpose),
                    INDEX idx_expires (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            # ====================== 听力练习表 ======================
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_set (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    type ENUM('cet4','cet6') NOT NULL,
                    year INT NOT NULL,
                    month INT NOT NULL,
                    set_order INT NOT NULL DEFAULT 0
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_section (
                    id VARCHAR(50) PRIMARY KEY,
                    set_id VARCHAR(50) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    section_type ENUM('news_report','long_conversation','passage','none') NOT NULL,
                    sort_order INT NOT NULL DEFAULT 0,
                    FOREIGN KEY (set_id) REFERENCES listening_set(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_sentence (
                    id VARCHAR(50) PRIMARY KEY,
                    set_id VARCHAR(50) NOT NULL,
                    section_id VARCHAR(50),
                    item_id VARCHAR(50) DEFAULT NULL,
                    en TEXT NOT NULL,
                    zh TEXT NOT NULL,
                    audio_url VARCHAR(500) DEFAULT '',
                    question_ref VARCHAR(100) DEFAULT '',
                    sort_order INT NOT NULL DEFAULT 0,
                    FOREIGN KEY (set_id) REFERENCES listening_set(id) ON DELETE CASCADE,
                    FOREIGN KEY (section_id) REFERENCES listening_section(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_item (
                    id VARCHAR(50) PRIMARY KEY,
                    set_id VARCHAR(50) NOT NULL,
                    section_id VARCHAR(50) NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    sort_order INT NOT NULL DEFAULT 0,
                    FOREIGN KEY (set_id) REFERENCES listening_set(id) ON DELETE CASCADE,
                    FOREIGN KEY (section_id) REFERENCES listening_section(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_question (
                    id VARCHAR(50) PRIMARY KEY,
                    set_id VARCHAR(50) NOT NULL,
                    section_id VARCHAR(50),
                    item_id VARCHAR(50) DEFAULT NULL,
                    question_number INT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_text_zh TEXT,
                    option_a VARCHAR(500) NOT NULL DEFAULT '',
                    option_b VARCHAR(500) NOT NULL DEFAULT '',
                    option_c VARCHAR(500) NOT NULL DEFAULT '',
                    option_d VARCHAR(500) NOT NULL DEFAULT '',
                    correct_answer CHAR(1) NOT NULL,
                    sort_order INT NOT NULL DEFAULT 0,
                    FOREIGN KEY (set_id) REFERENCES listening_set(id) ON DELETE CASCADE,
                    FOREIGN KEY (section_id) REFERENCES listening_section(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            # Migration: add item_id to existing tables if they predate the migration
            try:
                await cur.execute("ALTER TABLE listening_sentence ADD COLUMN item_id VARCHAR(50) DEFAULT NULL AFTER section_id")
            except Exception:
                pass
            try:
                await cur.execute("ALTER TABLE listening_question ADD COLUMN item_id VARCHAR(50) DEFAULT NULL AFTER section_id")
            except Exception:
                pass
            try:
                await cur.execute("ALTER TABLE listening_question ADD COLUMN question_text_zh TEXT AFTER question_text")
            except Exception:
                pass
            # Auth migration: add user_id to exam tables
            try:
                await cur.execute("ALTER TABLE listening_exam_record ADD COLUMN user_id VARCHAR(50) DEFAULT NULL AFTER id")
            except Exception:
                pass
            try:
                await cur.execute("ALTER TABLE listening_exam_answer ADD COLUMN user_id VARCHAR(50) DEFAULT NULL AFTER id")
            except Exception:
                pass
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_exam_record (
                    id VARCHAR(50) PRIMARY KEY,
                    set_id VARCHAR(50) NOT NULL,
                    total_questions INT NOT NULL,
                    correct_count INT NOT NULL,
                    accuracy DECIMAL(5,2) NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (set_id) REFERENCES listening_set(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_sentence_analysis (
                    sentence_text TEXT NOT NULL,
                    connected_speech JSON NOT NULL,
                    sense_groups_segmented TEXT NOT NULL,
                    sense_groups_explanation TEXT NOT NULL,
                    PRIMARY KEY (sentence_text(255))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS user_sentence_analysis (
                    user_id VARCHAR(50) NOT NULL,
                    sentence_text TEXT NOT NULL,
                    connected_speech JSON NOT NULL,
                    sense_groups_segmented TEXT NOT NULL,
                    sense_groups_explanation TEXT NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, sentence_text(200))
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_grammar_cache (
                    sentence_text VARCHAR(500) PRIMARY KEY,
                    score INT NOT NULL,
                    source_sent TEXT NOT NULL,
                    error_index JSON NOT NULL,
                    error_info JSON NOT NULL,
                    fixed_sent TEXT NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS listening_exam_answer (
                    id VARCHAR(50) PRIMARY KEY,
                    exam_record_id VARCHAR(50) NOT NULL,
                    question_id VARCHAR(50) NOT NULL,
                    user_answer CHAR(1) NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    FOREIGN KEY (exam_record_id) REFERENCES listening_exam_record(id) ON DELETE CASCADE,
                    FOREIGN KEY (question_id) REFERENCES listening_question(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            # ====================== AI 对话记录表 ======================
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    user_id VARCHAR(50) NOT NULL,
                    scene VARCHAR(50) NOT NULL,
                    data JSON NOT NULL,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, scene),
                    INDEX idx_chat_user (user_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
