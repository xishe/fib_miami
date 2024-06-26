import disnake
from disnake.ext import commands
import os
import json

# Загрузка конфигурации
with open('config.json', 'r') as f:
    config = json.load(f)

bot = commands.Bot(command_prefix=config['prefix'], intents=disnake.Intents.all())

# Загрузка когов
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")

bot.run(config['token'])
