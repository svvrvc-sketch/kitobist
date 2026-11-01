import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import aiosqlite
try:
    import asyncpg
except ImportError:
    asyncpg = None

from config import DATABASE_URL

logger = logging.getLogger(__name__)
DB_PATH = Path(__file__).resolve().parent.parent / "kitobist.db"

class Database:
    def __init__(self, db_url: str = DATABASE_URL, local_path: Path = DB_PATH):
        self.db_url = db_url.strip() if db_url else ""
        self.local_path = str(local_path)
        self.is_postgres = bool(self.db_url and (self.db_url.startswith("postgresql://") or self.db_url.startswith("postgres://")))
        self.pool = None

    async def init(self):
        """Ma'lumotlar bazasi jadvallarini yaratish"""
        if self.is_postgres and asyncpg:
            try:
                # 6543 portni 5432 ga avtomatik o'tkazish (Session pooler barqarorroq)
                clean_url = self.db_url.replace("postgres://", "postgresql://").replace(":6543", ":5432")
                self.pool = await asyncpg.create_pool(
                    dsn=clean_url,
                    min_size=1,
                    max_size=10,
                    statement_cache_size=0,
                    command_timeout=60
                )
                logger.info("🚀 Supabase (PostgreSQL 5432) ga muvaffaqiyatli ulandi!")

                async with self.pool.acquire() as conn:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT UNIQUE NOT NULL,
                            full_name TEXT,
                            username TEXT,
                            phone TEXT,
                            referrer_id BIGINT,
                            points INT DEFAULT 0,
                            is_verified INT DEFAULT 0,
                            is_blocked INT DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE TABLE IF NOT EXISTS referrals (
                            id SERIAL PRIMARY KEY,
                            referrer_id BIGINT NOT NULL,
                            referred_id BIGINT UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE TABLE IF NOT EXISTS channels (
                            id SERIAL PRIMARY KEY,
                            channel_id TEXT UNIQUE NOT NULL,
                            channel_title TEXT,
                            channel_url TEXT
                        );
                        CREATE TABLE IF NOT EXISTS settings (
                            key TEXT PRIMARY KEY,
                            value TEXT
                        );
                        CREATE TABLE IF NOT EXISTS button_posts (
                            button_key TEXT PRIMARY KEY,
                            photo_id TEXT,
                            content_text TEXT
                        );
                    """)
                return
            except Exception as e:
                logger.error(f"❌ Supabase ulanishida xatolik: {e}. Lokal SQLite ga o'tilmoqda...")
                self.is_postgres = False

        # SQLite fallback
        async with aiosqlite.connect(self.local_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    full_name TEXT,
                    username TEXT,
                    phone TEXT,
                    referrer_id INTEGER,
                    points INTEGER DEFAULT 0,
                    is_verified INTEGER DEFAULT 0,
                    is_blocked INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referred_id INTEGER UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id TEXT UNIQUE NOT NULL,
                    channel_title TEXT,
                    channel_url TEXT
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS button_posts (
                    button_key TEXT PRIMARY KEY,
                    photo_id TEXT,
                    content_text TEXT
                );
            """)
            await db.commit()

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
                return dict(row) if row else None
        else:
            async with aiosqlite.connect(self.local_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None

    async def add_or_update_user(self, user_id: int, full_name: str, username: Optional[str] = None, referrer_id: Optional[int] = None) -> bool:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                existing = await conn.fetchrow("SELECT user_id, referrer_id FROM users WHERE user_id = $1", user_id)
                if not existing:
                    await conn.execute(
                        "INSERT INTO users (user_id, full_name, username, referrer_id) VALUES ($1, $2, $3, $4)",
                        user_id, full_name, username, referrer_id
                    )
                    return True
                else:
                    # Agar oldin ro'yxatdan o'tgan bo'lsa faqat ism/username yangilanadi
                    await conn.execute(
                        "UPDATE users SET full_name = $1, username = $2 WHERE user_id = $3",
                        full_name, username, user_id
                    )
                    return False
        else:
            async with aiosqlite.connect(self.local_path) as db:
                existing = await self.get_user(user_id)
                if not existing:
                    await db.execute(
                        "INSERT INTO users (user_id, full_name, username, referrer_id) VALUES (?, ?, ?, ?)",
                        (user_id, full_name, username, referrer_id)
                    )
                    await db.commit()
                    return True
                else:
                    await db.execute(
                        "UPDATE users SET full_name = ?, username = ? WHERE user_id = ?",
                        (full_name, username, user_id)
                    )
                    await db.commit()
                    return False

    async def verify_user_phone(self, user_id: int, phone: str) -> Optional[int]:
        """
        Foydalanuvchi telefonini tasdiqlash va referal ballini hisoblash.
        """
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    user = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1 FOR UPDATE", user_id)
                    if not user:
                        return None

                    # Agar allaqachon tasdiqlangan bo'lsa
                    if user["is_verified"] == 1:
                        await conn.execute("UPDATE users SET phone = $1 WHERE user_id = $2", phone, user_id)
                        return None

                    # Tasdiqlash
                    await conn.execute("UPDATE users SET phone = $1, is_verified = 1 WHERE user_id = $2", phone, user_id)
                    referrer_id = user["referrer_id"]

                    # Agar taklif qilgan odam bo'lsa va o'zi bo'lmasa
                    if referrer_id and referrer_id != user_id:
                        # Oldin bu referal yozilganmi tekshirish
                        ref_exists = await conn.fetchrow(
                            "SELECT id FROM referrals WHERE referred_id = $1", user_id
                        )
                        if not ref_exists:
                            await conn.execute(
                                "INSERT INTO referrals (referrer_id, referred_id) VALUES ($1, $2)",
                                referrer_id, user_id
                            )
                            # Taklif qiluvchiga +1 ball
                            await conn.execute(
                                "UPDATE users SET points = points + 1 WHERE user_id = $1",
                                referrer_id
                            )
                            logger.info(f"⭐️ Referal ball qo'shildi: Referrer {referrer_id} <- Referred {user_id}")
                            return referrer_id
                    return None
        else:
            async with aiosqlite.connect(self.local_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                    user = await cursor.fetchone()
                    if not user:
                        return None
                    
                    if user["is_verified"] == 1:
                        await db.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
                        await db.commit()
                        return None

                    await db.execute(
                        "UPDATE users SET phone = ?, is_verified = 1 WHERE user_id = ?",
                        (phone, user_id)
                    )

                    referrer_id = user["referrer_id"]
                    if referrer_id and referrer_id != user_id:
                        try:
                            await db.execute(
                                "INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)",
                                (referrer_id, user_id)
                            )
                            await db.execute(
                                "UPDATE users SET points = points + 1 WHERE user_id = ?",
                                (referrer_id,)
                            )
                            await db.commit()
                            return referrer_id
                        except Exception:
                            pass

                    await db.commit()
                    return None

    async def get_referral_count(self, user_id: int) -> int:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                val = await conn.fetchval("SELECT COUNT(*) FROM referrals WHERE referrer_id = $1", user_id)
                return val or 0
        else:
            async with aiosqlite.connect(self.local_path) as db:
                async with db.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0

    async def get_top_rankings(self, limit: int = 10) -> List[Dict[str, Any]]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT user_id, full_name, username, points FROM users WHERE points > 0 ORDER BY points DESC, id ASC LIMIT $1",
                    limit
                )
                return [dict(r) for r in rows]
        else:
            async with aiosqlite.connect(self.local_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT user_id, full_name, username, points FROM users WHERE points > 0 ORDER BY points DESC, id ASC LIMIT ?",
                    (limit,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

    async def get_user_rank(self, user_id: int) -> Optional[int]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow("SELECT points FROM users WHERE user_id = $1", user_id)
                if not user or user["points"] <= 0:
                    return None
                val = await conn.fetchval("SELECT COUNT(*) + 1 FROM users WHERE points > $1", user["points"])
                return val
        else:
            async with aiosqlite.connect(self.local_path) as db:
                db.row_factory = aiosqlite.Row
                user = await self.get_user(user_id)
                if not user or user["points"] <= 0:
                    return None
                async with db.execute(
                    "SELECT COUNT(*) + 1 FROM users WHERE points > ?",
                    (user["points"],)
                ) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else None

    async def get_stats(self) -> Dict[str, Any]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                total_users = await conn.fetchval("SELECT COUNT(*) FROM users") or 0
                verified_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_verified = 1") or 0
                total_referrals = await conn.fetchval("SELECT COUNT(*) FROM referrals") or 0
                today_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE") or 0
                return {
                    "total_users": total_users,
                    "verified_users": verified_users,
                    "total_referrals": total_referrals,
                    "today_users": today_users
                }
        else:
            async with aiosqlite.connect(self.local_path) as db:
                async with db.execute("SELECT COUNT(*) FROM users") as c1:
                    total_users = (await c1.fetchone())[0]
                async with db.execute("SELECT COUNT(*) FROM users WHERE is_verified = 1") as c2:
                    verified_users = (await c2.fetchone())[0]
                async with db.execute("SELECT COUNT(*) FROM referrals") as c3:
                    total_referrals = (await c3.fetchone())[0]
                async with db.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')") as c4:
                    today_users = (await c4.fetchone())[0]
                return {
                    "total_users": total_users,
                    "verified_users": verified_users,
                    "total_referrals": total_referrals,
                    "today_users": today_users
                }

    async def get_all_user_ids(self) -> List[int]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT user_id FROM users WHERE is_blocked = 0")
                return [r["user_id"] for r in rows]
        else:
            async with aiosqlite.connect(self.local_path) as db:
                async with db.execute("SELECT user_id FROM users WHERE is_blocked = 0") as cursor:
                    rows = await cursor.fetchall()
                    return [row[0] for row in rows]

    async def set_blocked(self, user_id: int, is_blocked: int = 1):
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute("UPDATE users SET is_blocked = $1 WHERE user_id = $2", is_blocked, user_id)
        else:
            async with aiosqlite.connect(self.local_path) as db:
                await db.execute("UPDATE users SET is_blocked = ? WHERE user_id = ?", (is_blocked, user_id))
                await db.commit()

    async def get_channels(self) -> List[Dict[str, Any]]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM channels")
                return [dict(r) for r in rows]
        else:
            async with aiosqlite.connect(self.local_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM channels") as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

    async def add_channel(self, channel_id: str, channel_title: str, channel_url: str):
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO channels (channel_id, channel_title, channel_url)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (channel_id) DO UPDATE SET
                        channel_title = EXCLUDED.channel_title,
                        channel_url = EXCLUDED.channel_url
                """, channel_id, channel_title, channel_url)
        else:
            async with aiosqlite.connect(self.local_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO channels (channel_id, channel_title, channel_url) VALUES (?, ?, ?)",
                    (channel_id, channel_title, channel_url)
                )
                await db.commit()

    async def delete_channel(self, channel_id: str):
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute("DELETE FROM channels WHERE channel_id = $1", channel_id)
        else:
            async with aiosqlite.connect(self.local_path) as db:
                await db.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
                await db.commit()

    async def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                val = await conn.fetchval("SELECT value FROM settings WHERE key = $1", key)
                return val if val is not None else default
        else:
            async with aiosqlite.connect(self.local_path) as db:
                async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else default

    async def set_setting(self, key: str, value: str):
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO settings (key, value) VALUES ($1, $2)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """, key, value)
        else:
            async with aiosqlite.connect(self.local_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, value)
                )
                await db.commit()

    async def get_button_post(self, button_key: str) -> Optional[Dict[str, Any]]:
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM button_posts WHERE button_key = $1", button_key)
                return dict(row) if row else None
        else:
            async with aiosqlite.connect(self.local_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM button_posts WHERE button_key = ?", (button_key,)) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None

    async def set_button_post(self, button_key: str, photo_id: Optional[str], content_text: Optional[str]):
        if self.is_postgres and self.pool:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO button_posts (button_key, photo_id, content_text) VALUES ($1, $2, $3)
                    ON CONFLICT (button_key) DO UPDATE SET
                        photo_id = EXCLUDED.photo_id,
                        content_text = EXCLUDED.content_text
                """, button_key, photo_id, content_text)
        else:
            async with aiosqlite.connect(self.local_path) as db:
                await db.execute(
                    "INSERT OR REPLACE INTO button_posts (button_key, photo_id, content_text) VALUES (?, ?, ?)",
                    (button_key, photo_id, content_text)
                )
                await db.commit()

db = Database()
