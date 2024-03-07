import discord
import json
import os
from channelCheck import update_channel#update_channel程式從core目錄底下引入

bot = discord.Bot(intents = discord.Intents.all())
with open("token.json","r") as file:
    token = json.load(file)

for filename in os.listdir("./cog"):
    if filename.endswith(".py"):
        bot.load_extension(f"cog.{filename[:-3]}")
        print(f"📖 {filename} loaded")#test

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online")
    await bot.change_presence(activity=discord.Game(name="SITCON"))
    bot.loop.create_task(update_channel(bot))

if __name__=="__main__":
    bot.run(token["token"])