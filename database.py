import aiosqlite

async def create_tables():
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("CREATE TABLE IF NOT EXISTS users (discord_id TEXT, elo INTEGER, rank TEXT, wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, status TEXT)")
        cursor = await db.execute("CREATE TABLE IF NOT EXISTS matchs (match_id INTEGER AUTO_INCREMENT PRIMARY KEY, host_id TEXT, rank TEXT, status TEXT, FOREIGN KEY (host_id) REFERENCES users(discord_id))")
        await cursor.close()
        await db.commit()