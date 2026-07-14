# Standard imports
import os

# Third-party imports
import discord
import dotenv

# Local imports
import channel_check  # update_channel程式從core目錄底下引入
import cog.daily_charge

intt = discord.Intents.default()
intt.members = True
intt.message_content = True
bot = discord.Bot(intents=intt)


for filename in os.listdir(f"{os.getcwd()}/cog"):
    if filename.endswith(".py"):
        bot.load_extension(f"cog.{filename[:-3]}")
        print(f"📖 {filename} loaded")  # test


@bot.command()
async def load(ctx, extension):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)
        return
    bot.load_extension(f"cog.{extension}")
    await ctx.send(f"📖 {extension} loaded")


@bot.command()
async def unload(ctx, extension):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)
        return
    bot.unload_extension(f"cog.{extension}")
    await ctx.send(f"📖 {extension} unloaded")


@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online")

    bot.loop.create_task(channel_check.update_channel(bot))
    bot.loop.create_task(channel_check.change_status(bot))
    bot.loop.create_task(cog.daily_charge.Charge(bot).restore_downtime_point())


if __name__ == "__main__":
    dotenv.load_dotenv(f"{os.getcwd()}/.env", verbose=True, override=True)
    bot_token = os.getenv("DISCORD_TOKEN")
    bot.run(bot_token)
