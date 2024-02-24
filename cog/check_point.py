import discord
from discord.ext import commands
import json
from datetime import datetime


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
        self.embed.add_field(name="距離下次連續登入獎勵 : "+str(next_lottery), value='\n', inline=False)
        await interaction.response.send_message(embed=self.embed)

    @discord.slash_command(name="check_point", description="查看電電點")
    async def check(self, interaction: discord.Interaction):
       
        member=interaction.user.mention

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

                with open('./users.json', 'w') as f:
                    json.dump(data, f, indent=4)

            last_charge = data[str(interaction.user.id)]['last_charge']
            last_charge = datetime.strptime(last_charge, '%Y-%m-%d')

            combo = data[str(interaction.user.id)]['charge_combo']
            point = data[str(interaction.user.id)]['point']
            next_lottery = data[str(interaction.user.id)]['next_lottery']

            await self.send_message(point, combo, next_lottery, interaction)

def setup(bot):
    bot.add_cog(check_point(bot))
