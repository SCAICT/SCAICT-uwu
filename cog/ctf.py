# Standard imports
from datetime import datetime
import json
import os
import random

# Third-party imports
import discord
from discord.ext import commands
from discord.commands import Option

# Local imports
from build.build import Build
from cog.core.sql import read
from cog.core.sql import write
# 用於結束和SQL資料庫的會話，平常都用end()，但和 Discord 指令變數名稱衝突，所以這裡改名
from cog.core.sql import end as end_sql
from cog.core.sql import link_sql

def get_ctf_makers():
    try:
        with open(f"{os.getcwd()}/DataBase/server.config.json", "r", encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Configuration file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return {}

# By EM
def generate_ctf_id():
    return str(random.randint(100000000000000000, 999999999999999999))

class CTF(Build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.CTFView())

    ctf_commands = discord.SlashCommandGroup("ctf", "CTF 指令")

    class CTFView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout = None) # timeout of the view must be set to None

        @discord.ui.button(
            label = "回報 Flag",
            style = discord.ButtonStyle.blurple,
            emoji = "🚩",
            custom_id = "new_ctf"
        )
        # user送出flag
        # pylint: disable-next = unused-argument
        async def button_callback_1(self, button, interaction):
            class SubmitModal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)
                    self.add_item(
                        discord.ui.InputText(label = "Flag", placeholder = "Flag", required = True))

                async def callback(self, interaction: discord.Interaction):
                    try:
                        connection, cursor = link_sql() # SQL 會話
                        cursor.execute("USE CTF;")
                        question_id = interaction.message.embeds[0].footer.text.split(": ")[1]
                        # startTime
                        cursor.execute(f"SELECT start_time FROM data WHERE id={question_id};")
                        start_time = str(cursor.fetchone()[0])
                        # endTime
                        cursor.execute(f"SELECT end_time FROM data WHERE id={question_id};")
                        end = str(cursor.fetchone()[0])

                        # 判斷是否在作答時間內
                        current_time = datetime.now()
                        if datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') > current_time:
                            await interaction.response.send_message("答題時間尚未開始！", ephemeral = True)
                            end_sql(connection, cursor)
                            return
                        if end != "None" and datetime.strptime(end, '%Y-%m-%d %H:%M:%S') < current_time:
                            await interaction.response.send_message("目前不在作答時間內！", ephemeral = True)
                            end_sql(connection, cursor)
                            return

                        user_id = interaction.user.id
                        nickname = interaction.user
                        # 判斷題目可作答次數
                        # pylint: disable-next = line-too-long
                        cursor.execute(f"SELECT count FROM history WHERE data_id={question_id} AND uid={user_id};")
                        # return None or tuple.like (1,)
                        answer_count = cursor.fetchone() # 使用者回答次數
                        # 第一次作答flag
                        # not_exist = False if answer_count is not None else True
                        not_exist = answer_count is None
                        if not_exist:
                            # 初始化作答次數
                            # pylint: disable-next = line-too-long
                            cursor.execute(f"INSERT INTO history (data_id,uid,count) VALUES ({question_id},{user_id},0);")
                            answer_count = 0
                            # ctfFile[question_id]["history"][str(user_id)] = 0
                        else:
                            answer_count = answer_count[0]
                        cursor.execute(f"SELECT restrictions FROM data WHERE id={question_id};")
                        restrictions = str(cursor.fetchone()[0]) # 最大作答次數

                        # 無限沒辦法比大小，不用判斷有沒有超過限制
                        if restrictions != '∞':
                            # 判斷使用者是否超過每人限制次數
                            if answer_count >= int(restrictions):
                                await interaction.response.send_message(
                                    "你已經回答超過限制次數了喔！", ephemeral = True)
                                end_sql(connection, cursor)
                                return

                        # 更新作答次數，包括總表和個人表
                        # pylint: disable-next = line-too-long
                        cursor.execute(f"UPDATE history SET count=count+1 WHERE data_id={question_id} AND uid={user_id};")
                        answer_count += 1 # SQL和變數同步，變數之後還要用
                        cursor.execute(f"UPDATE data SET tried=tried+1 WHERE id={question_id};")

                        # 製造 embed 前置作業-取得必要數值
                        cursor.execute(f"SELECT tried FROM data WHERE id={question_id};")
                        total_tried = int(cursor.fetchone()[0]) # 該題總共嘗試次數
                        # pylint: disable-next = line-too-long
                        cursor.execute(f"SELECT COUNT(*) FROM history WHERE data_id={question_id} AND solved=1;")
                        total_solved = int(cursor.fetchone()[0]) # 該題完成人數

                        # 取得使用者輸入的 flag
                        response_flag = self.children[0].value
                        cursor.execute(f"SELECT flags FROM data WHERE id={question_id};")
                        answer = str(cursor.fetchone()[0])
                        # 輸入內容為正確答案
                        if response_flag == answer:
                            # 判斷是否重複回答
                            # pylint: disable-next = line-too-long
                            cursor.execute(f"SELECT solved FROM history WHERE data_id={question_id} AND uid={user_id};")
                            is_solved = int(cursor.fetchone()[0])
                            if is_solved:
                                embed = discord.Embed(title = "答題成功!")
                                embed.add_field(
                                    name = "",
                                    value = "但你已經解答過了所以沒有 :zap: 喔！",
                                    inline = False
                                )
                                await interaction.response.send_message(
                                    ephemeral = True, embeds = [ embed ]
                                )
                                return
                            # else 未曾回答過，送獎勵
                            # pylint: disable-next = line-too-long
                            cursor.execute(f"UPDATE history SET solved=1 WHERE data_id={question_id} AND uid={user_id};")
                            cursor.execute(f"SELECT score FROM data WHERE id={question_id};")
                            reward = int(cursor.fetchone()[0])
                            cursor.execute("USE CTF;") # 換資料庫存取電電點
                            current_point = read(user_id, "point", cursor)
                            new_point = current_point + reward
                            # 更新使用者電電點
                            write(user_id, "point", new_point, cursor)
                            # 更新作答狀態
                            # log
                            print(f'{user_id}, {nickname} Get {reward} by ctf, {str(datetime.now())}')

                            embed = discord.Embed(title = "答題成功!")
                            embed.add_field(
                                name = "+" + str(reward) + ":zap:",
                                value = "=" + str(new_point),
                                inline = False
                            )
                            await interaction.response.send_message(
                                embeds = [ embed ], ephemeral = True
                            )
                        else:
                            embed = discord.Embed(title = "答案錯誤!")
                            embed.add_field(
                                name = "嘗試次數",
                                value = str(answer_count) + "/" + str(restrictions),
                                inline = False
                            )
                            await interaction.response.send_message(
                                embeds = [ embed ], ephemeral = True
                            )

                        # edit the original message
                        # 更新題目顯示狀態
                        embed = interaction.message.embeds[0]
                        embed.set_field_at(0, name = "已完成", value = str(total_solved), inline = True)
                        embed.set_field_at(1, name = "已嘗試", value = str(total_tried), inline = True)
                        embed.set_field_at(2, name = "回答次數限制", value = str(restrictions), inline = True)
                        # set the new embed
                        await interaction.message.edit(embed = embed)
                    # pylint: disable-next = broad-exception-caught
                    except Exception as exception:
                        print(f"Error: {exception}")

                    end_sql(connection, cursor) # 結束SQL會話

            await interaction.response.send_modal(SubmitModal(title = "你找到 flag 了嗎？"))

    @ctf_commands.command(name = "create", description = "新題目")
    # 新增題目
    async def create(
        self,
        ctx,
        title: Option(str, "題目標題", required = True, default = ''),
        flag: Option(str, "輸入 flag 解答", required = True, default = ''),
        score: Option(int, "分數", required = True, default = '20'),
        limit: Option(int, "限制回答次數", required = False, default = ''),
        case: Option(bool, "大小寫忽略", required = False, default = False),
        # pylint: disable-next = line-too-long
        start: Option(str, f"開始作答日期 ({datetime.now().strftime('%y-%m-%d %H:%M:%S')})", required = False, default = ""), # 時間格式
        # pylint: disable-next = line-too-long
        end: Option(str, f"截止作答日期 ({datetime.now().strftime('%y-%m-%d %H:%M:%S')})", required = False, default = "")):
        # SQL沒有布林值，所以要將T/F轉換成0或1
        case = 1 if case else 0
        # get ctf maker role's ID
        role_id = get_ctf_makers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]
        # Check whether the user can send a question or not
        role = discord.utils.get(ctx.guild.roles, id = role_id)
        if role not in ctx.author.roles:
            await ctx.respond("你沒有權限建立題目喔！", ephemeral = True)
            return
        # 確認是否有填寫 title 和 flag
        if title == '' or flag == '':
            await ctx.respond("請填寫題目標題和 flag", ephemeral = True)
            return
        # ctfFile = get_ctf_file()

        try:
            connection, cursor = link_sql() # SQL 會話
            cursor.execute("USE CTF;")
            while True:
                new_id = generate_ctf_id()
                # 找尋是否有重複的ID，若無則跳出迴圈
                cursor.execute(
                    f"select id from data WHERE EXISTS(select id from data WHERE id={new_id});")
                id_exist = cursor.fetchone()
                if id_exist is None:
                    break
            # 轉型成SQL datetime格式 %Y-%m-%d %H:%M:%S
            start = (
                datetime.strptime(start, '%Y-%m-%d %H:%M:%S') if start != "" else
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            end = f"'{datetime.strptime(end, '%Y-%m-%d %H:%M:%S')}'" if end != "" else "NULL"
            # limit若沒有填寫，設為可嘗試無限次
            limit = "∞" if limit == "" else limit
            embed = discord.Embed(
                title = title,
                description = "+" + str(score) + "⚡",
                color = 0xff24cf,
            )
            embed.set_author(
                name = "SCAICT CTF",
                icon_url = "https://cdn-icons-png.flaticon.com/128/14929/14929899.png"
            )
            embed.set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
            embed.add_field(name = "已完成", value = "0", inline = True)
            embed.add_field(name = "已嘗試", value = "0", inline = True)
            embed.add_field(name = "回答次數限制", value = f"0/{limit}", inline = True)
            embed.add_field(name = "開始作答日期", value = start, inline = True)
            embed.add_field(name = "截止作答日期", value = end, inline = True)
            embed.add_field(name = "", value="", inline = False)
            embed.add_field(name = "可於下方討論，但請勿公布答案", value = "", inline = False)
            embed.set_footer(text = "題目 ID: " + new_id)
            # embed格式別亂改，會影響回應訊息時取值
            await ctx.respond("已成功建立題目！", ephemeral = True)
            response = await ctx.send(embed = embed, view = self.CTFView())
            message_id = response.id

            # 在CTF資料庫中的data資料表新增一筆CTF資料
            # print(f"INSERT INTO `data`\
            # (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) VALUES \
            # ({new_id},'{flag}',{score},'{limit}',{message_id},{case},'{start}',{end},\'{title}\',{0});")
            cursor.execute(f"INSERT INTO `data`\
            (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) VALUES \
            ({new_id},'{flag}',{score},'{limit}',{message_id},{case},'{start}',{end},\'{title}\',{0});")
            # CTFID,flag,score,可嘗試次數,message_id,大小寫限制,作答開始時間,作答結束時間,題目標題,已嘗試人數
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            print(f"Error: {exception}")

        end_sql(connection, cursor)

# 刪除題目，等等寫
    # @ctf_commands.command(name = "delete", description = "刪除題目")
    # async def delete_ctf(self, ctx, question_id: str):
    #     role_id = get_ctf_makers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]
    # @ctf_commands.command(description = "列出所有題目")
    @ctf_commands.command(description="列出所有題目")
    async def list_all(self, ctx):
        question_list = ["# **CTF 題目列表:**"]
        connection, cursor=link_sql()
        cursor.execute("use CTF;")
        cursor.execute("SELECT title,score,id FROM data")
        ctfinfo=cursor.fetchall()
        for title,score,qID in ctfinfo:
            question_list.append(
                f"* **{title}** - {score} :zap: *({qID})*")
        question_text = "\n".join(question_list)
        await ctx.respond(question_text)
        end_sql(connection, cursor)

def setup(bot):
    bot.add_cog(CTF(bot))
