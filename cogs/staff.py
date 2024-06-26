import disnake
from disnake.ext import commands
import datetime
import asyncio


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_staff_embeds(self, ctx, role_groups, title, channel_id):
        await ctx.message.delete()  # Удалить сообщение с вызовом команды

        channel = self.bot.get_channel(channel_id)
        guild = self.bot.get_guild(ctx.guild.id)

        if channel is None or guild is None:
            await ctx.send("Не удалось найти указанный канал или гильдию.")
            return

        def create_embed(title="", footer=False):
            embed = disnake.Embed(title=title, color=0x2F3136)
            if footer:
                embed.timestamp = datetime.datetime.now()
            return embed

        async def send_embeds():
            messages = []
            users_ids = [member.id for member in guild.members]
            checked_members = set()

            embeds = []
            for index, (group, roles) in enumerate(role_groups.items()):
                group_members = []

                for min_role in roles:
                    for i in range(len(users_ids)):
                        if users_ids[i] not in checked_members:
                            member = guild.get_member(users_ids[i])
                            if member is None:
                                continue
                            for mem_role in reversed(member.roles):
                                if min_role == mem_role.id and users_ids[i] not in checked_members:
                                    group_members.append(
                                        f"{len(group_members) + 1}. {mem_role.name} - {member.mention}")
                                    checked_members.add(users_ids[i])
                                    break

                if group_members:
                    chunks = [group_members[i:i + 30] for i in range(0, len(group_members), 30)]
                    for chunk_index, chunk in enumerate(chunks):
                        group_value = "\n".join(chunk)
                        current_embed = create_embed(
                            title=title if index == 0 and chunk_index == 0 else "")
                        current_embed.add_field(name=group, value=group_value, inline=False)
                        embeds.append(current_embed)

            if embeds:
                embeds[-1].timestamp = datetime.datetime.now()  # Установить временную метку только на последний Embed
                embeds[-1].set_footer(text="Актуально на", icon_url=f'{ctx.guild.icon.url}')

            for embed in embeds:
                msg = await channel.send(embed=embed)
                messages.append(msg)

            return messages

        previous_messages = await send_embeds()

        try:
            while True:
                await asyncio.sleep(3600)  # Ожидание перед каждым обновлением (1 час)
                for msg in previous_messages:
                    try:
                        await msg.delete()
                    except disnake.NotFound:
                        continue

                previous_messages = await send_embeds()

        except asyncio.CancelledError:
            pass  # Просто выходим из цикла, если задача отменена

        for msg in previous_messages:
            try:
                await msg.delete()
            except disnake.NotFound:
                continue

    @commands.command()
    async def staff_fa(self, ctx):
        role_groups = {
            'Curator FA': [1250800154014126163],
            'Free Agent': [1119257099562655847],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Free Agents", 1162247635567128697)

    @commands.command()
    async def staff_dea(self, ctx):
        role_groups = {
            'Curator of DEA': [1250912389986127952],
            'Head of DEA': [1119407809830846504],
            'Deputy Head of DEA': [1119408519809085551],
            'Instructor of DEA': [1119409964608393226],
            'Drug Enforcement Administration': [1119414502174232606],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Drug Enforcement Administration", 1119511363606298665)

    @commands.command()
    async def staff_hrt(self, ctx):
        role_groups = {
            'Curator of HRT': [1250912248596267009],
            'Head of HRT': [1119257099600396436],
            'Deputy Head of HRT': [1119257099583631449],
            'Instructor of HRT': [1119409956207210639],
            'Hostage Rescue Team': [1119257099583631442],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Hostage Rescue Team", 1119257102351859871)

    @commands.command()
    async def staff_id(self, ctx):
        role_groups = {
            'Curator of ID': [1250911887944585299],
            'Head of ID': [1156136105742188624],
            'Deputy Head of ID': [1156135975655854090],
            'Instructor of ID': [1156135305146023937],
            'Investigation Departament Crime': [1156140102817435698],
            'Investigation Department State': [1156135025197191270],
            'Trainee': [1119411467943432192],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Investigation Department", 1173623873967759422)

    @commands.command()
    async def staff_nsb(self, ctx):
        role_groups = {
            'Curator of NSB': [1250912575848452216],
            'Head of NSB': [1119257099600396434],
            'Deputy Head of NSB': [1119257099583631447],
            'Instructor of NSB': [1119409951366987856],
            'National Security Branch': [1119257099583631440],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав National Security Branch", 1163842995053932546)

    @commands.command()
    async def staff_fna(self, ctx):
        role_groups = {
            'Curator of FNA': [1250912121223643167],
            'Head of FNA': [1119257099600396433],
            'Deputy Head of FNA': [1119257099583631446],
            'Instructor of FNA': [1119409959994663002],
            'Federal National Academy': [1119257099562655853],
        }
        await self.send_staff_embeds(ctx, role_groups, "Состав Federal National Academy", 1119257103429804127)

    @commands.command()
    async def staff_high(self, ctx):
        role_groups = {
            'Director': [1119257099617181792],
            'Deputy Director': [1119257099617181791],
            'Assistant Director': [1119257099617181787],
            'Free Agent': [1250800154014126163],
            'Investigation Department': [1250911887944585299, 1156136105742188624, 1156135975655854090, 1156135305146023937],
            'Federal National Academy': [1250912121223643167, 1119257099600396433, 1119257099583631446, 1119409959994663002],
            'Hostage Rescue Team': [1250912248596267009, 1119257099600396436, 1119257099583631449, 1119409956207210639],
            'Drug Enforcement Administration': [1250912389986127952, 1119407809830846504, 1119408519809085551, 1119409964608393226],
            'National Security Branch': [1250912575848452216, 1119257099600396434, 1119257099583631447, 1119409951366987856],
        }
        await self.send_staff_embeds(ctx, role_groups, "Старший состав FIB", 1171806977010188298)


def setup(bot):
    bot.add_cog(Staff(bot))
