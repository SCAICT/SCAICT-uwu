# Future statements
from __future__ import annotations

# Standard imports
import datetime
import json
import os
import random
import traceback
import typing

# Third-party imports
import discord
import discord.commands
import discord.ext.commands

# Local imports
import build.build
import cog.core.sql

with open(
    f"{os.getcwd()}/database/server.config.json", "r", encoding="utf-8"
) as server_config:
    stickers = json.load(server_config)["SCAICT-alpha"]["stickers"]


def get_ctf_makers() -> dict:
    try:
        with open(
            f"{os.getcwd()}/database/server.config.json", "r", encoding="utf-8"
        ) as file:
            return json.load(file)
    except FileNotFoundError:
        print("Configuration file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return {}


# By EM
def generate_ctf_id() -> str:
    return str(random.randint(100000000000000000, 999999999999999999))


class CTF(build.build.Build):
    @discord.ext.commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_view(self.CTFView())

    ctf_commands = discord.SlashCommandGroup("ctf", "CTF 指令")

    class CTFView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None

        @discord.ui.button(
            label="回報 Flag",
            style=discord.ButtonStyle.blurple,
            emoji="🚩",
            custom_id="new_ctf",
        )
        # user送出flag
        # pylint: disable-next = unused-argument
        async def button_callback_1(self, button, interaction) -> None:
            class SubmitModal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)
                    self.add_item(
                        discord.ui.InputText(
                            label="Flag", placeholder="Flag", required=True
                        )
                    )

                async def callback(self, interaction: discord.Interaction) -> None:
                    try:
                        connection, cursor = cog.core.sql.endlink_sql()  # SQL 會話
                        question_id = interaction.message.embeds[0].footer.text.split(
                            ": "
                        )[1]
                        # startTime
                        cursor.execute(
                            "SELECT start_time FROM ctf_data WHERE id=%s;",
                            (question_id,),
                        )
                        start_time = str(cursor.fetchone()[0])
                        # endTime
                        cursor.execute(
                            "SELECT end_time FROM ctf_data WHERE id=%s;", (question_id,)
                        )
                        end = str(cursor.fetchone()[0])  # 若沒有設定結束時間，則為 None
                        end = (
                            "None" if end == "NULL" else end
                        )  # 有些版本的 mysql-connector-python 會回傳NULL，統一轉成None
                        # 判斷是否在作答時間內
                        current_time = datetime.datetime.now()
                        if (
                            datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                            > current_time
                        ):
                            await interaction.response.send_message(
                                "答題時間尚未開始！", ephemeral=True
                            )
                            cog.core.sql.end(connection, cursor)
                            return
                        if (
                            end != "None"
                            and datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
                            < current_time
                        ):
                            await interaction.response.send_message(
                                "目前不在作答時間內！", ephemeral=True
                            )
                            cog.core.sql.end(connection, cursor)
                            return

                        user_id = interaction.user.id
                        nickname = interaction.user
                        # 判斷題目可作答次數
                        # pylint: disable-next = line-too-long
                        cursor.execute(
                            "SELECT count FROM ctf_history WHERE data_id=%s AND uid=%s;",
                            (question_id, user_id),
                        )
                        # return None or tuple.like (1,)
                        answer_count = cursor.fetchone()  # 使用者回答次數
                        # 第一次作答flag
                        # not_exist = False if answer_count is not None else True
                        not_exist = answer_count is None
                        if not_exist:
                            # 初始化作答次數
                            # pylint: disable-next = line-too-long
                            cursor.execute(
                                "INSERT INTO ctf_history (data_id,uid,count) VALUES (%s,%s,0);",
                                (question_id, user_id),
                            )
                            answer_count = 0
                        else:
                            answer_count = answer_count[0]
                        cursor.execute(
                            "SELECT restrictions FROM ctf_data WHERE id=%s;",
                            (question_id,),
                        )
                        restrictions = str(cursor.fetchone()[0])  # 最大作答次數

                        # 無限沒辦法比大小，不用判斷有沒有超過限制
                        if restrictions != "∞":
                            # 判斷使用者是否超過每人限制次數
                            if answer_count >= int(restrictions):
                                await interaction.response.send_message(
                                    "你已經回答超過限制次數了喔！", ephemeral=True
                                )
                                cog.core.sql.end(connection, cursor)
                                return

                        # 更新作答次數，包括總表和個人表
                        # pylint: disable-next = line-too-long
                        cursor.execute(
                            "UPDATE ctf_history SET count=count+1 WHERE data_id=%s AND uid=%s;",
                            (question_id, user_id),
                        )
                        answer_count += 1  # SQL和變數同步，變數之後還要用
                        cursor.execute(
                            "UPDATE ctf_data SET tried=tried+1 WHERE id=%s;",
                            (question_id,),
                        )

                        # 製造 embed 前置作業-取得必要數值
                        cursor.execute(
                            "SELECT tried FROM ctf_data WHERE id=%s;", (question_id,)
                        )
                        total_tried = int(cursor.fetchone()[0])  # 該題總共嘗試次數
                        # pylint: disable-next = line-too-long
                        cursor.execute(
                            "SELECT COUNT(*) FROM ctf_history WHERE data_id=%s AND solved=1;",
                            (question_id,),
                        )
                        total_solved = int(cursor.fetchone()[0])  # 該題完成人數

                        # 取得使用者輸入的 flag
                        response_flag = self.children[0].value
                        cursor.execute(
                            "SELECT flags,case_status FROM ctf_data WHERE id=%s;",
                            (question_id,),
                        )
                        answer, case = cursor.fetchall()[0]
                        # 輸入內容為正確答案
                        if response_flag == answer or (
                            case == 1 and response_flag.lower() == answer.lower()
                        ):
                            # 判斷是否重複回答
                            cursor.execute(
                                "SELECT solved FROM ctf_history WHERE data_id=%s AND uid=%s;",
                                (question_id, user_id),
                            )
                            is_solved = int(cursor.fetchone()[0])
                            if is_solved:
                                embed = discord.Embed(title="答題成功!")
                                embed.add_field(
                                    name="",
                                    value=f"但你已經解答過了所以沒有 {stickers['zap']}  喔！",
                                    inline=False,
                                )
                                await interaction.response.send_message(
                                    ephemeral=True, embeds=[embed]
                                )
                                return

                            # else 未曾回答過，送獎勵
                            # pylint: disable-next = line-too-long
                            cursor.execute(
                                "UPDATE ctf_history SET solved=1 WHERE data_id=%s AND uid=%s;",
                                (question_id, user_id),
                            )
                            # pylint: disable-next = line-too-long
                            cursor.execute(
                                "SELECT score FROM ctf_data WHERE id=%s;",
                                (question_id,),
                            )
                            reward = int(cursor.fetchone()[0])
                            # cursor.execute("USE Discord;") # 換資料庫存取電電點
                            current_point = cog.core.sql.read(user_id, "point", cursor)
                            new_point = current_point + reward
                            # 更新使用者電電點
                            cog.core.sql.write(user_id, "point", new_point, cursor)
                            # 更新作答狀態
                            # log
                            print(
                                f"{user_id}, {nickname} Get {reward} by ctf, {str(datetime.datetime.now())}"
                            )

                            embed = discord.Embed(title="答題成功!")
                            embed.add_field(
                                name="+" + str(reward) + f" {stickers['zap']} ",
                                value="=" + str(new_point),
                                inline=False,
                            )
                            await interaction.response.send_message(
                                embeds=[embed], ephemeral=True
                            )
                        else:
                            embed = discord.Embed(title="答案錯誤!")
                            embed.add_field(
                                name="嘗試次數",
                                value=str(answer_count) + "/" + str(restrictions),
                                inline=False,
                            )
                            await interaction.response.send_message(
                                embeds=[embed], ephemeral=True
                            )

                        # edit the original message
                        # 更新題目顯示狀態
                        embed = interaction.message.embeds[0]
                        embed.set_field_at(
                            0, name="已完成", value=str(total_solved), inline=True
                        )
                        embed.set_field_at(
                            1, name="已嘗試", value=str(total_tried), inline=True
                        )
                        embed.set_field_at(
                            2, name="回答次數限制", value=str(restrictions), inline=True
                        )
                        # set the new embed
                        await interaction.message.edit(embed=embed)
                    # pylint: disable-next = broad-exception-caught
                    except Exception as exception:
                        traceback_str = "".join(
                            traceback.format_exception(
                                type(exception), exception, exception.__traceback__
                            )
                        )
                        print(f"Error: {exception}\n{traceback_str}")
                    cog.core.sql.end(connection, cursor)  # 結束SQL會話

                def clear_items(self) -> typing.Self:
                    """
                    Clear all InputText from the modal.

                    This should be implemented by the parent class in Pycord.
                    However, we're now fixing it here as a workaround.
                    """

                    try:
                        self._children.clear()
                        self.__weights.clear()
                    except ValueError:
                        pass

                    return self

            await interaction.response.send_modal(
                SubmitModal(title="你找到 flag 了嗎？")
            )

    @ctf_commands.command(name="create", description="新題目")
    # 新增題目
    # pylint: disable-next = too-many-positional-arguments
    async def create(
        self,
        ctx,
        title: str = discord.commands.Option(str, "題目標題", required=True),
        flag: str = discord.commands.Option(str, "輸入 flag 解答", required=True),
        score: int = discord.commands.Option(int, "分數", required=True, default="20"),
        limit: int = discord.commands.Option(
            int, "限制回答次數", required=False, default="∞"
        ),
        case: bool = discord.commands.Option(
            bool, "大小寫忽略", required=False, default=False
        ),  # True:忽略大小寫
        # pylint: disable-next = line-too-long
        start: str = discord.commands.Option(
            str,
            f"開始作答日期 ({datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')})",
            required=False,
            default="",
        ),  # 時間格式
        # pylint: disable-next = line-too-long
        end: str = discord.commands.Option(
            str,
            f"截止作答日期 ({datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')})",
            required=False,
            default="",
        ),
    ) -> None:
        # SQL沒有布林值，所以要將T/F轉換成0或1
        case = 1 if case else 0
        # get ctf maker role's ID
        role_id = get_ctf_makers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]
        # Check whether the user can send a question or not
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        if role not in ctx.author.roles:
            await ctx.respond("你沒有權限建立題目喔！", ephemeral=True)
            return
        try:
            await ctx.defer()  # 確保機器人請求不會超時
            connection, cursor = cog.core.sql.link_sql()  # SQL 會話
            # cursor.execute("USE CTF;")
            while True:
                new_id = generate_ctf_id()
                # 找尋是否有重複的ID，若無則跳出迴圈
                cursor.execute(
                    "select id from ctf_data WHERE EXISTS(select id from ctf_data WHERE id=%s);",
                    (new_id,),
                )
                id_exist = cursor.fetchone()
                if id_exist is None:
                    break
            # 轉型成SQL datetime格式 '%Y-%m-%d %H:%M:%S'
            start = (
                datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                if start != ""
                else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            end = (
                f"{datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')}"
                if end != ""
                else "NULL"
            )
            # limit若沒有填寫，設為可嘗試無限次
            limit = "∞" if limit == "" else limit
            if limit == 0:
                await ctx.respond("限制回答次數不可為0！", ephemeral=True)
                return
            embed = discord.Embed(
                title=title,
                description="+" + str(score) + f"{stickers['zap']} ",
                color=0xFF24CF,
            )
            embed.set_author(
                name="SCAICT CTF",
                icon_url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png",
            )
            embed.set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png"
            )
            embed.add_field(name="已完成", value="0", inline=True)
            embed.add_field(name="已嘗試", value="0", inline=True)
            embed.add_field(name="回答次數限制", value=f"0/{limit}", inline=True)
            embed.add_field(name="開始作答日期", value=start, inline=True)
            embed.add_field(name="截止作答日期", value=end, inline=True)
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="可於下方討論，但請勿公布答案", value="", inline=False)
            embed.set_footer(text="題目 ID: " + new_id)
            # embed格式別亂改，會影響回應訊息時取值
            response = await ctx.send(embed=embed, view=self.CTFView())
            message_id = response.id

            # 先傳創建成功的訊息，再對資料庫進行操作，因為資料庫要存 response.id
            # 在CTF資料庫中的data資料表新增一筆CTF資料
            # print(f"INSERT INTO `ctf_data`\
            # (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) VALUES \
            # ({new_id},'{flag}',{score},'{limit}',{message_id},{case},'{start}','{end}',\'{title}\',{0});")
            if end == "NULL":
                cursor.execute(
                    "INSERT INTO `ctf_data` (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) \
                                VALUES (%s,%s,%s,%s,%s,%s,%s,NULL,%s,%s);",
                    (new_id, flag, score, limit, message_id, case, start, title, 0),
                )
            else:
                cursor.execute(
                    "INSERT INTO `ctf_data` (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) \
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
                    (
                        new_id,
                        flag,
                        score,
                        limit,
                        message_id,
                        case,
                        start,
                        end,
                        title,
                        0,
                    ),
                )
            await ctx.respond("已成功建立題目！", ephemeral=True)
            # CTFID,flag,score,可嘗試次數,message_id,大小寫限制,作答開始時間,作答結束時間,題目標題,已嘗試人數
        # pylint: disable-next = broad-exception-caught
        except Exception as exception:
            traceback_str = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )
            print(f"Error: {exception}\n{traceback_str}")

        cog.core.sql.end(connection, cursor)

    # 刪除題目
    @ctf_commands.command(name="delete", description="刪除題目")
    async def delete_ctf(
        self,
        ctx,
        qid: str = discord.Option(str, "欲刪除的題目", required=True),
        channel_id: str = discord.Option(str, "題目所在的貼文頻道", required=True),
        # 防呆
        key: str = discord.Option(str, "輸入該題題目解答", required=True),
    ) -> None:
        role_id = get_ctf_makers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        if role not in ctx.author.roles:
            await ctx.respond("你沒有權限刪除題目！", ephemeral=True)
            return
        try:
            connection, cursor = cog.core.sql.link_sql()
            cursor.execute(
                "SELECT message_id, title FROM ctf_data WHERE id=%s and flags=%s;",
                (
                    qid,
                    key,
                ),
            )
            # 取得題目的 embed 訊息 ID
            msg_id = cursor.fetchall()
            if len(msg_id) == 0:  # 返回空 list 代表沒有這個題目
                await ctx.respond(
                    "沒有這個題目喔，請檢查輸入的 qid 和 flag！", ephemeral=True
                )
                return
            title = msg_id[0][1]
            msg_id = msg_id[0][0]
            # 取得題目的貼文頻道
            # id 太長不能以 int 型態傳入，而 get_channel 只接受 int 型態
            channel = self.bot.get_channel(int(channel_id))
            message = await channel.fetch_message(msg_id)
            if message is None:
                await ctx.send("Message not found.")
                await ctx.respond(
                    "找不到題目訊息，請檢查欲刪除題目所在的討論串頻道是否和輸入的一致！",
                    ephemeral=True,
                )
                return
            cursor.execute("DELETE FROM ctf_data WHERE id=%s and flags=%s;", (qid, key))
            await message.delete()
            await ctx.respond(f"{ctx.author} 成功刪除題目 | **{title}**")
        except Exception as exception:
            await ctx.respond(
                f"出了一點小問題，請聯絡管理員\n{exception}", ephemeral=True
            )
            print(f"Error: {exception}")
            # 删除消息
        cog.core.sql.end(connection, cursor)

    @ctf_commands.command(name="list", description="列出所有題目")
    async def list_all(self, ctx) -> None:
        question_list = ["# **CTF 題目列表:**"]
        connection, cursor = cog.core.sql.link_sql()
        # cursor.execute("use CTF;")
        cursor.execute("SELECT title, score, id FROM ctf_data")
        ctf_info = cursor.fetchall()
        for title, score, qid in ctf_info:
            question_list.append(
                f"* **{title}** - {score} {stickers['zap']}  *({qid})*"
            )
        question_text = "\n".join(question_list)
        await ctx.respond(question_text)
        cog.core.sql.end(connection, cursor)


def setup(bot: discord.Bot):
    bot.add_cog(CTF(bot))
