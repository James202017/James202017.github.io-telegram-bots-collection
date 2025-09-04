import aiosqlite
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

from app.config import settings

async def init_db():
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT,
                created_at TEXT
            );
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                expires_at TEXT,
                UNIQUE(user_id, role)
            );
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                city TEXT,
                params_json TEXT,
                created_at TEXT,
                status TEXT
            );
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                method TEXT,
                amount INTEGER,
                plan TEXT,
                role TEXT,
                status TEXT,
                payload TEXT,
                created_at TEXT
            );
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_user_id INTEGER,
                city TEXT,
                address TEXT,
                price INTEGER,
                rooms INTEGER,
                new_build INTEGER,
                url TEXT,
                created_at TEXT
            );
        ''')
        await db.commit()

async def upsert_user(user_id: int, username: Optional[str], role: Optional[str] = None):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id, username, role, created_at) VALUES(?,?,?,?)",
            (user_id, username or "", role or "", datetime.utcnow().isoformat())
        )
        if role:
            await db.execute("UPDATE users SET role=? WHERE user_id=?", (role, user_id))
        await db.commit()

async def set_subscription(user_id: int, role: str, days: int):
    expires = datetime.utcnow() + timedelta(days=days)
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "INSERT INTO subscriptions(user_id, role, expires_at) VALUES(?,?,?) "
            "ON CONFLICT(user_id, role) DO UPDATE SET expires_at=excluded.expires_at",
            (user_id, role, expires.isoformat())
        )
        await db.commit()
    return expires

async def has_active_subscription(user_id: int, role: str) -> bool:
    async with aiosqlite.connect(settings.db_path) as db:
        async with db.execute(
            "SELECT expires_at FROM subscriptions WHERE user_id=? AND role=?", (user_id, role)
        ) as cur:
            row = await cur.fetchone()
            if not row:
                return False
            expires = datetime.fromisoformat(row[0])
            return expires > datetime.utcnow()

async def insert_lead(user_id: int, role: str, city: str, params: Dict[str, Any]):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "INSERT INTO leads(user_id, role, city, params_json, created_at, status) "
            "VALUES(?,?,?,?,?,?)",
            (user_id, role, city, json.dumps(params, ensure_ascii=False), datetime.utcnow().isoformat(), "new")
        )
        await db.commit()

async def list_recent_leads(limit: int = 10):
    async with aiosqlite.connect(settings.db_path) as db:
        async with db.execute(
            "SELECT id, city, params_json, created_at FROM leads ORDER BY id DESC LIMIT ?",
            (limit,)
        ) as cur:
            rows = await cur.fetchall()
            return rows

async def insert_property(agent_user_id: int, city: str, address: str, price: int, rooms: int, new_build: bool, url: str):
    async with aiosqlite.connect(settings.db_path) as db:
        await db.execute(
            "INSERT INTO properties(agent_user_id, city, address, price, rooms, new_build, url, created_at) "
            "VALUES(?,?,?,?,?,?,?,?)",
            (agent_user_id, city, address, price, rooms, int(new_build), url, datetime.utcnow().isoformat())
        )
        await db.commit()

async def list_properties(city: str, max_price: Optional[int], rooms: Optional[int], new_build: Optional[bool], limit: int = 10):
    query = "SELECT city, address, price, rooms, new_build, url FROM properties WHERE city=?"
    params = [city]
    if max_price is not None:
        query += " AND price<=?"
        params.append(max_price)
    if rooms is not None:
        query += " AND rooms=?"
        params.append(rooms)
    if new_build is not None:
        query += " AND new_build=?"
        params.append(int(new_build))
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    async with aiosqlite.connect(settings.db_path) as db:
        async with db.execute(query, tuple(params)) as cur:
            return await cur.fetchall()
