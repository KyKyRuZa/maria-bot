from .base import get_pool
from utils.validation import validate_user_id, validate_full_name, validate_age, validate_role, validate_phone

async def save_user(user_id: int, full_name: str, age: int, role: str, phone: str):
    validated_user_id = validate_user_id(user_id)
    validated_full_name = validate_full_name(full_name)
    validated_age = validate_age(age)
    validated_role = validate_role(role)
    validated_phone = validate_phone(phone)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, full_name, age, role, phone)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) DO UPDATE
            SET full_name = $2, age = $3, role = $4, phone = $5
        ''', validated_user_id, validated_full_name, validated_age, validated_role, validated_phone)
    

async def get_user_role(user_id: int) -> str | None:
    validated_user_id = validate_user_id(user_id)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT role FROM users WHERE user_id = $1", validated_user_id)

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