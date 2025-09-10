import asyncpg
from dotenv import load_dotenv
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

async def create_pool():
    return await asyncpg.create_pool(**DB_CONFIG)

# --- Пользователи ---
async def save_user(user_id: int, full_name: str, age: int, role: str, phone: str):
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, full_name, age, role, phone)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE
            SET full_name = $2, age = $3, role = $4, phone = $5
        ''', user_id, full_name, age, role, phone)
    await pool.close()

async def get_user_role(user_id: int) -> str | None:
    pool = await create_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT role FROM users WHERE user_id = $1", user_id)
    await pool.close()
    return row['role'] if row else None

async def get_all_users():
    pool = await create_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, full_name, age, role, phone, registered_at 
            FROM users 
            ORDER BY registered_at DESC
        """)
    await pool.close()
    return rows

async def get_user_stats():
    pool = await create_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        adults = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'Взрослый'")
        children = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'Ребёнок'")
    await pool.close()
    return {"total": total, "adults": adults, "children": children}

# --- Цены ---
async def load_prices():
    pool = await create_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM prices 
            ORDER BY category, service_type, duration, session_count
        """)
    await pool.close()
    return rows

async def update_price(category: str, service_type: str, duration: str, session_count: int, new_price: int):
    pool = await create_pool()
    async with pool.acquire() as conn:
        clean_duration = duration if duration is not None else ''
        
        await conn.execute('''
            INSERT INTO prices (category, service_type, duration, session_count, price)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (category, service_type, duration, session_count)
            DO UPDATE SET price = EXCLUDED.price
        ''', category, service_type, clean_duration, session_count, new_price)
    await pool.close()

# --- Финансы ---
async def get_financial_report():
    return {"total_revenue": 0, "active_subscriptions": 0}

# --- Записи на тренировки ---
async def save_registration(user_id: int, full_name: str, role: str, training_time: str, session_count: int, price: int):
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO registrations (user_id, full_name, role, training_time, session_count, price)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE
            SET training_time = $4, session_count = $5, price = $6, registered_at = NOW()
        ''', user_id, full_name, role, training_time, session_count, price)
    await pool.close()
    
async def update_registration_role(user_id: int, new_role: str):
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE registrations SET role = $1 WHERE user_id = $2",
            new_role, user_id
        )
    await pool.close()
    
async def get_user_registration(user_id: int):
    """
    Получить запись пользователя на тренировку
    """
    pool = await create_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT full_name, role, training_time, session_count, price, registered_at
            FROM registrations 
            WHERE user_id = $1
        """, user_id)
    await pool.close()
    return row

async def get_all_registrations():
    pool = await create_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT 
                r.user_id,
                u.full_name,
                u.age,
                u.role,
                r.training_time,
                r.session_count,
                r.price,
                r.registered_at,
                u.phone
            FROM registrations r
            JOIN users u ON r.user_id = u.user_id
            ORDER BY r.registered_at DESC
        """)
    await pool.close()
    return rows