import disnake
from disnake.ext import commands
import json
import datetime

class EmbedSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="say",
        description="Отправляет настраиваемое embed сообщение в канал."
    )
    async def say(self, inter: disnake.ApplicationCommandInteraction,
                  content: str = commands.Param(default="", description="Текст перед embed сообщением."),
                  embed_json: str = commands.Param(
                      name='embed_json',
                      description="Создайте embed_json на сайте: https://oldeb.nadeko.bot/"
                  )):
        await inter.response.defer(ephemeral=True)

        try:
            data = json.loads(embed_json)

            embed = disnake.Embed(
                title=data.get("title", "Без заголовка"),
                description=data.get("description", ""),
                color=disnake.Color(data.get("color", 0)),
                timestamp=datetime.datetime.now()
            )

            author_info = data.get("author")
            if author_info:
                embed.set_author(name=author_info.get("name", ""), icon_url=author_info.get("icon_url", ""))

            footer_info = data.get("footer")
            if footer_info:
                embed.set_footer(text=footer_info.get("text", ""), icon_url=footer_info.get("icon_url", ""))
            elif inter.author.avatar:
                embed.set_footer(text=f"{inter.author.display_name}", icon_url=inter.author.avatar.url)

            thumbnail_url = data.get("thumbnail")
            if thumbnail_url:
                embed.set_thumbnail(url=thumbnail_url)

            image_url = data.get("image")
            if image_url:
                embed.set_image(url=image_url)

            for field in data.get("fields", []):
                embed.add_field(name=field.get("name", "Без названия"), value=field.get("value", ""),
                                inline=field.get("inline", False))

            if content or data.get("plainText", "") or embed.fields or embed.title or embed.description:
                await inter.channel.send(content=content, embed=embed)
                await inter.edit_original_response(content="✔ Сообщение успешно отправлено.", embed=None)
            else:
                await inter.edit_original_response(content="❌ Сообщение не может быть пустым.", embed=None)

        except json.JSONDecodeError:
            await inter.followup.send("❌ Ошибка: Введенные данные не являются валидным JSON.", ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"❌ Непредвиденная ошибка: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(EmbedSender(bot))
