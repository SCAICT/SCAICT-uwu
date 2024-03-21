import discord
import json
import os
from channelCheck import update_channel#update_channel程式從core目錄底下引入
bot = discord.Bot(intents = discord.Intents.all())
#更改目前位置到專案根目錄(SCAICT-DISCORD-BOT 資料夾)，再找檔案
os.chdir("./")
with open(f"{os.getcwd()}/token.json","r") as file:
    token = json.load(file)

for filename in os.listdir(f"{os.getcwd()}/cog"):
    if filename.endswith(".py"):
        bot.load_extension(f"cog.{filename[:-3]}")
        print(f"📖 {filename} loaded")#test

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="深度學習"))
    bot.loop.create_task(update_channel(bot))

if __name__=="__main__":
    bot.run(token["token"])