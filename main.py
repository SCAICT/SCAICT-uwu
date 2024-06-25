# Standard imports
import json
import os
# Third-party imports
import discord
# Local imports
from channel_check import update_channel # update_channel程式從core目錄底下引入
from channel_check import changeStatus # update_channel程式從core目錄底下引入

bot = discord.Bot(intents = discord.Intents.all())
# 變更目前位置到專案根目錄（SCAICT-DISCORD-BOT 資料夾），再找檔案
os.chdir("./")
with open(f"{os.getcwd()}/token.json","r", encoding = "utf-8") as file:
    token = json.load(file)

for filename in os.listdir(f"{os.getcwd()}/cog"):
    if filename.endswith(".py"):
        bot.load_extension(f"cog.{filename[:-3]}")
        print(f"📖 {filename} loaded")#test

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online")

    bot.loop.create_task(update_channel(bot))
    bot.loop.create_task(changeStatus(bot))

if __name__=="__main__":
    bot.run(token["discord_token"])
