# SRLC 6 Mans Discord Bot

## Overview

This Discord bot is designed to enhance the gaming experience for players participating in the SRLC 6 Mans matchs. The bot automates various processes, including game creation, player queue management, and game tracking.

## Features

- **Automated Game Creation**: The bot can create games dynamically based on player participation.
- **Player Queue Management**: Players can join queues for specific game types, and the bot handles the organization of these players.
- **Rank-based Matching**: Players are matched based on their ranks, ensuring balanced competition.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Aitaneuh/SRLC-3.0.git
   cd SRLC-3.0
   ```

2. **Install Dependencies**:
   Make sure you have Python 3.8 or higher installed. You can install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   Create a `.env` file in the root directory and add your Discord bot token:
   ```bash
   DISCORD_TOKEN=your_discord_bot_token
   ```

4. **Run the Bot**:
   Start the bot using:
   ```bash
   python main.py
   ```

## Usage

Once the bot is running, you can interact with it in your Discord server. Use the following commands to get started:

- **!queue**: Join the game queue.
- **!leave**: Leave the queue.
- **!status**: Check the status of the queue.

## Database

The bot uses SQLite for storing game and user data. The database schema includes tables for `games` and `users`, which manage game states and player statuses.

### Example Database Schema

```sql
CREATE TABLE "games" (
    "game_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "host_id" TEXT,
    "rank" TEXT,
    "status" TEXT
);

CREATE TABLE "users" (
      "discord_id" TEXT, 
      "elo" INTEGER, 
      "rank" TEXT, 
      "wins" INTEGER DEFAULT 0, 
      "losses" INTEGER DEFAULT 0, 
      "status" TEXT, 
      "game_id" INTEGER DEFAULT 0, 
      "team" TEXT
);
```

## Contact

For any questions or support, feel free to reach out to the project maintainer:
- **Ethan**: [Aitaneuh](https://discordapp.com/users/677579030966304769)

---

Thank you for checking out the SRLC 6 Mans Discord Bot!
