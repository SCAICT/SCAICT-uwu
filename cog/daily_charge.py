# Standard imports
# import csv
from datetime import datetime, timedelta
import json
import os

# Third-party imports
import discord
from discord.ext import commands

# Local imports
from cog.core.sql import write
from cog.core.sql import read
from cog.core.sql import link_sql
from cog.core.sql import end

def get_channels(): # 取得特殊用途頻道的清單，這裡會用來判斷是否在簽到頻道簽到，否則不予受理
    with open(f"{os.getcwd()}/DataBase/server.config.json", "r", encoding = "utf-8") as file:
        return json.load(file)["SCAICT-alpha"]["channel"]

class Charge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = None

    async def send_message(self, point, combo, interaction):
        # 讀表符ID
        with open(f"{os.getcwd()}/DataBase/server.config.json", "r", encoding = "utf-8") as file:
            stickers = json.load(file)["SCAICT-alpha"]["stickers"]

        self.embed = discord.Embed(
            title = f"{interaction.user.name}剛剛充電了！",
            description = "",
            color = 0x14e15c
        )

        if interaction.user.avatar is not None: # 預設頭像沒有這個
            self.embed.set_thumbnail(url = str(interaction.user.avatar))

        self.embed.add_field(
            name = "",
            value = f":battery:+5{stickers['zap']}= " + str(point) + f"{stickers['zap']}",
            inline = False
        )
        self.embed.add_field(
            name = "連續登入獎勵: " + str(combo) + "/" + str(combo + 7 - combo % 7),
            value = "\n",
            inline = False
        )
        self.embed.set_footer(text = f"{interaction.user.name}充電成功！")
        await interaction.response.send_message(embed = self.embed)

    async def already_charge(self, interaction):
        self.embed = discord.Embed(color = 0xff0000)
        if interaction.user.avatar is not None: # 預設頭像沒有這個
            self.embed.set_thumbnail(url = str(interaction.user.avatar))
        self.embed.add_field(name = "您夠電了，明天再來!", value = "⚡⚡⚡🛐🛐🛐", inline = False)
        await interaction.response.send_message(embed = self.embed, ephemeral = True)

    async def channel_error(self, interaction):
        self.embed = discord.Embed(color = 0xff0000)
        self.embed.set_thumbnail(url = "https://http.cat/images/404.jpg")
        self.embed.add_field(name = "這裡似乎沒有打雷…", value = "  ⛱️", inline = False)
        self.embed.add_field(name = "到「每日充電」頻道試試吧！", value = "", inline = False)
        # 其他文案：這裡似乎離無線充電座太遠了，到「每日充電」頻道試試吧！ 待商議
        await interaction.response.send_message(embed = self.embed, ephemeral = True)

    @discord.slash_command(name = "charge", description = "每日充電")
    async def charge(self, interaction):
        user_id = interaction.user.id
        connection, cursor = link_sql() # SQL 會話
        last_charge = read(user_id, 'last_charge', cursor) # SQL回傳型態：<class 'datetime.date'>
        # strptime轉型後：<class 'datetime.datetime'>
        last_charge = datetime.strptime(str(last_charge), '%Y-%m-%d %H:%M:%S')
        # get now time and combo
        now = datetime.now().replace(microsecond = 0)
        combo = read(user_id, 'charge_combo', cursor) # 連續登入
        point = read(user_id, 'point', cursor)
        if interaction.channel.id != get_channels()["everyDayCharge"]:
            await self.channel_error(interaction)
            # End connection instead of return
            # return
        if now.date() == last_charge.date(): # 今天已經充電過了
            await self.already_charge(interaction)
            # End connection instead of return
            # return
        else:
            combo = 1 if now.date() - last_charge.date() > timedelta(days=1) else combo + 1
            point += 5
            if combo % 7 == 0:
                ticket = read(user_id, 'ticket', cursor)
                write(user_id, 'ticket', ticket + 4, cursor)
            write(user_id, 'last_charge', now, cursor)
            write(user_id, 'charge_combo', combo, cursor)
            write(user_id, 'point', point, cursor)
            await self.send_message(point, combo, interaction)

            # 紀錄log
            # pylint: disable-next = line-too-long
            print(f"{interaction.user.id},{interaction.user} Get 5 point by daily_charge {datetime.now()}")
        end(connection, cursor)

def setup(bot):
    bot.add_cog(Charge(bot))
