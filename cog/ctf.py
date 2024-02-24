import discord
from build.build import build
from discord.ext import commands

class ctf(build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.ctfView())

    #成員身分組
    class ctfView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None) # timeout of the view must be set to None
        @discord.ui.button(label="回報 Flag",style=discord.ButtonStyle.blurple,emoji="🚩",custom_id="new_ctf")
        async def button_callback_1(self,button,interaction):
            await interaction.response.send_message("已收到 flag`",ephemeral=True)
            
    @discord.slash_command()
    async def create_ctf(self,ctx):
        if ctx.author.guild_permissions.administrator:
            embed=discord.Embed(color=0x16b0fe)
            embed.set_thumbnail(url="https://emojiisland.com/cdn/shop/products/Nerd_with_Glasses_Emoji_2a8485bc-f136-4156-9af6-297d8522d8d1_large.png?v=1571606036")
            embed.add_field(name="哈囉 點一下", value="  ", inline=False)
            await ctx.respond(embed=embed,view=self.ctfView())





def setup(bot):
    bot.add_cog(ctf(bot))