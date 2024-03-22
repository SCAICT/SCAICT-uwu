import discord
from discord.ext import commands
import json
from datetime import datetime
from datetime import date
from datetime import timedelta
import csv
import os
from cog.core.SQL import read
from cog.core.SQL import write
from cog.core.SQL import isExist
from cog.core.SQL import end    #用來結束和SQL資料庫的會話
from cog.core.SQL import linkSQL
def insertUser(userId,TABLE,CURSOR):#初始化(創建)傳入該ID的表格
    CURSOR.execute(f"INSERT INTO {TABLE} (uid) VALUE({userId})")#其他屬性在創造時MYSQL會給預設值
def getChannels():#要特殊用途頻道的列表，這裡會用來判斷是否在簽到頻簽到，否則不予授理
    #os.chdir("./")
    with open(f"{os.getcwd()}/DataBase/server.config.json", "r") as file:
        return json.load(file)["SCAICT-alpha"]["channel"]

class comment(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    def reset(self,message, now,CURSOR):
        userId=message.author.id
        write(userId,"today_comments",0,CURSOR)#歸零發言次數
        write(userId,"last_comment",str(now),CURSOR)
        write(userId,"times",2,CURSOR,TABLE="CommentPoints")#初始化達標後能獲得的電電點
        write(userId,"next_reward",1,CURSOR,TABLE="CommentPoints")
    

    def reward(self,message,CURSOR):
        #讀USER資料表的東西
        userId=message.author.id
        nickName=message.author
        today_comments=read(userId,"today_comments",CURSOR)
        point=read(userId,"point",CURSOR)
        #讀CommentPoints 資料表裡面的東西，這個表格紀錄有關發言次數非線性加分的資料
        next_reward=read(userId,"next_reward",CURSOR,TABLE="CommentPoints")
        times=read(userId,"times",CURSOR,TABLE="CommentPoints")

        today_comments+=1
        
        if today_comments==next_reward:
            point+=2
            next_reward+=times**2
            times+=1
            write(userId,"point",point,CURSOR)
            write(userId,"next_reward",next_reward,CURSOR,TABLE="CommentPoints")
            write(userId,"times",times,CURSOR,TABLE="CommentPoints")
    
            #紀錄log
            print(f"{userId},{nickName} Get 2 point by comment {datetime.now()}")
        write(userId,"today_comments",today_comments,CURSOR)

    

    @commands.Cog.listener()
    async def on_message(self, message):
        userId=message.author.id
        CONNECTION,CURSOR=linkSQL()#SQL 會話

        spChannel=getChannels()#特殊用途的channel
        #創建該user的資料表
        if userId==1214954731747680326 or message.channel.id==spChannel["commandChannel"]:
            #機器人會想給自己記錄電電點，必須排除
            return
        if not(isExist(userId,"USER",CURSOR)):#該 uesr id 不在USER表格內，插入該筆用戶資料
            insertUser(userId,"USER",CURSOR)
        if not(isExist(userId,"CommentPoints",CURSOR)):
            insertUser(userId,"CommentPoints",CURSOR)
        now = date.today()
        delta = timedelta(days=1)
        last_comment  = read(userId, 'last_comment',CURSOR)#SQL回傳型態:<class 'datetime.date'>

        if message.channel.id==spChannel["countChannel"]:
            hex_string = message.content
            decimal_number = int(hex_string, 16)
            with open(f"{os.getcwd()}/DataBase/game.json", "r") as file:
                game = json.load(file)
            if decimal_number == game["count"]+1:
                game["count"]=decimal_number
                with open(f"{os.getcwd()}/DataBase/game.json", "w") as file:
                    json.dump(game,file)
                # add a check emoji to the message
                await message.add_reaction("✅")
            else:
                await message.add_reaction("❌")

        if(now-last_comment >= delta):
            self.reset(message, now,CURSOR)

        self.reward(message,CURSOR)
        end(CONNECTION,CURSOR)
        
        

def setup(bot):
    bot.add_cog(comment(bot))
