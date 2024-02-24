import discord
from build.build import build
from discord.ext import commands
from discord.commands import Option
import json
import random

with open("ctf.json","r") as file:
        ctfFile = json.load(file)
# By EM
class ctf(build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.ctfView())
        
    
    ctf_commands  = discord.SlashCommandGroup("ctf", "CTF 指令")
    class ctfView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None
        @discord.ui.button(label="回報 Flag",style=discord.ButtonStyle.blurple,emoji="🚩",custom_id="new_ctf")
        async def button_callback_1(self,button,interaction):
            await interaction.response.send_message("好我還沒做完",ephemeral=True)

    @ctf_commands.command(name = "create", description = "新題目")
    # @option(flag = "輸入 flag 解答", score = "分數", limit = "限制次數(空白無限制)")
    async def create(self,ctx: discord.Interaction, flag: Option(str, "輸入 flag 解答", required = True, default = ''), score: Option(int, "分數", required = True, default = '20'), limit: Option(int, "限制回答次數", required = False, default = '')):
        newId = generateCTFId()
        while(newId in ctfFile):
            newId = generateCTFId()
        ctfFile[newId] = {"flag":flag,"score":score,"limit":limit}
        
        with open("ctf.json", "w") as outfile:
            json.dump(ctfFile, outfile)
            
        limit = "∞" if limit == None else limit
        embed=discord.Embed(color=0xff24cf)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
        embed.add_field(name="按下方按鈕回報 flag", value="+"+str(score)+"⚡", inline=False)
        embed.add_field(name="", value="已完成: 10\n回答次數: 0/" + limit, inline=False)
        embed.add_field(name="可於下方討論，但請勿公布答案", value="", inline=False)
        embed.set_footer(text="ID"+newId)
        await ctx.respond(embed=embed,view=self.ctfView())

    @ctf_commands.command(description="ball.") # this decorator makes a slash command
    async def ping(self,ctx): # a slash command will be created with the name "ping"
        print(ctfFile["1210607581190688879"])
        await ctx.respond("Pong!")
    
    @ctf_commands.command(description="列出所有題目") # this decorator makes a slash command
    async def list_all(self,ctx):
        question_list = []
        for question_id, question_data in ctfFile.items():
            question_list.append(f"* {question_id} - {question_data['score']} point")
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
    return str(random.randint(1000000000000000000,9999999999999999999))