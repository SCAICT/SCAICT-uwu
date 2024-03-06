import discord
from build.build import build
from discord.ext import commands
from discord.commands import Option
import json
import random
# import user
from cog.core.SQL import read
from cog.core.SQL import write
from cog.core.SQL import end    #用來結束和SQL資料庫的會話
from cog.core.SQL import linkSQL
from datetime import datetime
import csv

def getCTFFile():
    with open("./database/ctf.json", "r") as file:
        return json.load(file)
def getCTFmakers():
    with open("./database/server.config.json", "r") as file:
        return json.load(file)
# By EM
class ctf(build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.ctfView())

    ctf_commands = discord.SlashCommandGroup("ctf", "CTF 指令")

    class ctfView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)  # timeout of the view must be set to None
        @discord.ui.button(label="回報 Flag", style=discord.ButtonStyle.blurple, emoji="🚩" ,custom_id="new_ctf")
        async def button_callback_1(self, button, interaction):
            class SubmitModal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)
                    self.add_item(discord.ui.InputText(label="Flag", placeholder="Flag", required=True))
                async def callback(self, interaction: discord.Interaction):
                    ctfFile = getCTFFile()
                    question_id = interaction.message.embeds[0].footer.text.split(": ")[1]
                    ctf_question = ctfFile[question_id]
                    current_time = datetime.now()
                    if datetime.strptime(ctf_question["start"], '%y/%m/%d %H:%M:%S') > current_time:
                        await interaction.response.send_message("答題時間尚未開始！",ephemeral=True)
                        return
                    if ctf_question["end"] != "None" and datetime.strptime(ctf_question["end"], '%y/%m/%d %H:%M:%S') < current_time:
                        await interaction.response.send_message("目前不在作答時間內！",ephemeral=True)
                        return
                    userId = interaction.user.id
                    if str(userId) not in ctf_question["history"]:
                        ctfFile[question_id]["history"][str(userId)] = 0
                    if ctf_question["limit"]!='∞':#無限沒辦法比大小，直接跳過這個邏輯
                        if str(userId) in ctf_question["history"] and ctf_question["history"][str(userId)] >= int(ctf_question["limit"]):
                            await interaction.response.send_message("你已經回答超過限制次數了喔！",ephemeral=True)
                            return
                    ctfFile[question_id]["history"][str(userId)] = ctfFile[question_id]["history"][str(userId)] + 1
                    ctfFile[question_id]["tried"] = ctf_question["tried"] + 1
                    response_flag = self.children[0].value
                    answer = ctf_question["flag"]
                    if response_flag == answer:
                        CONNECTION,CURSOR=linkSQL()#SQL 會話
                        if int(userId) in ctf_question["solved"]:
                            embed = discord.Embed(title="答題成功!")
                            embed.add_field(name=""  , value="但你已經解答過了所以沒有 :zap: 喔！", inline=False)
                            await interaction.response.send_message(ephemeral=True,embeds=[embed])
                            return
                        current_point = read(userId, "point",CURSOR)
                        new_point = current_point + int(ctf_question["score"])
                        ctfFile[question_id]["solved"].append(userId)
                        write(userId, "point", new_point,CURSOR)
                        with open('./database/point_log.csv', 'a+', newline='') as log:
                            writer = csv.writer(log)
                            writer.writerow([userId, str(interaction.user.name),ctf_question["score"] , str(
                                read(userId, 'point',CURSOR)), 'ctf', str(datetime.now())])
                        embed = discord.Embed(title="答題成功!")
                        embed.add_field(name="+" + str(ctf_question["score"]) + ":zap:" , value="=" + str(new_point), inline=False)
                        await interaction.response.send_message(embeds=[embed],ephemeral=True)
                    else:
                        embed = discord.Embed(title="答案錯誤!")
                        embed.add_field(name="嘗試次數" , value=str(ctf_question["history"][str(userId)]) + "/"+ str(ctf_question["limit"]), inline=False)
                        await interaction.response.send_message(embeds=[embed],ephemeral=True)
                    with open("./database/ctf.json", "w") as outfile:
                        json.dump(ctfFile, outfile)
                    end(CONNECTION,CURSOR)
                    # edit the original message
                    embed = interaction.message.embeds[0]
                    embed.set_field_at(0, name="已完成", value=str(len(ctfFile[question_id]["solved"])), inline=True)
                    embed.set_field_at(1, name="已嘗試", value=str(ctfFile[question_id]["tried"]), inline=True)
                    embed.set_field_at(2, name="回答次數限制", value=str(ctfFile[question_id]["limit"]), inline=True)
                    # set the new embed
                    await interaction.message.edit(embed=embed)
            await interaction.response.send_modal(SubmitModal(title="你找到 Flag 了嗎？"))
    @ctf_commands.command(name="create", description="新題目")
    async def create(self, ctx: discord.Interaction,
        title: Option(str, "題目標題", required=True, default=''),  
        flag: Option(str, "輸入 flag 解答", required=True, default=''), 
        score: Option(int, "分數", required=True, default='20'), 
        limit: Option(int, "限制回答次數", required=False, default=''),
        case: Option(bool, "大小寫忽略", required=False, default=False), 
        start: Option(str, f"開始作答日期 ({datetime.now().strftime('%y/%m/%d %H:%M:%S')})", required=False, default=""), 
        end: Option(str, f"截止作答日期 ({datetime.now().strftime('%y/%m/%d %H:%M:%S')})", required=False, default="")):
        role_id =getCTFmakers()["SCAICT-alpha"]["SP-role"]["CTF_Maker"]#get ctf maker role's ID 
        # Check whether the user can send a question or not
        role = discord.utils.get(ctx.guild.roles, id=role_id)
        if role not in ctx.author.roles:
            await ctx.respond("你沒有權限創建題目喔！")
            return
        # 確認是否有填寫 title 和 flag
        if title == '' or flag == '':
            await ctx.respond("請填寫題目標題和 flag")
            return
        newId = generateCTFId()
        ctfFile = getCTFFile()
        while (newId in ctfFile):
            newId = generateCTFId()
        start = datetime.strptime(start, '%y/%m/%d %H:%M:%S') if start != "" else datetime.now().strftime('%y/%m/%d %H:%M:%S')
        end = datetime.strptime(end, '%y/%m/%d %H:%M:%S') if end != "" else None
        limit = "∞" if limit == "" else limit
        embed = discord.Embed(
            title=title,
            description="+" +
                        str(score)+"⚡",
            color=0xff24cf,
            )
        embed.set_author(name="SCAICT CTF", icon_url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
        embed.add_field(name="已完成", value= "0", inline=True)
        embed.add_field(name="已嘗試", value= "0", inline=True)
        embed.add_field(name="回答次數限制", value="0/"+limit,inline=True )
        embed.add_field(name="開始作答日期", value=start, inline=True)
        embed.add_field(name="截止作答日期", value=end, inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="可於下方討論，但請勿公布答案", value="", inline=False)
        embed.set_footer(text="題目 ID: "+newId)
        response = await ctx.respond(embed=embed, view=self.ctfView())
        messageId = response.id
        ctfFile[newId] = {"flag": flag, 
                          "score": score, 
                          "limit": limit, 
                          "messageId": messageId,
                          "case": case,
                          "start": str(start), 
                          "end": str(end), 
                          "title": title,
                          "solved":[],
                          "tried": 0,
                          "history": {}}
        with open("./database/ctf.json", "w") as outfile:
            json.dump(ctfFile, outfile)

    # 測試用
    # @ctf_commands.command(description="球")
    # async def ping(self, ctx):
    #     await ctx.respond(user.read(ctx.author.id, "point"))
    
    @ctf_commands.command(description="列出所有題目")
    async def list_all(self, ctx):
        question_list = ["**CTF 題目列表:**"]
        ctfFile = getCTFFile()
        for question_id, question_data in ctfFile.items():
            question_list.append(
                f"* **{question_data['title']}** - {question_data['score']} :zap: *({question_id})*")
        question_text = "\n".join(question_list)
        await ctx.respond(question_text)

    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot

    def setup(self):
        self.bot.add_application_command(ctf_commands)

def setup(bot):
    bot.add_cog(ctf(bot))

def generateCTFId():
    return str(random.randint(1000000000000000000, 9999999999999999999))
