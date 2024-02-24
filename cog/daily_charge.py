import discord
from discord.ext import commands
import user
from datetime import datetime
import csv


class charge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send_message(self, point, combo, interaction):
        self.embed = discord.Embed(color=0x14e15c)
        self.embed.set_thumbnail(url=str(interaction.user.avatar))
        self.embed.add_field(name=":battery: 充電成功!",
                             value="+5:zap: = "+str(point)+":zap:", inline=False)
        self.embed.add_field(name="連續登入獎勵: "+str(combo)+"/" +
                             str(combo + 7- combo % 7), value='\n', inline=False)
        await interaction.response.send_message(embed=self.embed)
        
    async def already_charge(self, interaction):
        self.embed = discord.Embed(color=0xff0000)
        self.embed.set_thumbnail(url=str(interaction.user.avatar))
        self.embed.add_field(name="您夠電了，明天再來!", value="⚡⚡⚡🛐🛐🛐", inline=False)
        await interaction.response.send_message(embed=self.embed)
    @discord.slash_command(name="charge", description="每日充電")
    
    async def charge(self, interaction: discord.Interaction):
        userId = interaction.user.id
        last_charge = user.read(userId, 'last_charge')
        last_charge = datetime.strptime(last_charge, '%Y-%m-%d')
        combo = user.read(userId, 'charge_combo')
        point = user.read(userId, 'point')
        now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # get now time
        if (now == last_charge):
            last_charge = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
            await self.already_charge(interaction)
        else:
            combo = 1 if (now - last_charge).days > 1 else combo + 1
            point += 5
            last_charge = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
            await self.send_message(point, combo, interaction)
            with open('./database/point_log.csv', 'a+', newline='') as log:
                writer = csv.writer(log)
                writer.writerow([str(interaction.user.id), str(interaction.user.name), '5', str(
                    user.read(userId, 'point')), 'charge', str(datetime.now())])
            
        user.write(userId, 'last_charge', last_charge)
        user.write(userId, 'charge_combo', combo)
        user.write(userId, 'point', point)


def setup(bot):
    bot.add_cog(charge(bot))
