import discord
from build.build import build
from discord.ext import commands

class ctf(build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.ctfView())

    ctf_commands  = discord.SlashCommandGroup("ctf", "CTF 指令")

    #成員身分組
    class ctfView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None
        @discord.ui.button(label="回報 Flag",style=discord.ButtonStyle.blurple,emoji="🚩",custom_id="new_ctf")
        async def button_callback_1(self,button,interaction):
            await interaction.response.send_message("已收到 flag",ephemeral=True)
            
    @ctf_commands.command()
    async def create_ctf(self,ctx):
        embed=discord.Embed(color=0xff24cf)
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/128/14929/14929899.png")
        embed.add_field(name="按下方按鈕回報 flag", value="+20⚡", inline=False)
        embed.add_field(name="", value="已完成: 10\n可回答次數: ∞", inline=False)
        embed.add_field(name="可於下方討論，但請勿公布答案", value="", inline=False)
        await ctx.respond(embed=embed,view=self.ctfView())

    @ctf_commands.command(description="ball.") # this decorator makes a slash command
    async def ping(self,ctx): # a slash command will be created with the name "ping"
        await ctx.respond("Pong!")

    self.bot.add_application_command(ctf_commands)

def setup(bot):
    bot.add_cog(ctf(bot))