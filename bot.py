import discord
import requests
import os
import json

TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = 1448909951602004008  # ✅ Discord ID mo (ikaw ang owner)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# File para i-save ang channel ID (para hindi mawala kahit mag-restart)
CHANNEL_FILE = "channel_config.json"

def get_channel_id():
    if os.path.exists(CHANNEL_FILE):
        with open(CHANNEL_FILE, "r") as f:
            data = json.load(f)
            return data.get("channel_id", 0)
    return 0

def save_channel_id(channel_id):
    with open(CHANNEL_FILE, "w") as f:
        json.dump({"channel_id": channel_id}, f)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    channel_id = get_channel_id()
    if channel_id:
        print(f"📡 Bot is active in channel ID: {channel_id}")
    else:
        print("⚠️ Bot is disabled. Use /setchannel #channel to activate.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 🔥 COMMAND: /setchannel (owner only)
    if message.content.startswith("/setchannel"):
        # Check kung owner ang gumamit
        if message.author.id != OWNER_ID:
            await message.reply("❌ Only the bot owner can use this command.")
            return

        # Kunin ang channel mention (ex: #general)
        parts = message.content.split()
        if len(parts) < 2:
            await message.reply("⚠️ Usage: `/setchannel #channel`")
            return

        # Kunin ang channel ID mula sa mention
        channel_mention = parts[1]
        channel_id = int(channel_mention.strip("<#>&"))
        
        save_channel_id(channel_id)
        await message.reply(f"✅ Bot will now reply in <#{channel_id}>")
        return

    # 🔥 COMMAND: /disable (owner only - stop replying anywhere)
    if message.content.startswith("/disable"):
        if message.author.id != OWNER_ID:
            await message.reply("❌ Only the bot owner can use this command.")
            return
        
        save_channel_id(0)
        await message.reply("✅ Bot disabled. It will not reply to any channel. Use `/setchannel #channel` to enable again.")
        return

    # 🔥 COMMAND: /status (anyone - check kung enabled ang bot)
    if message.content.startswith("/status"):
        channel_id = get_channel_id()
        if channel_id:
            await message.reply(f"✅ Bot is active and replying in <#{channel_id}>")
        else:
            await message.reply("⚠️ Bot is currently disabled. Ask the owner to use `/setchannel`.")
        return

    # ✅ Normal AI reply (check kung enabled at nasa tamang channel)
    channel_id = get_channel_id()
    if channel_id == 0:
        return  # Bot is disabled
    
    if message.channel.id != channel_id:
        return  # Not the right channel

    # AI Reply with typing indicator
    async with message.channel.typing():
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant. Respond in English."},
                {"role": "user", "content": message.content}
            ]
        }

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                if len(answer) > 1900:
                    answer = answer[:1900] + "..."
                await message.reply(answer)
            else:
                await message.reply(f"Error: {response.status_code}")

        except Exception as e:
            await message.reply(f"Sorry, error: {str(e)}")

client.run(TOKEN)
