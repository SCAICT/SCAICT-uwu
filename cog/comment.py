import discord
from discord.ext import commands
import json
from datetime import datetime
from datetime import timedelta
import csv


class comment(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    def reset(self, data, message, now):
        data[str(message.author.id)]['num_comment'] = 0
        data[str(message.author.id)]['last_comment'] = str(now.year)+"-"+str(now.month)+"-"+str(now.day)
        data[str(message.author.id)]['num_comment_point'] = {"times": 2, "next_reward": 1}
        return data
    

    def reward(self, data, message, now):
        data[str(message.author.id)]['num_comment'] += 1
        data[str(message.author.id)]['last_comment'] = str(now.year)+"-"+str(now.month)+"-"+str(now.day)

        if(data[str(message.author.id)]['num_comment'] == data[str(message.author.id)]['num_comment_point']['next_reward']):

            data[str(message.author.id)]['point'] += 2
            times = data[str(message.author.id)]['num_comment_point']['times']
            data[str(message.author.id)]['num_comment_point']['next_reward'] += times*times
            data[str(message.author.id)]['num_comment_point']['times'] += 1
            
            with open('./point_log.csv', 'a+', newline='') as log:
                writer = csv.writer(log)
                writer.writerow([str(message.author.id), str(message.author.name), '2', str(data[str(message.author.id)]['point']), 'comment', str(datetime.now())])

        return data
    

    @commands.Cog.listener()
    async def on_message(self, message):
        with open('./database/users.json', 'r') as file:

            data = json.load(file)

            if str(message.author.id) not in data:
                data[str(message.author.id)] = {
                    "point": 0,
                    "charge_combo": 0,
                    "last_charge": "1970-01-01",
                    "next_lottery": 7,
                    "num_comment": 0,
                    "last_comment": "1970-01-01",
                    "num_comment_point": {"times": 2, "next_reward": 1}
                }

            now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            delta = timedelta(days=1)

            last_comment = data[str(message.author.id)]['last_comment']
            last_comment = datetime.strptime(last_comment, '%Y-%m-%d')

            if(now-last_comment >= delta):
                data = self.reset(data, message, now)

            data = self.reward(data, message, now)

            with open('./database/users.json', 'w') as writer:
                json.dump(data, writer, indent=4)

def setup(bot):
    bot.add_cog(comment(bot))