import aiosqlite

async def create_tables():
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("CREATE TABLE IF NOT EXISTS users (discord_id TEXT, elo INTEGER, rank TEXT, wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, status TEXT)")
        cursor = await db.execute("CREATE TABLE IF NOT EXISTS matchs (match_id INTEGER AUTO_INCREMENT PRIMARY KEY, host_id TEXT, rank TEXT, status TEXT, FOREIGN KEY (host_id) REFERENCES users(discord_id))")
        await cursor.close()
        await db.commit()

async def create_user(discord_id, elo, rank):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (discord_id, elo, rank, 0, 0, "inactive"))
        await cursor.close()
        await db.commit()

async def update_user(discord_id, elo, rank):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("UPDATE users SET elo = ?, rank = ? WHERE discord_id = ?", (elo, rank, discord_id))
        await cursor.close()
        await db.commit()

async def get_user(discord_id):
    async with aiosqlite.connect('Main.db') as db:
         async with db.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,)) as cursor:
            user = await cursor.fetchone()
            return user