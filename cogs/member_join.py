import disnake
from disnake.ext import commands
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel_id = 1250907992988323972  # Замените на реальный ID канала
        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            embed = disnake.Embed(
                title="Добро пожаловать во фракцию FIB",
                description="Перед началом работы, тебе нужно изменить никнейм на сервере по этой форме:\n\n"
                            "**Отдел | Имя Фамилия | Static ID** \n\n"
                            "Пример:\n"
                            "TR | Rick Immortal | 43642",
                color=0x2F3136,
                timestamp=datetime.datetime.now()
            )
            embed.set_thumbnail(url='https://i1.imageban.ru/out/2024/06/13/a041166e5540d54d088f3ae5ad0b9d6a.webp')
            embed.set_footer(text=f"ID пользователя: {member.id}")
            await channel.send(f'{member.mention}', embed=embed)

def setup(bot):
    bot.add_cog(Moderation(bot))
