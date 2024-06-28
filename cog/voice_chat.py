# Standard imports
import asyncio
# Third-party imports
import discord
from discord.ext import commands
# Local imports
from build.build import Build

# 建立動態語音頻道
class VoiceChat(Build):
    async def check_and_delete_empty_channel(self, voice_channel):
        while voice_channel.members:
            # 持續 loop 直到沒有人在頻道裡
            await asyncio.sleep(20)
        await voice_channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        target_voice_channel_name = "創建語音"
        target_category_name = "----------動態語音頻道----------"
        if (
            after.channel
            and after.channel != before.channel
            and after.channel.name == target_voice_channel_name
        ):
            guild = after.channel.guild
            category = discord.utils.get(guild.categories, name = target_category_name)

            new_channel = await guild.create_voice_channel(f"{member.name}的頻道", category = category)

            await member.move_to(new_channel)

            # await self.check_and_delete_empty_channel(new_channel)
            self.bot.loop.create_task(self.check_and_delete_empty_channel(new_channel))

def setup(bot):
    bot.add_cog(VoiceChat(bot))
