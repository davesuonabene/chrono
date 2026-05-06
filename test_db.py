
import asyncio
import asyncpg

async def test_conn():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/prefect')
        print("✅ Successfully connected to PostgreSQL")
        await conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
