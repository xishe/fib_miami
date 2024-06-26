import disnake
from disnake.ext import commands


class KAInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ka_info')
    async def ka_info(self, ctx):
        embed1 = disnake.Embed(
            title="Список команд:",
            description="```/invite - Принять игрока во фракцию```\n**Пример использования: **\n\n> /invite **member**:@member \n- **passport**:Static ID,\n\n**Необязательные опции: **\n- **rank**: ранг на который принимается человек,\n- **reason**: ссылка на восстановление/перевод\n\n*Описание: Команда используется для принятия игрока во фракцию с указанием паспортных данных.*",
            color=disnake.Color.blue()
        )

        embed2 = disnake.Embed(
            description="```/rank - Изменить ранг игроку во фракции```\n**Пример использования: **\n\n> /rank **member**: @member \n- **action**: Повышен с 7 на 8 ранг \n- **reason**: причина повышения (ссылка на отчет)\n- **passport**: Static ID\n\n*Описание: Команда для изменения ранга игрока во фракции с указанием причины и паспортных данных.*",
            color=disnake.Color.green()
        )

        embed3 = disnake.Embed(
            description="```/appoint - Назначить на должность```\n**Пример использования: **\n\n> /appoint **member**: @member \n- **reason**: причина назначения \n- **system**: система повышения (дискорд канал)\n- **passport**: Static ID\n\n*Описание: Команда для назначения игрока на должность с указанием причины и паспортных данных.*",
            color=disnake.Color.purple()
        )

        embed4 = disnake.Embed(
            description="```/uval_nik - Уволить игрока из фракции (нет в Discord)```\n**Пример использования: **\n\n> /uval_nik **user_name**: имя и фамилия игрока \n- **passport**: Static ID \n- **reason**: причина увольнения\n\n*Описание: Команда для увольнения игрока из фракции с указанием причины и паспортных данных, если игрока нет в Discord.*",
            color=disnake.Color.red()
        )

        embed5 = disnake.Embed(
            description="```/uval - Уволить игрока из фракции```\n**Пример использования: **\n\n> /uval **member**: @member \n- **reason**: причина увольнения \n- **passport**: Static ID\n\n*Описание: Команда для увольнения игрока из фракции с указанием причины и паспортных данных.*",
            color=disnake.Color.red()
        )

        embed6 = disnake.Embed(
            description="```/logs - Показать логи пользователя```\n**Пример использования: **\n\n> /logs **member**: @member\n\n*Описание: Команда для отображения логов пользователя.*",
            color=disnake.Color.dark_grey()
        )

        await ctx.send(embeds=[embed1, embed2, embed3, embed4, embed5, embed6])


def setup(bot):
    bot.add_cog(KAInfo(bot))
