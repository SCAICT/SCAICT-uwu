import discord
from discord.ext import commands
import user
from datetime import datetime
from datetime import timedelta
import csv

class daily_charge(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    async def send_message(self, point, combo, next_lottery, interaction):
        
        member=interaction.user.mention

        self.embed = discord.Embed(color=0x14e15c)
        
        self.embed.set_thumbnail(url=str(interaction.user.avatar))
        self.embed.add_field(name="Charge Successfully!", value="成功充電!", inline=False)
        self.embed.add_field(name="\n", value='\n', inline=False)
        self.embed.add_field(name="\n", value='用戶 : '+member, inline=False)
        self.embed.add_field(name="目前點數 : "+str(point), value='\n', inline=False)
        self.embed.add_field(name="已連續充電 : "+str(combo), value='\n', inline=False)
        self.embed.add_field(name="距離下次連續登入獎勵 : "+str(next_lottery), value='\n', inline=False)
        await interaction.response.send_message(embed=self.embed)


    async def already_charge(self, interaction):
        
        member=interaction.user.mention

        self.embed = discord.Embed(color=0xff0000)
        
        self.embed.set_thumbnail(url=str(interaction.user.avatar))
        self.embed.add_field(name="\n", value=member, inline=False)
        self.embed.add_field(name="You've already charged today!", value="您夠電了，明天再來!", inline=False)
        self.embed.add_field(name="⚡⚡⚡🛐🛐🛐", value="\n", inline=False)
        await interaction.response.send_message(embed=self.embed)


    @discord.slash_command(name="daily_charge", description="每日充電")
    async def charge(self, interaction: discord.Interaction):
        userId = interaction.user.id
        last_charge = user.read(userId,'last_charge')
        last_charge = datetime.strptime(last_charge, '%Y-%m-%d')
        combo = user.read(userId,'charge_combo')
        point = user.read(userId,'point')
        next_lottery = user.read(userId,'next_lottery')
        now=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        #get now time
        delta = timedelta(days=1)
        #set combo time limit
        if(now-last_charge == delta):
            combo += 1
            point += 5
            last_charge = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
            next_lottery -= 1
            await self.send_message(point, combo, next_lottery, interaction)
            if(next_lottery == 0):
                next_lottery = 7
            with open('./point_log.csv', 'a+', newline='') as log:
                writer = csv.writer(log)
                writer.writerow([str(interaction.user.id), str(interaction.user.name), '5', str(user.read(userId,'point')), 'daily_charge', str(datetime.now())])
        
        elif(now == last_charge):
            last_charge = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
            await self.already_charge(interaction)

        else:
            combo = 1
            point += 5
            last_charge = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
            next_lottery = 6
            await self.send_message(point, combo, next_lottery, interaction)

            with open('./point_log.csv', 'a+', newline='') as log:
                writer = csv.writer(log)
                writer.writerow([str(interaction.user.id), str(interaction.user.name), '5', str(user.read(userId,'point')), 'daily_charge', str(datetime.now())])

        user.write(userId,'last_charge',last_charge)
        user.write(userId,'charge_combo',combo)
        user.write(userId,'point',point)
        user.write(userId,'next_lottery',next_lottery)

def setup(bot):
    bot.add_cog(daily_charge(bot))