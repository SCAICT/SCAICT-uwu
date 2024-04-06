# Third-party imports
import discord
from discord.ext import commands
# Local imports
from cog.core.sql import read
from cog.core.sql import link_sql
from cog.core.sql import end

class CheckPoint(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = None

    async def send_message(self, point, combo, interaction):
        member = interaction.user.mention
        # mention the users

        self.embed = discord.Embed(color=0x14e15c)

        if interaction.user.avatar is not None: # 預設頭像沒有這個
            self.embed.set_thumbnail(url = str(interaction.user.avatar))
        self.embed.add_field(name = "\n", value = "使用者：" + member, inline = False)
        self.embed.add_field(name = "目前點數：" + str(point), value = '\n', inline = False)
        self.embed.add_field(name = "已連續充電：" + str(combo), value = '\n', inline = False)
        self.embed.add_field(
            name = "距離下次連續登入獎勵：" + str(combo + 7 - combo % 7),
            value = "\n",
            inline = False
        )
        await interaction.response.send_message(embed = self.embed)

    @discord.slash_command(name = "check_point", description = "查看電電點")
    async def check(self, interaction):
        connection, cursor = link_sql() # SQL 會話
        user_id = interaction.user.id
        combo = read(user_id, "charge_combo", cursor)
        point = read(user_id, "point", cursor)
        await self.send_message(point, combo, interaction)
        end(connection, cursor)

def setup(bot):
    bot.add_cog(CheckPoint(bot))
