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
                    en TEXT NOT NULL,
                    zh TEXT NOT NULL,
                    audio_url VARCHAR(500) DEFAULT '',
                    question_ref VARCHAR(100) DEFAULT '',
                    sort_order INT NOT NULL DEFAULT 0,
                    FOREIGN KEY (set_id) REFERENCES listening_set(id) ON DELETE CASCADE,
                    FOREIGN KEY (section_id) REFERENCES listening_section(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
