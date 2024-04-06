import discord
import asyncio
from build.build import build
from discord.ext import commands

#創建動態語音頻道

class VoiceChat(build):

    @commands.Cog.listener()
    async def on_voice_state_update(self,member, before, after):
        target_voice_channel_name =  "創建語音"
        target_category_name = "----------動態語音頻道----------"
        if (
            after.channel
            and after.channel != before.channel
            and after.channel.name == target_voice_channel_name
        ):
            guild = after.channel.guild
            category = discord.utils.get(guild.categories, name=target_category_name)

            new_channel = await guild.create_voice_channel(f'{member.name}的頻道', category=category)

            await member.move_to(new_channel)

            await self.check_and_delete_empty_channel(new_channel)

    async def check_and_delete_empty_channel(self,voice_channel):
            await asyncio.sleep(20)

            members = voice_channel.members

            if not members:
                await voice_channel.delete()

def setup(bot):
    bot.add_cog(VoiceChat(bot))
