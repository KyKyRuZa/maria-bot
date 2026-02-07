from .base import get_pool
from utils.validation import validate_category, validate_service_type, validate_session_count, validate_price

async def load_prices():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM prices
            ORDER BY category, service_type, duration, session_count
        """)
    return rows

async def update_price(category: str, service_type: str, duration: str, session_count: int, new_price: int):
    validated_category = validate_category(category)
    validated_service_type = validate_service_type(service_type)
    validated_session_count = validate_session_count(session_count)
    validated_new_price = validate_price(new_price)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        clean_duration = duration if duration is not None else ''

        await conn.execute('''
            INSERT INTO prices (category, service_type, duration, session_count, price)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (category, service_type, duration, session_count)
            DO UPDATE SET price = EXCLUDED.price
        ''', validated_category, validated_service_type, clean_duration, validated_session_count, validated_new_price)
    

async def get_current_price(category: str, service_type: str, duration: str, session_count: int) -> int:
    validated_category = validate_category(category)
    validated_service_type = validate_service_type(service_type)
    validated_session_count = validate_session_count(session_count)
    
    pool = get_pool()
    async with pool.acquire() as conn:
        clean_duration = duration if duration is not None else ''

        price = await conn.fetchval('''
            SELECT price FROM prices
            WHERE category = $1
            AND service_type = $2
            AND COALESCE(duration, '') = $3
            AND session_count = $4
        ''', validated_category, validated_service_type, clean_duration, validated_session_count)

    return price if price is not None else 0