import discord
from build.build import build
from discord.ext import commands
from discord.commands import Option
import json
import random
import user
with open("./database/ctf.json", "r") as file:
    ctfFile = json.load(file)
    
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
                    embed = discord.Embed(title="答題成功!")
                    embed.add_field(name="Short Input", value=self.children[0].value)
                    await interaction.response.send_message(embeds=[embed])
            await interaction.response.send_modal(SubmitModal(title="Modal via Slash Command"))

    @ctf_commands.command(name="create", description="新題目")
    async def create(self, ctx: discord.Interaction,
        title: Option(str, "題目標題", required=True, default=''),  
        flag: Option(str, "輸入 flag 解答", required=True, default=''), 
        score: Option(int, "分數", required=True, default='20'), 
        limit: Option(int, "限制回答次數", required=False, default=''),
        case: Option(bool, "大小寫忽略", required=False, default=False), 
        start: Option(str, "開始作答日期", required=False, default=""), 
        end: Option(str, "截止作答日期", required=False, default="")):
        newId = generateCTFId()
        while (newId in ctfFile):
            newId = generateCTFId()
        ctfFile[newId] = {"flag": flag, "score": score, "limit": limit}
        
        with open("ctf.json", "w") as outfile:
            json.dump(ctfFile, outfile)

        limit = "∞" if limit == None else limit
        embed = discord.Embed(color=0xff24cf)
        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
        embed.add_field(name="按下方按鈕回報 flag", value="+" +
                        str(score)+"⚡", inline=False)
        embed.add_field(name="", value="已完成: 10\n回答次數: 0/" +
                        limit, inline=False)
        embed.add_field(name="可於下方討論，但請勿公布答案", value="", inline=False)
        embed.set_footer(text="ID"+newId)
        await ctx.respond(embed=embed, view=self.ctfView())

    # 測試用
    @ctf_commands.command(description="球")
    async def ping(self, ctx):
        user.write(ctx.author.id, "point", 1000)
        await ctx.respond(user.read(ctx.author.id, "point"))
    
    @ctf_commands.command(description="列出所有題目")
    async def list_all(self, ctx):
        question_list = []
        for question_id, question_data in ctfFile.items():
            question_list.append(
                f"* {question_id} - {question_data['score']} point")
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
