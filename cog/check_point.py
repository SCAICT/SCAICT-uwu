import discord
from discord.ext import commands
from  cog.core.SQL import read
from cog.core.SQL import linkSQL
from cog.core.SQL import end
class check_point(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    async def send_message(self, point, combo, interaction):
        
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
    async def check(self, interaction):
        CONNECTION,CURSOR=linkSQL()#SQL 會話
        userId = interaction.user.id
        combo = read(userId,'charge_combo',CURSOR)
        point = read(userId,'point',CURSOR)
        await self.send_message(point, combo, interaction)
        end(CONNECTION,CURSOR)
def setup(bot):
    bot.add_cog(check_point(bot))
