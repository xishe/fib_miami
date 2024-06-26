import disnake
from disnake.ext import commands
import aiosqlite
import datetime
import os
import asyncio

# Инициализация базы данных
async def init_db():
    async with aiosqlite.connect('faction_management.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                discord_id INTEGER UNIQUE,
                                user_name TEXT
                            )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS actions (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT
                            )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS logs (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                guild_id INTEGER,
                                guild_name TEXT,
                                user_id INTEGER,
                                author_id INTEGER,
                                timestamp TEXT,
                                action_id INTEGER,
                                passport TEXT,
                                rank TEXT,
                                reason TEXT,
                                system TEXT,
                                FOREIGN KEY(user_id) REFERENCES users(discord_id),
                                FOREIGN KEY(author_id) REFERENCES users(discord_id),
                                FOREIGN KEY(action_id) REFERENCES actions(id)
                            )''')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_guild_id ON logs(guild_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON logs(user_id)')
        await db.commit()

class FactionManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(init_db())

    # Функция для сохранения логов пользователя в базу данных
    async def log_user_action(self, guild_id, guild_name, user_id, user_name, author_id, author_name, action, passport=None, rank=None, reason=None, system=None):
        async with aiosqlite.connect('faction_management.db') as db:
            await db.execute('INSERT OR IGNORE INTO users (discord_id, user_name) VALUES (?, ?)', (user_id, user_name))
            await db.execute('INSERT OR IGNORE INTO users (discord_id, user_name) VALUES (?, ?)', (author_id, author_name))
            await db.execute('INSERT OR IGNORE INTO actions (name) VALUES (?)', (action,))
            await db.execute('''INSERT INTO logs (guild_id, guild_name, user_id, author_id, timestamp, action_id, passport, rank, reason, system) 
                                VALUES (?, ?, ?, ?, ?, (SELECT id FROM actions WHERE name = ?), ?, ?, ?, ?)''',
                             (guild_id, guild_name, user_id, author_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), action, passport, rank, reason, system))
            await db.commit()

    # Функция для создания embed сообщений
    def create_embed(self, title, color, fields, inline_fields):
        embed = disnake.Embed(title=title, color=color)
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
        for name, value in inline_fields.items():
            embed.add_field(name=name, value=value, inline=True)
        embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return embed

    @commands.slash_command(description="Принять игрока во фракцию")
    async def invite(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Участник, которого принимают"),
        passport: str = commands.Param(description="Static ID"),
        rank: str = commands.Param(description="Ранг, на который принимается игрок", default="1"),
        reason: str = commands.Param(description="Причина принятия", default="Набор/заявка")
    ):
        inviter_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        invitee_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        await self.log_user_action(inter.guild.id, inter.guild.name, member.id, member.display_name, inter.author.id, inter.author.display_name, "Принят", passport, rank, reason)

        fields = {
            "Принял(а):": inviter_details,
            "Принят(а):": invitee_details
        }
        inline_fields = {
            "Номер паспорта": passport,
            "Действие": f"Принят на {rank} ранг",
            "Причина": reason
        }

        embed = self.create_embed("Кадровый аудит • Принятие", disnake.Color.blue(), fields, inline_fields)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Изменить ранг игроку во фракции")
    async def rank(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Участник, которому изменяют ранг"),
        action: str = commands.Param(description="Действие (повышение/понижение) | Пример: Повышен с 7 на 8 ранг"),
        reason: str = commands.Param(description="Причина изменение ранга (ссылка на отчёт)"),
        passport: str = commands.Param(description="Static ID")
    ):
        changer_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        changee_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        await self.log_user_action(inter.guild.id, inter.guild.name, member.id, member.display_name, inter.author.id, inter.author.display_name, "Изменен ранг", passport, action, reason)

        fields = {
            "Обновил(а) ранг:": changer_details,
            "Обновлен(а):": changee_details
        }
        inline_fields = {
            "Номер паспорта": passport,
            "Действие": action
        }
        embed = self.create_embed("Кадровый аудит • Изменение ранга", disnake.Color.green(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Назначить на должность")
    async def appoint(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Участник, которого назначают"),
        reason: str = commands.Param(description="Причина назначения | На кого назначен"),
        system: disnake.TextChannel = commands.Param(description="Система повышения (дискорд канал)"),
        passport: str = commands.Param(description="Static ID")
    ):
        assigner_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        assignee_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        await self.log_user_action(inter.guild.id, inter.guild.name, member.id, member.display_name, inter.author.id, inter.author.display_name, "Назначен", passport, None, reason, system.name)

        fields = {
            "Назначил(а):": assigner_details,
            "Назначен(а):": assignee_details
        }
        inline_fields = {
            "Номер паспорта": passport,
            "Система повышения": system.mention
        }
        embed = self.create_embed("Кадровый аудит • Назначение на должность", disnake.Color.purple(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Уволить игрока из фракции (нет в Discord)")
    async def uval_nik(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user_name: str = commands.Param(description="Имя и фамилия игрока"),
        passport: str = commands.Param(description="Static ID"),
        reason: str = commands.Param(description="Причина увольнения | Ссылка на заявление на увольнение")
    ):
        remover_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        await self.log_user_action(inter.guild.id, inter.guild.name, user_name, user_name, inter.author.id, inter.author.display_name, "Уволен (нет в Discord)", passport, None, reason)

        fields = {
            "Уволил(а):": remover_details,
            "Уволен(а):": user_name
        }
        inline_fields = {
            "Номер паспорта": passport
        }
        embed = self.create_embed("Кадровый аудит • Увольнение (нет в Discord)", disnake.Color.red(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)
        await inter.response.send_message(embed=embed)

    @commands.slash_command(description="Уволить игрока из фракции")
    async def uval(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Участник, которого увольняют"),
        reason: str = commands.Param(description="Причина увольнения"),
        passport: str = commands.Param(description="Static ID")
    ):
        remover_details = f"{inter.author.mention} | {inter.author.display_name} | ||{inter.author.id}||"
        removed_details = f"{member.mention} | {member.display_name} | ||{member.id}||"
        await self.log_user_action(inter.guild.id, inter.guild.name, member.id, member.display_name, inter.author.id, inter.author.display_name, "Уволен", passport, None, reason)

        fields = {
            "Уволил(а):": remover_details,
            "Уволен(а):": removed_details
        }
        inline_fields = {
            "Номер паспорта": passport
        }
        embed = self.create_embed("Кадровый аудит • Увольнение", disnake.Color.red(), fields, inline_fields)
        embed.add_field(name='Причина', value=reason, inline=False)
        await inter.response.send_message(embed=embed)
        if inter.author.top_role > member.top_role:
            await member.kick(reason=reason)  # Кикаем пользователя с сервера

    @commands.slash_command(description="Показать логи пользователя")
    async def logs(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(description="Участник, чьи логи показываем")
    ):
        async with aiosqlite.connect('faction_management.db') as db:
            c = await db.execute('''SELECT logs.timestamp, actions.name, logs.passport, logs.rank, logs.reason, logs.system, logs.user_id, 
                                    (SELECT user_name FROM users WHERE discord_id = logs.user_id) AS user_name, logs.author_id, 
                                    (SELECT user_name FROM users WHERE discord_id = logs.author_id) AS author_name 
                                    FROM logs 
                                    JOIN actions ON logs.action_id = actions.id 
                                    WHERE (logs.user_id = ? AND logs.guild_id = ?) OR (logs.author_id = ? AND logs.guild_id = ?)''',
                                    (member.id, inter.guild.id, member.id, inter.guild.id))
            logs = await c.fetchall()

        if not logs:
            await inter.response.send_message(f"Логи для пользователя {member.mention} не найдены.", ephemeral=True)
            return

        # Функция для разбивки списка на части
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        # Максимальное количество логов на одной странице
        max_logs_per_page = 3
        log_pages = list(chunks(logs, max_logs_per_page))

        # Создание страницы с логами
        def create_embed(page, page_num, total_pages):
            embed = disnake.Embed(
                title=f"Логи пользователя {member.display_name} (Страница {page_num}/{total_pages})",
                color=disnake.Color.blue()
            )
            for log in page:
                embed.add_field(
                    name=f"{log[0]}: {log[1]}",
                    value=f"Паспорт: {log[2]}, Ранг: {log[3]}, Причина: {log[4]}, Система: {log[5]}, "
                          f"Пользователь: {log[7]} (ID: {log[6]}), Автор: {log[9]} (ID: {log[8]})",
                    inline=False
                )
            return embed

        # Отправка первой страницы
        current_page = 0
        total_pages = len(log_pages)
        embed = create_embed(log_pages[current_page], current_page + 1, total_pages)
        components = [
            disnake.ui.Button(label="⬅️", custom_id="prev_page", style=disnake.ButtonStyle.secondary),
            disnake.ui.Button(label="➡️", custom_id="next_page", style=disnake.ButtonStyle.secondary),
            disnake.ui.Button(label="Скачать полные логи", custom_id="download_logs", style=disnake.ButtonStyle.primary)
        ]

        await inter.response.send_message(embed=embed, components=components, ephemeral=True)
        message = await inter.original_message()

        # Обработчик для кнопок
        while True:
            try:
                button_inter = await self.bot.wait_for(
                    "interaction",
                    check=lambda i: i.data["custom_id"] in ["prev_page", "next_page", "download_logs"] and i.message.id == message.id,
                    timeout=60.0
                )

                if button_inter.data["custom_id"] == "next_page" and current_page < total_pages - 1:
                    current_page += 1
                    embed = create_embed(log_pages[current_page], current_page + 1, total_pages)
                    await button_inter.response.edit_message(embed=embed)

                elif button_inter.data["custom_id"] == "prev_page" and current_page > 0:
                    current_page -= 1
                    embed = create_embed(log_pages[current_page], current_page + 1, total_pages)
                    await button_inter.response.edit_message(embed=embed)

                elif button_inter.data["custom_id"] == "download_logs":
                    filename = f"user_logs_{member.id}_{inter.guild.id}.html"
                    await self.create_html_file_for_logs({inter.guild.id: {"guild_name": inter.guild.name, "logs": logs}}, filename, inter.guild.name)
                    await button_inter.response.send_message(
                        "Полные логи можно скачать ниже.", file=disnake.File(filename), ephemeral=True
                    )
                    os.remove(filename)
            except asyncio.TimeoutError:
                break

    @commands.slash_command(description="Показать все логи")
    @commands.has_permissions(administrator=True)
    async def all_logs(self, inter):
        async with aiosqlite.connect('faction_management.db') as db:
            c = await db.execute('''SELECT guild_id, guild_name, timestamp, actions.name, passport, rank, reason, system, user_id, 
                                    (SELECT user_name FROM users WHERE discord_id = user_id) AS user_name, author_id, 
                                    (SELECT user_name FROM users WHERE discord_id = author_id) AS author_name 
                                    FROM logs 
                                    JOIN actions ON logs.action_id = actions.id''')
            logs = await c.fetchall()

        if not logs:
            await inter.response.send_message("Нет логов для отображения.", ephemeral=True)
            return

        logs = sorted(logs, key=lambda x: x[2])
        logs_by_guild = {}
        for log in logs:
            guild_id = log[0]
            guild_name = log[1]
            if guild_id not in logs_by_guild:
                logs_by_guild[guild_id] = {
                    "guild_name": guild_name,
                    "logs": []
                }
            logs_by_guild[guild_id]["logs"].append(log)

        filename = 'all_user_logs.html'
        await self.create_html_file_for_all_logs(logs_by_guild, filename, "All Servers")
        await inter.response.send_message("Полные логи можно скачать ниже.", file=disnake.File(filename), ephemeral=True)
        os.remove(filename)

    # Функция для создания HTML файла с логами для команды /logs
    async def create_html_file_for_logs(self, logs_by_guild, filename, guild_name):
        html_content = '''
        <html>
        <head>
            <title>User Logs</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                table, th, td { border: 1px solid #ccc; }
                th, td { padding: 10px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
        '''
        html_content += f"<h1>User Logs - {guild_name}</h1>"

        # Создание логов по серверу
        for guild_id, guild_info in logs_by_guild.items():
            html_content += f'<h2 id="guild_{guild_id}">Сервер {guild_info["guild_name"]} (ID: {guild_id})</h2>'
            html_content += '''
            <table>
                <tr>
                    <th>Время</th>
                    <th>Действие</th>
                    <th>Паспорт</th>
                    <th>Ранг</th>
                    <th>Причина</th>
                    <th>Система</th>
                    <th>ID Пользователя</th>
                    <th>Имя Пользователя</th>
                    <th>ID Автора</th>
                    <th>Имя Автора</th>
                </tr>
            '''
            for log in guild_info["logs"]:
                timestamp = log[0]
                action = log[1]
                passport = log[2]
                rank = log[3]
                reason = log[4]
                system = log[5]
                user_id = log[6]
                user_name = log[7]
                author_id = log[8]
                author_name = log[9]
                html_content += f"<tr><td>{timestamp}</td><td>{action}</td><td>{passport}</td><td>{rank}</td><td>{reason}</td><td>{system}</td><td>{user_id}</td><td>{user_name}</td><td>{author_id}</td><td>{author_name}</td></tr>"
            html_content += '</table>'

        html_content += "</body></html>"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    # Функция для создания HTML файла с логами для команды /all_logs
    async def create_html_file_for_all_logs(self, logs_by_guild, filename, guild_name):
        html_content = '''
        <html>
        <head>
            <title>User Logs</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1, h2 { color: #333; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                table, th, td { border: 1px solid #ccc; }
                th, td { padding: 10px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
        '''
        html_content += f"<h1>User Logs - {guild_name}</h1>"

        # Создание оглавления
        html_content += "<h2>Список серверов</h2><ul>"
        for guild_id, guild_info in logs_by_guild.items():
            html_content += f'<li><a href="#guild_{guild_id}">Сервер {guild_info["guild_name"]} (ID: {guild_id})</a></li>'
        html_content += "</ul>"

        # Создание логов по серверам
        for guild_id, guild_info in logs_by_guild.items():
            html_content += f'<h2 id="guild_{guild_id}">Сервер {guild_info["guild_name"]} (ID: {guild_id})</h2>'
            html_content += '''
            <table>
                <tr>
                    <th>Время</th>
                    <th>Действие</th>
                    <th>Паспорт</th>
                    <th>Ранг</th>
                    <th>Причина</th>
                    <th>Система</th>
                    <th>ID Пользователя</th>
                    <th>Имя Пользователя</th>
                    <th>ID Автора</th>
                    <th>Имя Автора</th>
                </tr>
            '''
            for log in guild_info["logs"]:
                timestamp = log[2]
                action = log[3]
                passport = log[4]
                rank = log[5]
                reason = log[6]
                system = log[7]
                user_id = log[8]
                user_name = log[9]
                author_id = log[10]
                author_name = log[11]
                html_content += f"<tr><td>{timestamp}</td><td>{action}</td><td>{passport}</td><td>{rank}</td><td>{reason}</td><td>{system}</td><td>{user_id}</td><td>{user_name}</td><td>{author_id}</td><td>{author_name}</td></tr>"
            html_content += '</table>'

        html_content += "</body></html>"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)


def setup(bot):
    bot.add_cog(FactionManagement(bot))
