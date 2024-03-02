import discord
from discord.ext import commands
import json
from datetime import datetime
from datetime import timedelta
import csv
from cog.core.SQL import read
from cog.core.SQL import write
from cog.core.SQL import isExist
from cog.core.SQL import end    #用來結束和SQL資料庫的會話
from cog.core.secret import connect
def initUser(userId):#初始化(創建)傳入該ID的表格
    connection=connect()
    cursor=connection.cursor()
    
    cursor.execute(f"INSERT INTO USER(uid,point,ticket,charge_combo,next_lottery,today_comments,last_charge,last_comment)\
                                    VALUE({userId},0,0,0,0,0,'1970-01-01','1970-01-01')")
    end(connection,cursor)

def initCommentPoints(userId):#初始化(創建)傳入該ID的表格
    connection=connect()
    cursor=connection.cursor()
    
    cursor.execute(f"INSERT INTO CommentPoints(uid,times,next_reward)\
                                    VALUE({userId},0,0)")
    end(connection,cursor)
class comment(commands.Cog):

    def __init__(self, bot):
        self.bot=bot

    def reset(self,message, now):
        userId=message.author.id
        write(message.author.id,"today_comments",0)#歸零發言次數
        write(userId,"last_comment",str(now))
        write(userId,"times",2,"CommentPoints")#初始化達標後能獲得的電電點
        write(userId,"next_reward",1,"CommentPoints")
    

    def reward(self,userId, now):
        #讀USER資料表的東西
        today_comments=read(userId,"today_comments")
        point=read(userId,"point")
        #讀CommentPoints 資料表裡面的東西，這個表格紀錄有關發言次數非線性加分的資料
        next_reward=read(userId,"next_reward","CommentPoints")
        times=read(userId,"times","CommentPoints")

        today_comments+=1
        
        if today_comments==next_reward:
            point+=2
            next_reward+=times**2#Each直覺:感覺怪怪的
            times+=1
            write(userId,"point",point)
            write(userId,"next_reward",next_reward,"CommentPoints")
            write(userId,"times",times,"CommentPoints")
        write(userId,"today_comments",today_comments)
        with open('./point_log.csv', 'a+', newline='') as log:
            writer = csv.writer(log)
            writer.writerow([str(userId), str(userId), '2', str(read(userId,"point")), 'comment', str(datetime.now())])
    

    @commands.Cog.listener()
    async def on_message(self, message):
        userId=message.author.id
        #創建該user的資料表
        if not(isExist(userId,"USER")):#該 uesr id 不在USER表格內，插入該筆用戶資料
            initUser(userId)
        if not(isExist(userId,"CommentPoints")):
            initUser()
        now = datetime.now().replace(microsecond=0)
        delta = timedelta(days=1)

        last_comment  = read(userId, 'last_charge')#SQL回傳型態:<class 'datetime.date'>
        last_comment  = datetime.strptime(str(last_comment), '%Y-%m-%d %H:%M:%S')#strptime轉型後':<class 'datetime.datetime'>

        if(now-last_comment >= delta):#把昨天或更早的發言次數歸零
            self.reset(message, now)

        self.reward(userId, now)
        

def setup(bot):
    bot.add_cog(comment(bot))