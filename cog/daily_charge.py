# Standard imports
# import csv
from datetime import datetime, timedelta
import json
import os
from typing import cast

# Third-party imports
import discord
from discord.ext import commands

# Local imports
from cog.core.downtime import get_downtime_list, write_downtime_list, get_history
from cog.core.sql import write, read, mysql_connection
from cog.core.sql_abstract import UserRecord


def get_channels():  # 取得特殊用途頻道的清單，這裡會用來判斷是否在簽到頻道簽到，否則不予受理
    with open(
        f"{os.getcwd()}/DataBase/server.config.json", "r", encoding="utf-8"
    ) as file:
        return json.load(file)["SCAICT-alpha"]["channel"]


class Charge(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    async def restore_downtime_point(self):
        downtime_list = get_downtime_list()
        unprocessed_downtime_list = list(
            filter(lambda x: not x.is_restored, downtime_list)
        )

        if not unprocessed_downtime_list:
            return

        earliest_downtime_start = min(
            unprocessed_downtime_list, key=lambda downtime: downtime.start
        ).start
        # TODO: now() or end but with some condition
        latest_downtime_end = datetime.now()

        charge_channel_id = get_channels()["everyDayCharge"]
        messages = await get_history(
            self.bot,
            charge_channel_id,
            after=earliest_downtime_start,
            before=latest_downtime_end,
        )

        # TODO: cache the last_charged date
        # cached_change: UserDict = UserDict()
        with mysql_connection() as cursor:
            # XXX: check with a better method, because the module on the running machine have no `_connection` attribute :skull:
            # assert (
            #     cursor._connection.autocommit is False
            # ), "Unsafe operation at restoring downtime point due to commit automatically."

            for message in messages:
                created_time: datetime = message.created_at
                author = message.author

                assert self.bot.user, "Bot was not logged in."
                if author.id == self.bot.user.id:
                    continue

                last_charge = self.get_last_charged(author, cursor)
                already_charged = created_time.date() == last_charge.date()
                if already_charged:
                    continue

                if any(
                    message.created_at in downtime
                    for downtime in unprocessed_downtime_list
                ):
                    user_data = UserRecord.from_sql(author.id) or UserRecord.default(
                        author.id
                    )

                    delta_record = self.reward(
                        author,
                        last_charge,
                        created_time,
                        cursor,
                        user_data.charge_combo,
                        user_data.point,
                        is_forgivable=True,
                    )

                    # TODO: send the message together, or there may have problem about send but not modify
                    embed = self.embed_successful(
                        delta_record.point, delta_record.charge_combo, author
                    )
                    await message.reply(embed=embed, silent=True)
            # end loop
            # modify all "is_restored" of each data from datelist
            restored_downtime_list = [
                downtime.marked_as_restored() for downtime in downtime_list
            ]
            write_downtime_list(restored_downtime_list)

        # commit and close the connection

    def embed_channel_error(self):
        embed = discord.Embed(color=0xFF0000)
        embed.set_thumbnail(url="https://http.cat/images/404.jpg")
        embed.add_field(name="這裡似乎沒有打雷…", value="  ⛱️", inline=False)
        embed.add_field(name="到「每日充電」頻道試試吧！", value="", inline=False)

        return embed

    def embed_already_charged(self, user: discord.User | discord.Member):
        embed = discord.Embed(color=0xFF0000)
        if user.avatar is not None:  # 預設頭像沒有這個
            embed.set_thumbnail(url=str(user.avatar))
            embed.add_field(
                name="您夠電了，明天再來!", value="⚡⚡⚡🛐🛐🛐", inline=False
            )
        return embed

    def embed_successful(self, point, combo, user: discord.User | discord.Member):
        # 讀表符ID
        with open(
            f"{os.getcwd()}/DataBase/server.config.json", "r", encoding="utf-8"
        ) as file:
            stickers = json.load(file)["SCAICT-alpha"]["stickers"]

        embed = discord.Embed(
            title=f"{user.name}剛剛充電了！",
            description="",
            color=0x14E15C,
        )

        if user.avatar is not None:  # 預設頭像沒有這個
            embed.set_thumbnail(url=str(user.avatar))

        embed.add_field(
            name="",
            value=f":battery:+5{stickers['zap']}= " + str(point) + f"{stickers['zap']}",
            inline=False,
        )
        embed.add_field(
            name="連續登入獎勵: " + str(combo) + "/" + str(combo + 7 - combo % 7),
            value="\n",
            inline=False,
        )
        embed.set_footer(text=f"{user.name}充電成功！")

        return embed

    def is_forgivable(self, user: discord.User | discord.Member) -> bool:
        # TODO: implement by add a table column called `is_forgivable` to control
        """Return if user cannot charge due to downtime

        For example, if downtime is from 2025-03-14 09:03:00 to 2025-04-11 21:00:00,
        return True for all users who have charged between 2025-03-13(yesterday) to 2025-03-14(downtime.start),
        if is_forgivable is True, you won't loss combo.
        but after next charge, is_forgivable will be False,
        because user will execute not at downtime, if downtime is correct
        """
        user_data = UserRecord.from_sql(user.id)

        if user_data is None:
            return False

        last_charge = user_data.last_charge
        downtime_list = get_downtime_list()

        return any(
            downtime.start.date() - timedelta(days=1)
            <= last_charge.date()
            <= downtime.start.date()
            for downtime in downtime_list
        )

    # TODO: inherit a MySQLCursorAbstract to add method about these or consider to add self.cursor
    def reward(
        self,
        user: discord.User | discord.Member,
        last_charge: datetime,
        executed_at: datetime,
        cursor,
        orig_combo: int,
        orig_point: int,
        is_forgivable: bool = False,
    ) -> UserRecord:
        delta_record = UserRecord(user.id)

        combo = (
            1
            if is_forgivable
            or (executed_at.date() - last_charge.date() > timedelta(days=1))
            else orig_combo + 1
        )
        point = orig_point + 5
        if combo % 7 == 0:
            ticket = read(user.id, "ticket", cursor)
            # refactor with UserRecord.to_sql
            write(user.id, "ticket", ticket + 4, cursor)
            delta_record.ticket = ticket + 4
        write(user.id, "last_charge", executed_at, cursor)
        write(user.id, "charge_combo", combo, cursor)
        write(user.id, "point", point, cursor)

        delta_record.last_charge = executed_at
        delta_record.charge_combo = combo
        delta_record.point = point

        # 紀錄log
        # TODO: record both executed time and datetime.now() after logger is implemented
        # pylint: disable-next = line-too-long
        print(f"{user.id},{user} Get 5 point by daily_charge {datetime.now()}")

        return delta_record

    # TODO: inherit a MySQLCursorAbstract to add method about these or consider to add self.cursor
    def get_last_charged(self, user: discord.User | discord.Member, cursor):
        last_charge = read(
            user.id, "last_charge", cursor
        )  # SQL回傳型態：<class 'datetime.date'>
        # strptime轉型後：<class 'datetime.datetime'>
        last_charge = datetime.strptime(str(last_charge), "%Y-%m-%d %H:%M:%S")

        return last_charge

    @discord.slash_command(name="charge", description="每日充電")
    async def charge(self, interaction):
        interaction = cast(discord.Interaction, interaction)

        assert (
            interaction.user
        ), "Interaction may be in PING interactions, so that interaction.user is invalid."
        assert interaction.channel, "There are no channel returned from interation."

        # TODO: Use UserRecord or its extension to manage user data uniformly
        if interaction.channel.id != get_channels()["everyDayCharge"]:
            embed = self.embed_channel_error()
            # 其他文案：這裡似乎離無線充電座太遠了，到「每日充電」頻道試試吧！ 待商議
            await interaction.response.send_message(embed=embed, ephemeral=True)
            # End connection instead of return
            return

        with mysql_connection() as cursor:  # SQL 會話
            user = interaction.user

            # get now time and combo
            now = datetime.now().replace(microsecond=0)

            last_charge = self.get_last_charged(user, cursor)
            already_charged = now.date() == last_charge.date()

            if already_charged:
                embed = self.embed_already_charged(user)
                await interaction.response.send_message(embed=embed, ephemeral=True)

                return

            combo: int = read(
                user.id, "charge_combo", cursor
            )  # 連續登入 # pyright: ignore[reportAssignmentType]
            point: int = read(
                user.id, "point", cursor
            )  # pyright: ignore[reportAssignmentType]

            is_forgivable = self.is_forgivable(user)

            self.reward(user, last_charge, now, cursor, combo, point, is_forgivable)

            embed = self.embed_successful(point, combo, user)
            await interaction.response.send_message(embed=embed)


async def setup(bot: discord.Bot):
    bot.add_cog(Charge(bot))
