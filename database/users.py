from .base import get_pool

async def save_user(user_id: int, full_name: str, age: int, role: str, phone: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, full_name, age, role, phone)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE
            SET full_name = $2, age = $3, role = $4, phone = $5
        ''', user_id, full_name, age, role, phone)
    

async def get_user_role(user_id: int) -> str | None:
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT role FROM users WHERE user_id = $1", user_id)
    
    return row['role'] if row else None

async def get_all_users():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, full_name, age, role, phone, registered_at 
            FROM users 
            ORDER BY registered_at DESC
        """)
    
    return rows

async def get_user_stats():
    pool = get_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        adults = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'Взрослый'")
        children = await conn.fetchval("SELECT COUNT(*) FROM users WHERE role = 'Ребёнок'")
    
    return {"total": total, "adults": adults, "children": children}