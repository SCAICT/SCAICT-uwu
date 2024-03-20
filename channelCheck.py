import asyncio
import json
import os
from cog.core.SQL import linkSQL
from cog.core.SQL import end
def openJSON():
    #open setting file
    os.chdir("./")
    with open(f"{os.getcwd()}/DataBase/server.config.json","r") as file:
        GlobalSetting= json.load(file)
    return GlobalSetting
def totalPoint():
    connection,cursor=linkSQL()
    cursor.execute(f'SELECT SUM(point) FROM `USER`')
    points = cursor.fetchone()[0]
    end(connection,cursor)
    return points
async def update_channel(bot):
        channel=openJSON()["SCAICT-alpha"]["channel"]
        await bot.wait_until_ready() 
        guild = bot.get_guild(channel["serverID"])  #YOUR_GUILD_ID

        if guild is None:
            print("找不到指定的伺服器")
            return

        memberChannel = guild.get_channel(channel["memberCount"])  #YOUR_CHANNEL_ID
        pointChannel=guild.get_channel(channel["pointCount"])
        if channel is None:
            print("找不到指定的頻道")
            return

        while not bot.is_closed():
            points=totalPoint()
            total_members = guild.member_count
            await memberChannel.edit(name=f"👥電池數：{total_members}")
            await pointChannel.edit(name=f"🔋總電量：{points}")
            await asyncio.sleep(600)
