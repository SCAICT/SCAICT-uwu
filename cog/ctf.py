# Standard imports
from datetime import datetime
import json
import os
import random
# Third-party imports
import discord
from discord.ext import commands
from discord.commands import Option
# Local imports
from build.build import Build
from cog.core.sql import read
from cog.core.sql import write
from cog.core.sql import end as endSQL # 用來結束和SQL資料庫的會話，平常都用end()，但和 Discord 指令變數名稱衝突，所以這裡改名
from cog.core.sql import link_sql

def getCTFmakers():
    with open(f"{os.getcwd()}/DataBase/server.config.json", "r") as file:
        return json.load(file)

# By EM
def generateCTFId():
    return str(random.randint(100000000000000000, 999999999999999999))
class ctf(Build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.CTFView())

    ctf_commands = discord.SlashCommandGroup("ctf", "CTF 指令")

    class CTFView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None
        @discord.ui.button(label="回報 Flag", style=discord.ButtonStyle.blurple, emoji="🚩" ,custom_id="new_ctf")
        #user送出flag
        async def button_callback_1(self, button, interaction):
            class SubmitModal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)
                    self.add_item(
                        discord.ui.InputText(label = "Flag", placeholder = "Flag", required = True))

                async def callback(self, interaction: discord.Interaction):
                    CONNECTION,CURSOR=link_sql()#SQL 會話
                    CURSOR.execute(f"USE CTF;")
                    question_id = interaction.message.embeds[0].footer.text.split(": ")[1]
                    #startTime
                    CURSOR.execute(f"SELECT start_time FROM data WHERE id={question_id};")
                    starTime=str(CURSOR.fetchone()[0])
                    #endTime
                    CURSOR.execute(f"SELECT end_time FROM data WHERE id={question_id};")
                    end=str(CURSOR.fetchone()[0])
                    
                    #判斷是否在作答時間內
                    current_time = datetime.now()
                    if datetime.strptime(starTime, '%Y-%m-%d %H:%M:%S') > current_time:
                        await interaction.response.send_message("答題時間尚未開始！",ephemeral=True)
                        endSQL(CONNECTION,CURSOR)
                        return
                    if end != "None" and datetime.strptime(end, '%y/%m/%d %H:%M:%S') < current_time:
                        await interaction.response.send_message("目前不在作答時間內！",ephemeral=True)
                        endSQL(CONNECTION,CURSOR)
                        return
                    userId = interaction.user.id
                    nickName = interaction.user
                    #判斷題目可作答次數
                    CURSOR.execute(f"SELECT count FROM history WHERE data_id={question_id} AND uid={userId};")
                    #return None or tuple.like (1,)
                    answerCount=CURSOR.fetchone()#使用者回答次數
                    #第一次作答flag
                    notExist =False if answerCount!=None else True
                    if notExist:
                        #初始化作答次數
                        CURSOR.execute(f"INSERT INTO history (data_id,uid,count) VALUES ({question_id},{userId},0);")
                        answerCount=0
                        # ctfFile[question_id]["history"][str(userId)] = 0
                    else:
                        answerCount=answerCount[0]
                    CURSOR.execute(f"SELECT restrictions FROM data WHERE id={question_id};")
                    restrictions =str(CURSOR.fetchone()[0])#最大作答次數
                    if restrictions !='∞':#無限沒辦法比大小，不用判斷有沒有超過限制
                        #判斷用戶是否超過每人限制次數
                        if  answerCount>=int(restrictions):
                            await interaction.response.send_message("你已經回答超過限制次數了喔！",ephemeral=True)
                            endSQL(CONNECTION,CURSOR)
                            return

                    #更新作答次數，包括總表和個人表
                    CURSOR.execute(f"UPDATE history SET count=count+1 WHERE data_id={question_id} AND uid={userId};")
                    answerCount+=1#SQL和變數同步，變數之後還要用
                    CURSOR.execute(f"UPDATE data SET tried=tried+1 WHERE id={question_id};")
                    
                    #製造 embed 前置作業-取得必要數值
                    CURSOR.execute(f"SELECT tried FROM data WHERE id={question_id};")
                    totalTried = int(CURSOR.fetchone()[0])#該題總共嘗試次數
                    CURSOR.execute(f"SELECT COUNT(*) FROM history WHERE data_id={question_id} AND solved=1;")
                    totalSolved = int(CURSOR.fetchone()[0])#該題完成人數
                    
                    #取得使用者輸入的 flag
                    response_flag = self.children[0].value
                    CURSOR.execute(f"SELECT flags FROM data WHERE id={question_id};")
                    answer =str(CURSOR.fetchone()[0])
                    #輸入內容為正確答案
                    if response_flag == answer:
                        #判斷是否重複回答
                        CURSOR.execute(f"SELECT solved FROM history WHERE data_id={question_id} AND uid={userId};")
                        isSolved=int(CURSOR.fetchone()[0])
                        if isSolved:
                            embed = discord.Embed(title="答題成功!")
                            embed.add_field(name=""  , value="但你已經解答過了所以沒有 :zap: 喔！", inline=False)
                            await interaction.response.send_message(ephemeral=True,embeds=[embed])
                            return
                        else:#未曾回答過，送獎勵
                            CURSOR.execute(f"UPDATE history SET solved=1 WHERE data_id={question_id} AND uid={userId};")
                            CURSOR.execute(f"SELECT score FROM data WHERE id={question_id};")
                            reward=int(CURSOR.fetchone()[0])
                            CURSOR.execute(f"USE Discord;")#換資料庫存取電電點
                            current_point = read(userId, "point",CURSOR)
                            new_point = current_point + reward
                            #更新用戶電電點
                            write(userId, "point", new_point,CURSOR)
                            #更新作答狀態
                            #log
                            print(f'{userId},{nickName} Get {reward} by ctf, {str(datetime.now())}')
                            
                            embed = discord.Embed(title="答題成功!")
                            embed.add_field(name="+" + str(reward) + ":zap:" , value="=" + str(new_point), inline=False)
                            await interaction.response.send_message(embeds=[embed],ephemeral=True)
                    else:
                        embed = discord.Embed(title="答案錯誤!")
                        embed.add_field(name="嘗試次數" , value=str(answerCount) + "/"+ str(restrictions), inline=False)
                        await interaction.response.send_message(embeds=[embed],ephemeral=True)

                    # edit the original message
                    #更新題目顯示狀態
                    embed = interaction.message.embeds[0]
                    embed.set_field_at(0, name="已完成", value=str(totalSolved), inline=True)
                    embed.set_field_at(1, name="已嘗試", value=str(totalTried), inline=True)
                    embed.set_field_at(2, name="回答次數限制", value=str(restrictions), inline=True)
                    # set the new embed
                    await interaction.message.edit(embed=embed)
                    endSQL(CONNECTION,CURSOR)#結束SQL會話
            await interaction.response.send_modal(SubmitModal(title="你找到 Flag 了嗎？"))
    @ctf_commands.command(name="create", description="新題目")
    #生成新題目
    async def create(self, ctx,
        title: Option(str, "題目標題", required=True, default=''),  
        flag: Option(str, "輸入 flag 解答", required=True, default=''), 
        score: Option(int, "分數", required=True, default='20'), 
        limit: Option(int, "限制回答次數", required=False, default=''),
        case: Option(bool, "大小寫忽略", required=False, default=False), 
        start: Option(str, f"開始作答日期 ({datetime.now().strftime('%y/%m/%d %H:%M:%S')})", required=False, default=""), #時間格式
        end: Option(str, f"截止作答日期 ({datetime.now().strftime('%y/%m/%d %H:%M:%S')})", required=False, default="")):
        #SQL沒有布林值，所以要將T/F轉換成0或1
        case=1 if case else 0
        role_id =getCTFmakers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]#get ctf maker role's ID 
        # Check whether the user can send a question or not
        role = discord.utils.get(ctx.guild.roles, id = role_id)
        if role not in ctx.author.roles:
            await ctx.respond("你沒有權限建立題目喔！", mephemeral = True)
            return
        # 確認是否有填寫 title 和 flag
        if title == '' or flag == '':
            await ctx.respond("請填寫題目標題和 flag", ephemeral = True)
            return
        # ctfFile = getCTFFile()
        
        CONNECTION,CURSOR=link_sql()#SQL 會話
        CURSOR.execute("USE CTF;")
        while (1):
            newId = generateCTFId()
            #找尋是否有重複的ID，若無則跳出迴圈
            CURSOR.execute(f"select id from data WHERE EXISTS(select id from data WHERE id={newId});")
            idExist=CURSOR.fetchone()
            if(idExist==None):
                break
        #轉型程SQL datetime格式 %Y-%m-%d %H:%M:%S
        start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S') if start != "" else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end = f"'{datetime.strptime(end, '%Y-%m-%d %H:%M:%S')}'" if end != "" else "NULL"
        #limit若沒有填寫，設為可嘗試無限次
        limit = "∞" if limit == "" else limit
        embed = discord.Embed(
            title = title,
            description = "+" + str(score) + "⚡",
            color = 0xff24cf,
        )
        embed.set_author(
            name = "SCAICT CTF",
            icon_url = "https://cdn-icons-png.flaticon.com/128/14929/14929899.png"
        )
        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
        embed.add_field(name="已完成", value= "0", inline=True)
        embed.add_field(name="已嘗試", value= "0", inline=True)
        embed.add_field(name="回答次數限制", value=f"0/{limit}",inline=True )
        embed.add_field(name="開始作答日期", value=start, inline=True)
        embed.add_field(name="截止作答日期", value=end, inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="可於下方討論，但請勿公布答案", value="", inline=False)
        embed.set_footer(text="題目 ID: "+newId)
        #embed格式別亂改，會影響回應訊息時取值
        await ctx.respond("題目創建成功!",ephemeral=True)
        response = await ctx.send(embed=embed, view=self.ctfView())
        messageId = response.id
        
        #在CTF資料庫中的data表格新增一筆ctf資料
        # print(f"INSERT INTO `data`\
        # (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) VALUES \
        # ({newId},'{flag}',{score},'{limit}',{messageId},{case},'{start}',{end},\'{title}\',{0});")
        CURSOR.execute(f"INSERT INTO `data`\
        (id,flags,score,restrictions,message_id,case_status,start_time,end_time,title,tried) VALUES \
        ({newId},'{flag}',{score},'{limit}',{messageId},{case},'{start}',{end},\'{title}\',{0});")
        #CTFID,flag,score,可嘗試次數,message_id,大小寫限制,作答開始時間,作答結束時間,題目標題,已嘗試人數
        endSQL(CONNECTION,CURSOR)

        
#刪除題目，等等寫
    # @ctf_commands.command(name="delete", description="刪除題目")
    # async def deleteCTF(self, ctx, question_id: str):
    #     role_id =getCTFmakers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]
    # 列出所有題目
    @ctf_commands.command(description="列出所有題目")
    async def list_all(self, ctx):
        question_list = ["# **CTF 題目列表:**"]
        connection, cursor=link_sql()
        cursor.execute("use CTF;")
        cursor.execute("SELECT title,score,id FROM data")
        ctfinfo=cursor.fetchall()
        for title,score,qID in ctfinfo:
            question_list.append(
                f"* **{title}** - {score} :zap: *({qID})*")
        question_text = "\n".join(question_list)
        await ctx.respond(question_text)
        endSQL(connection, cursor)

def setup(bot):
    bot.add_cog(ctf(bot))

