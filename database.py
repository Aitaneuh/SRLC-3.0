import aiosqlite

async def create_tables():
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("CREATE TABLE IF NOT EXISTS users (discord_id TEXT, elo INTEGER, rank TEXT, wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, status TEXT, game_id INTEGER DEFAULT 0, team TEXT)")
        cursor = await db.execute("CREATE TABLE IF NOT EXISTS 'games' ('game_id'	INTEGER,'host_id'	TEXT,'rank'	TEXT,'status'	TEXT,PRIMARY KEY('game_id' AUTOINCREMENT))")
        await cursor.close()
        await db.commit()

async def create_user(discord_id, elo, rank):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (discord_id, elo, rank, 0, 0, "inactive", 0, None))
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

async def add_to_queue(discord_id, game_id):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("UPDATE users SET game_id = ?, status = ? WHERE discord_id = ?", (game_id, "in_queue", discord_id))
        await cursor.close()
        await db.commit()

async def remove_from_queue(discord_id):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("UPDATE users SET game_id = ?, status = ? WHERE discord_id = ?", (0, "inactive", discord_id))
        await cursor.close()
        await db.commit()

async def count_queued_game_by_rank(rank):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT COUNT(*) FROM games WHERE status = ? AND rank = ?", ("in_queue", rank)) as cursor:
            count = await cursor.fetchone()
            return count[0]
        
async def create_game(rank):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("INSERT INTO games (host_id, rank, status) VALUES (?, ?, ?)", ("0", rank, "in_queue"))
        await cursor.close()
        await db.commit()


async def get_queued_game_id_by_rank(rank):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT game_id FROM games WHERE status = ? AND rank = ?", ("in_queue", rank)) as cursor:
            result = await cursor.fetchone()
            if result:  
                game_id = result[0]  
            else:
                game_id = None  
            return game_id
        
async def count_player_by_game(game_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT COUNT(*) FROM users WHERE game_id = ?", (game_id,)) as cursor:
            count = await cursor.fetchone()
            return count[0]
        
async def start_game(game_id):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("UPDATE games SET status = ? WHERE game_id = ?", ("started", game_id))
        cursor = await db.execute("UPDATE users SET status = ? WHERE game_id = ?", ("in_game", game_id))
        await cursor.close()
        await db.commit()

async def get_players_by_game(game_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT discord_id FROM users WHERE game_id = ?", (game_id,)) as cursor:
            players = await cursor.fetchall()
            return [player[0] for player in players]
        
async def add_host_id(host_id, game_id):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("UPDATE games SET host_id = ? WHERE game_id = ?", (host_id, game_id))
        await cursor.close()
        await db.commit()

async def update_player_team(player_id, team_color):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("UPDATE users SET team = ? WHERE discord_id = ?", (team_color, player_id))
        await cursor.close()
        await db.commit()

async def get_game_by_user(user_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT game_id FROM users WHERE discord_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()
            if result:  
                game_id = result[0]  
            else:
                game_id = None  
            return game_id

async def delete_game(game_id):
    async with aiosqlite.connect('Main.db') as db:
        cursor = await db.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
        await cursor.close()
        await db.commit()

async def get_host_id_by_game_id(game_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT host_id FROM games WHERE game_id = ?", (game_id,)) as cursor:
                result = await cursor.fetchone()
                if result is not None:
                    host_id = result[0]  
                    return host_id
                else:
                    return result
        
async def get_blue_team_players_by_game_id(game_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT discord_id FROM users WHERE game_id = ? AND team = ?", (game_id, "blue")) as cursor:
            players = await cursor.fetchall()
            return [player[0] for player in players]
        
async def get_orange_team_players_by_game_id(game_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT discord_id FROM users WHERE game_id = ? AND team = ?", (game_id, "orange")) as cursor:
            players = await cursor.fetchall()
            return [player[0] for player in players]
        
async def get_player_elo(player_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT elo FROM users WHERE discord_id = ?", (player_id,)) as cursor:
            elo = await cursor.fetchone()
            return elo[0] if elo else None

async def update_player_elo(player_id, new_elo):
    async with aiosqlite.connect('Main.db') as db:
        await db.execute("UPDATE users SET elo = ? WHERE discord_id = ?", (new_elo, player_id))
        await db.commit()

async def add_a_win(player_id):
    async with aiosqlite.connect('Main.db') as db:
        await db.execute("UPDATE users SET wins = wins + 1 WHERE discord_id = ?", (player_id,))
        await db.commit()

async def add_a_lose(player_id):
    async with aiosqlite.connect('Main.db') as db:
        await db.execute("UPDATE users SET losses = losses + 1 WHERE discord_id = ?", (player_id,))
        await db.commit()

async def leave_a_game(player_id):
    async with aiosqlite.connect('Main.db') as db:
        await db.execute("UPDATE users SET status = ?, game_id = ?, team = ? WHERE discord_id = ?", ("inactive", "0", None, player_id))
        await db.commit()
        
async def get_rank_by_game_id(game_id):
    async with aiosqlite.connect('Main.db') as db:
        async with db.execute("SELECT rank FROM games WHERE game_id = ?", (game_id,)) as cursor:
                result = await cursor.fetchone()
                if result is not None:
                    rank = result[0]  
                    return rank
                else:
                    return result