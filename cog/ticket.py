# Future statements
from __future__ import annotations

# Standard imports
import asyncio

# Third-party imports
import discord
import discord.ext.commands

# Local imports
import build.build


# ticket 頻道
class Ticket(build.build.Build):
    @discord.ext.commands.Cog.listener()
    async def on_ready(self) -> None:
        self.bot.add_view(self.TicketView())
        self.bot.add_view(self.CloseView())
        self.bot.add_view(self.DelView())

    ## del cahnnel button
    class DelView(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)  # timeout of the view must be set to Nones

        @discord.ui.button(
            label="刪除頻道", style=discord.ButtonStyle.red, emoji="🗑️", custom_id="del"
        )
        # pylint: disable-next = unused-argument
        async def button_callback(
            self, button, interaction: discord.Interaction
        ) -> None:
            """
            Parameters:
                button:
                interaction (discord.Interaction):
            """

            embed = discord.Embed(color=0xFF0000)
            embed.add_field(name="將於幾秒後刪除", value=" ", inline=False)
            await interaction.response.send_message(embed=embed)
            await asyncio.sleep(3)

            try:
                await interaction.channel.delete()
            except discord.Forbidden:
                await interaction.followup.send("我沒有權限刪除頻道！")

    ## close button
    class CloseView(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)  # timeout of the view must be set to Nones

        @discord.ui.button(
            label="關閉表單",
            style=discord.ButtonStyle.red,
            emoji="🔒",
            custom_id="close",
        )
        # pylint: disable-next = unused-argument
        async def button_callback(
            self, button, interaction: discord.Interaction
        ) -> None:
            """
            Parameters:
                button:
                interaction (discord.Interaction):
            """

            channel = interaction.channel

            # 收回頻道中所有成員（即開單者）的檢視權限，
            # 而不是按下按鈕的人，避免管理員代關時把自己鎖在外面
            try:
                for target in list(channel.overwrites):
                    if isinstance(target, discord.Member) and not target.bot:
                        await channel.set_permissions(target, read_messages=False)
            except discord.Forbidden:
                await interaction.response.send_message(
                    "我沒有權限關閉這個頻道，請檢查機器人的身分組權限！",
                    ephemeral=True,
                )

                return

            embed = discord.Embed(color=0xFF0A0A)
            embed.add_field(name="已成功關閉頻道", value=" ", inline=False)
            await channel.send(embed=embed)

            # 通知管理員確認並刪除頻道；找不到 root 身分組時不 tag，
            # 避免整個互動失敗
            role = discord.utils.get(interaction.guild.roles, name="root")
            embed = discord.Embed(color=0xFFF700)
            embed.add_field(name="請確認並刪除頻道", value=" ", inline=False)
            await interaction.response.send_message(
                role.mention if role else None, embed=embed, view=Ticket.DelView()
            )

    ## create ticket button
    class TicketView(discord.ui.View):
        def __init__(self) -> None:
            super().__init__(timeout=None)  # timeout of the view must be set to None

        @discord.ui.button(
            label="點擊開單",
            style=discord.ButtonStyle.blurple,
            emoji="📩",
            custom_id="ticket",
        )
        # pylint: disable-next = unused-argument
        async def button_callback(
            self, button, interaction: discord.Interaction
        ) -> None:
            """
            Parameters:
                button:
                interaction (discord.Interaction):
            """

            await self.create_ticket_channel(interaction, "開單")

        # pylint: disable-next = unused-argument
        async def create_ticket_channel(
            self, interaction: discord.Interaction, button_name
        ) -> None:
            """
            Parameters:
                interaction (discord.Interaction):
                button_name:
            """

            user = interaction.user
            guild = interaction.guild
            target_category_name = "開單處"

            existing_channels = [
                channel
                for channel in guild.text_channels
                if channel.name.startswith(interaction.user.name)
            ]

            if existing_channels:
                await interaction.response.send_message(
                    "你已經有建立頻道了！", ephemeral=True
                )

                return

            # 建立頻道名稱
            channel_name = f"{interaction.user.name}的ticket頻道"

            # 取得或建立目標類別
            category = discord.utils.get(guild.categories, name=target_category_name)

            if category is None:
                category = await guild.create_category(target_category_name)

            # 建立頻道
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True),
            }

            channel = await category.create_text_channel(
                name=channel_name, overwrites=overwrites
            )

            # 向頻道傳送歡迎訊息
            embed = discord.Embed(color=0x4AF750)
            embed.add_field(name="請闡述你的問題 並等待回覆！", value="", inline=False)
            embed.add_field(
                name="若需關閉客服單 可以點擊下方按鈕 🔒 關閉", value="", inline=False
            )
            await channel.send(
                f"這裡是{user.mention}的頻道", embed=embed, view=Ticket.CloseView()
            )  # 修改這裡，使用 Ticket.CloseView()

            await interaction.response.send_message(
                f"已建立 {channel.mention}！", ephemeral=True
            )

    @discord.slash_command()
    async def create_ticket_button(self, ctx) -> None:
        """
        Parameters:
            ctx:
        """

        if ctx.author.guild_permissions.administrator:
            # 修改這裡，使用 Ticket.TicketView()
            embed = discord.Embed(title=" ", color=0xFEFCB6)
            embed.set_thumbnail(
                url="https://cdn-icons-png.flaticon.com/512/2067/2067179.png"
            )
            embed.add_field(name="SCAICT-Discord", value=" ", inline=False)
            embed.add_field(name="客服單", value="", inline=False)
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(
                name="----- 什麼時候可以按這個酷酷的按鈕？ -----",
                value="  ",
                inline=False,
            )
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(
                name="各種伺服器內疑難雜症：包括但不限於 不當言行檢舉、領獎、活動轉發、贊助",
                value="",
                inline=False,
            )
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(
                name="課程問題：當你對中電會課程的報名、上課通知有疑慮時可以點我詢問",
                value="",
                inline=False,
            )
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(
                name="----------------- 注意事項 --------------------",
                value=" ",
                inline=False,
            )
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(
                name="請不要隨意開啟客服單，若屢勸不聽將會扣電電點，嚴重者會踢出伺服器",
                value="",
                inline=False,
            )
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(name=" ", value=" ", inline=False)
            embed.set_footer(text="所有客服單將自動留存，以保障雙方權益。")
            await ctx.respond(embed=embed, view=Ticket.TicketView())


def setup(bot: discord.Bot) -> None:
    """
    Parameters:
        bot (discord.Bot):
    """

    bot.add_cog(Ticket(bot))
