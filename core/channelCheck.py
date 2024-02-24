import asyncio
import discord

async def update_channel(bot):
        await bot.wait_until_ready() 
        guild = bot.get_guild(1203338928535379978)  #YOUR_GUILD_ID

        if guild is None:
            print("找不到指定的伺服器")
            return

        channel = guild.get_channel(1210619287044096040)  #YOUR_CHANNEL_ID

        if channel is None:
            print("找不到指定的頻道")
            return

        while not bot.is_closed():
            total_members = guild.member_count
            await channel.edit(name=f"電子數{total_members}")
            await asyncio.sleep(600)