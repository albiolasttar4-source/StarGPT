import discord
import requests
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

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
            await message.reply(answer[:2000])  # Discord limit ay 2000 chars
        else:
            await message.reply(f"Error: {response.status_code}")

    except Exception as e:
        await message.reply(f"Sorry, error: {str(e)}")

client.run(TOKEN)
