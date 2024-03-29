import discord
from discord.ext import commands
from datetime import datetime
import csv
import os
import json
from cog.core.SQL import write
from cog.core.SQL import read
from cog.core.SQL import linkSQL
from cog.core.SQL import end

def getChannels():#要特殊用途頻道的列表，這裡會用來判斷是否在簽到頻簽到，否則不予授理
    
    with open(f"{os.getcwd()}/DataBase/server.config.json", "r") as file:
        return json.load(file)["SCAICT-alpha"]["channel"]


class charge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send_message(self, point, combo, interaction):
        #讀表符ID
        with open(f"{os.getcwd()}/DataBase/server.config.json", "r") as file:
            stickers=json.load(file)["SCAICT-alpha"]["stickers"]
        
        
        self.embed = discord.Embed(title=f"{interaction.user.name}剛剛充電了!", description="",color=0x14e15c)
        
        if interaction.user.avatar!=None:#預設頭像沒有這個
            self.embed.set_thumbnail(url=str(interaction.user.avatar))

        self.embed.add_field(name="",
                             value=":battery:+5:zap:= "+str(point)+f"{stickers['logo']}", inline=False)
        self.embed.add_field(name="連續登入獎勵: "+str(combo)+"/" +
                             str(combo + 7- combo % 7), value='\n', inline=False)
        self.embed.set_footer(text=f"{interaction.user.name}充電成功!")
        await interaction.response.send_message(embed=self.embed)
        
    async def already_charge(self, interaction):
        self.embed = discord.Embed(color=0xff0000)
        if interaction.user.avatar!=None:#預設頭像沒有這個
            self.embed.set_thumbnail(url=str(interaction.user.avatar))
        self.embed.add_field(name="您夠電了，明天再來!", value="⚡⚡⚡🛐🛐🛐", inline=False)
        await interaction.response.send_message(embed=self.embed,ephemeral=True)
        
    async def channelError(self,interaction):
        self.embed = discord.Embed(color=0xff0000)
        self.embed.set_thumbnail(url="https://http.cat/images/404.jpg")
        self.embed.add_field(name="這裡似乎沒有打雷...", value="  ⛱️", inline=False)
        self.embed.add_field(name="到'每日充電'頻道試試吧!", value="", inline=False)
        #其他文案:這裡似乎離無線充電座太遠了，到'每日充電'頻道試試吧! 待商議
        await interaction.response.send_message(embed=self.embed, ephemeral=True)
        
        
    @discord.slash_command(name="charge", description="每日充電")
    async def charge(self, interaction):
        userId = interaction.user.id
        CONNECTION,CURSOR=linkSQL()#SQL 會話
        last_charge = read(userId, 'last_charge',CURSOR)#SQL回傳型態:<class 'datetime.date'>
        last_charge = datetime.strptime(str(last_charge), '%Y-%m-%d %H:%M:%S')#strptime轉型後':<class 'datetime.datetime'>
        # get now time and combo
        now = datetime.now().replace(microsecond=0)
        combo = read(userId, 'charge_combo',CURSOR)#連續登入
        point = read(userId, 'point',CURSOR)
        if (interaction.channel.id!=getChannels()["everyDayCharge"]):
            await self.channelError(interaction)
            return
        if (now.date() == last_charge.date()):#今天已經充電過了
            await self.already_charge(interaction)
            return
        else:
            combo = 1 if (now - last_charge).days > 1 else combo + 1
            point += 5
            write(userId, 'last_charge', now,CURSOR)
            write(userId, 'charge_combo', combo,CURSOR)
            write(userId, 'point', point,CURSOR)
            await self.send_message(point, combo, interaction)
            
            #紀錄log
            print(f"{interaction.user.id},{interaction.user} Get 5 point by daily_charge {datetime.now()}")
        end(CONNECTION,CURSOR)



def setup(bot):
    bot.add_cog(charge(bot))
