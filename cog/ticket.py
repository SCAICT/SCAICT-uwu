# Standard imports
import asyncio

# Third-party imports
import discord
from discord.ext import commands

# Local imports
from build.build import Build


# ticket 頻道
class Ticket(Build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.TicketView())
        self.bot.add_view(self.CloseView())
        self.bot.add_view(self.DelView())

    ## del cahnnel button
    class DelView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to Nones

        @discord.ui.button(
            label="刪除頻道", style=discord.ButtonStyle.red, emoji="🗑️", custom_id="del"
        )
        # pylint: disable-next = unused-argument
        async def button_callback(self, button, interaction):
            embed = discord.Embed(color=0xFF0000)
            embed.add_field(name="將於幾秒後刪除", value=" ", inline=False)
            await interaction.response.send_message(embed=embed)
            await asyncio.sleep(3)
            await interaction.channel.delete()

    ## close button
    class CloseView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to Nones

        @discord.ui.button(
            label="關閉表單",
            style=discord.ButtonStyle.red,
            emoji="🔒",
            custom_id="close",
        )
        # pylint: disable-next = unused-argument
        async def button_callback(self, button, interaction):
            user = interaction.user
            channel = interaction.channel

            # 這裡可以加入你的權限處理邏輯
            # 這裡是一個範例：將使用者的檢視權限設定為 False
            embed = discord.Embed(color=0xFF0A0A)
            embed.add_field(name="已成功關閉頻道", value=" ", inline=False)
            await channel.send(embed=embed)
            await channel.set_permissions(user, read_messages=False)

            # 回覆使用者，表示已完成操作

            role = discord.utils.get(interaction.guild.roles, name="root")
            embed = discord.Embed(color=0xFFF700)
            embed.add_field(name="請確認並刪除頻道", value=" ", inline=False)
            await interaction.response.send_message(
                role.mention, embed=embed, view=Ticket.DelView()
            )  # 修改這裡，使用 Ticket.DelView()

    ## create ticket button
    class TicketView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None

        @discord.ui.button(
            label="點擊開單",
            style=discord.ButtonStyle.blurple,
            emoji="📩",
            custom_id="ticket",
        )
        # pylint: disable-next = unused-argument
        async def button_callback(self, button, interaction):
            await self.create_ticket_channel(interaction, "開單")

        # pylint: disable-next = unused-argument
        async def create_ticket_channel(self, interaction, button_name):
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
    async def create_ticket_button(self, ctx):
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


def setup(bot):
    bot.add_cog(Ticket(bot))
