import discord
from discord.ext import commands
from datetime import datetime
import user

class check_point(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    async def send_message(self, point, combo, next_lottery, interaction):
        
        member=interaction.user.mention
        #mention the users

        self.embed = discord.Embed(color=0x14e15c)
        
        self.embed.set_thumbnail(url=str(interaction.user.avatar))
        self.embed.add_field(name="\n", value='用戶 : '+member, inline=False)
        self.embed.add_field(name="目前點數 : "+str(point), value='\n', inline=False)
        self.embed.add_field(name="已連續充電 : "+str(combo), value='\n', inline=False)
        self.embed.add_field(name="距離下次連續登入獎勵 : "+str(combo + 7-combo % 7), value='\n', inline=False)
        await interaction.response.send_message(embed=self.embed)

    @discord.slash_command(name="check_point", description="查看電電點")
    async def check(self, interaction: discord.Interaction):
        member=interaction.user.mention
        userId = interaction.user.id
        last_charge = user.read(userId,'last_charge')
        last_charge = datetime.strptime(last_charge, '%Y-%m-%d')
        combo = user.read(userId,'charge_combo')
        point = user.read(userId,'point')

        await self.send_message(point, combo, next_lottery, interaction)

def setup(bot):
    bot.add_cog(check_point(bot))
