import asyncio
import json
import os
def openJSON():
    #open setting file
    os.chdir("./")
    with open(f"{os.getcwd()}/DataBase/server.config.json","r") as file:
        GlobalSetting= json.load(file)
    return GlobalSetting

async def update_channel(bot):
        channel=openJSON()["SCAICT-alpha"]["channel"]
        await bot.wait_until_ready() 
        guild = bot.get_guild(channel["serverID"])  #YOUR_GUILD_ID

        if guild is None:
            print("找不到指定的伺服器")
            return

        channel = guild.get_channel(channel["memberCount"])  #YOUR_CHANNEL_ID

        if channel is None:
            print("找不到指定的頻道")
            return

        while not bot.is_closed():
            total_members = guild.member_count
            await channel.edit(name=f"👥電池數：{total_members}")
            await asyncio.sleep(600)
