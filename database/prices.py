from .base import get_pool

async def load_prices():
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM prices 
            ORDER BY category, service_type, duration, session_count
        """)
    return rows

async def update_price(category: str, service_type: str, duration: str, session_count: int, new_price: int):
    pool = get_pool()
    async with pool.acquire() as conn:
        clean_duration = duration if duration is not None else ''
        
        await conn.execute('''
            INSERT INTO prices (category, service_type, duration, session_count, price)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (category, service_type, duration, session_count)
            DO UPDATE SET price = EXCLUDED.price
        ''', category, service_type, clean_duration, session_count, new_price)
    

async def get_current_price(category: str, service_type: str, duration: str, session_count: int) -> int:
    pool = get_pool()
    async with pool.acquire() as conn:
        clean_duration = duration if duration is not None else ''
        
        price = await conn.fetchval('''
            SELECT price FROM prices 
            WHERE category = $1 
            AND service_type = $2 
            AND COALESCE(duration, '') = $3
            AND session_count = $4
        ''', category, service_type, clean_duration, session_count)
        
    return price if price is not None else 0