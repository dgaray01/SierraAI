
---

# SierraAI Discord Bot

## Installation Steps

### 1. Clone the Repository

Clone the SierraAI repository from GitHub:

```bash
git clone https://github.com/dgaray01/SierraAI.git
cd SierraAI/discord
```

### 2. Install Node.js

Ensure you have Node.js version 20.x.x installed. Check your current version with:

```bash
node -v
```

If needed, install or update Node.js to version 20.x.x. You can download it from the [Node.js official website](https://nodejs.org/).

### 3. Install Dependencies

In the `discord` directory of the repository, install the required dependencies:

```bash
npm install
```

### 4. Set Up Configuration

1. **Create a Discord Bot**: Go to the [Discord Developer Portal](https://discord.com/developers/applications), create a new bot, and copy your bot token.

2. **Create a `.env` File**:

   In the `discord` directory, create a file named `.env` and add the following line:

   ```env
   DISCORD_TOKEN= # Your Discord Bot Token
   CLIENT_ID= # Your Discord Bot Application Token
   API_URL= # The HTTP server's URL
   API_TOKEN= # Your HTTP server's API Token
   ```

   Replace `your-bot-token-here` with the token you copied from the Discord Developer Portal.

### 5. Start the Bot

Run the bot using Node.js:

```bash
npm start
```

Your bot should now be running and connected to your Discord server.

---

Feel free to add any additional setup or troubleshooting steps if needed!
