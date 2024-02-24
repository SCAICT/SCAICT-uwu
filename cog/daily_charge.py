import discord
from discord.ext import commands
import json
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

        with open('./users.json', 'r') as file:

            data=json.load(file)

            #check if the user in json file
            if str(interaction.user.id) not in data:
                data[str(interaction.user.id)] = {
                    "point": 0,
                    "charge_combo": 0,
                    "last_charge": "1970-01-01",
                    "next_lottery": 7,
                    "num_comment": 0,
                    "last_comment": "1970-01-01",
                    "num_comment_point": {"times": 2, "next_reward": 1}
                }

            last_charge = data[str(interaction.user.id)]['last_charge']
            last_charge = datetime.strptime(last_charge, '%Y-%m-%d')

            combo = data[str(interaction.user.id)]['charge_combo']

            point = data[str(interaction.user.id)]['point']
            
            next_lottery = data[str(interaction.user.id)]['next_lottery']

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
                    writer.writerow([str(interaction.user.id), str(interaction.user.name), '5', str(data[str(interaction.user.id)]['point']), 'daily_charge', str(datetime.now())])
            
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
                    writer.writerow([str(interaction.user.id), str(interaction.user.name), '5', str(data[str(interaction.user.id)]['point']), 'daily_charge', str(datetime.now())])

            data[str(interaction.user.id)]['last_charge'] = last_charge
            data[str(interaction.user.id)]['charge_combo'] = combo
            data[str(interaction.user.id)]['point'] = point
            data[str(interaction.user.id)]['next_lottery'] = next_lottery

            with open('./users.json', 'w') as writer:
                json.dump(data, writer, indent=4)
            

def setup(bot):
    bot.add_cog(daily_charge(bot))