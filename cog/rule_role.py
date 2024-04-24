# Third-party imports
import discord
from discord.ext import commands
# Local imports
from build.build import Build

class RuleRoles(Build):

    # 當使用者按下表情符號 -> 領取身分組
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # 取得反應的資訊
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = payload.emoji.name

        # 檢查是否為指定的訊息和 emoji
        if payload.message_id == 1208097539820232734 and emoji == "⚡":
            # 給予身分組
            role = discord.utils.get(guild.roles, name = "二月主題課程")
            await member.add_roles(role)

    # 當使用者收回表情符號 -> 取消身分組
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # 取得反應的資訊
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        emoji = payload.emoji.name

        # 檢查是否為指定的 emoji
        if payload.message_id == 1208097539820232734 and emoji == "⚡":
            # 移除身分組
            role = discord.utils.get(guild.roles, name = "二月主題課程")
            await member.remove_roles(role)

def setup(bot):
    bot.add_cog(RuleRoles(bot))
