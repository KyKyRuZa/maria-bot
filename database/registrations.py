from .base import get_pool
import logging
logger = logging.getLogger(__name__)

async def save_registration(user_id: int, full_name: str, role: str, training_time: str, session_count: int, price: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO registrations (user_id, full_name, role, training_time, session_count, price)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE
            SET training_time = $4, session_count = $5, price = $6, registered_at = NOW()
        ''', user_id, full_name, role, training_time, session_count, price)
    
    
async def update_registration_role(user_id: int, new_role: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE registrations SET role = $1 WHERE user_id = $2",
            new_role, user_id
        )
    
    
async def get_user_registration(user_id: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT full_name, role, training_time, session_count, price, registered_at
            FROM registrations 
            WHERE user_id = $1
        """, user_id)
    
    return row

async def delete_registration(user_id: int) -> bool:
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM registrations WHERE user_id = $1", user_id)
    
    deleted = result.split()[-1] != "0"
    if deleted:
        logger.info(f"🗑 Запись пользователя удалена: user_id={user_id}")
    else:
        logger.warning(f"🗑 Попытка удаления несуществующей записи: user_id={user_id}")
    return deleted

async def get_all_registrations():
    pool = get_pool()
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
    
    return rows

async def get_financial_report():
    return {"total_revenue": 0, "active_subscriptions": 0}