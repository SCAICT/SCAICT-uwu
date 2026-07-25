# Future statements
from __future__ import annotations

# Third-party imports
import discord

# Local imports
import build.build


class ManagerCommand(build.build.Build):
    @discord.slash_command(name="reload", description="你是管理員才讓你用")
    async def reload(self, ctx, package) -> None:
        """
        Parameters:
            ctx:
            package:
        """

        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)

            return

        self.bot.reload_extension(f"cog.{package}")
        await ctx.respond(f"🔄 {package} reloaded")

    @discord.slash_command(name="announce", description="中電喵公告")
    async def announce(
        self,
        ctx,
        channel: discord.abc.GuildChannel = discord.Option(
            discord.abc.GuildChannel,
            "要發布到的頻道",
            # 一般文字頻道與公告頻道都可以選
            channel_types=[discord.ChannelType.text, discord.ChannelType.news],
        ),
        content: str = discord.Option(str, "公告內容，輸入 \\n 可換行"),
        ping: str = discord.Option(
            str,
            "要不要標註大家",
            choices=["不標註", "@here", "@everyone"],
            default="不標註",
        ),
    ) -> None:
        """
        Parameters:
            ctx:
            channel (discord.abc.GuildChannel):
            content (str):
            ping (str):
        """

        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("你沒有權限使用這個指令！", ephemeral=True)

            return

        # 斜線指令的輸入框不能換行，用 \n 代替
        text = content.replace("\\n", "\n")
        # 「# 」開頭的行會顯示成 Discord 的大字標題
        text = f"## 中電喵公告\n{text}"

        if ping in ("@here", "@everyone"):
            text = f"{ping}\n{text}"

        try:
            message = await channel.send(text)
        except discord.Forbidden:
            await ctx.respond(
                f"我沒有在 {channel.mention} 發言的權限！", ephemeral=True
            )

            return

        # 發到公告頻道時順便「發佈」，推送給有追蹤這個頻道的伺服器
        if channel.is_news():
            try:
                await message.publish()
            except discord.Forbidden:
                print(f"No permission to publish in #{channel.name}")

        # 純文字訊息看不出發布者，在 log 留下記錄
        print(f"{ctx.author.id}, {ctx.author} announce to #{channel.name}")
        await ctx.respond(f"公告已發布到 {channel.mention}！", ephemeral=True)


def setup(bot: discord.Bot) -> None:
    """
    Parameters:
        bot (discord.Bot):
    """

    bot.add_cog(ManagerCommand(bot))
