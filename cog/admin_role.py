# Third-party imports
import discord
from discord.ext import commands
# Local imports
from build.build import Build

class AdminRole(Build):
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.RoleView())

    # 成員身分組
    class RoleView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout = None) # timeout of the view must be set to None

        @discord.ui.button(
            label = "領取身分組",
            style = discord.ButtonStyle.blurple,
            emoji = "🥇",
            custom_id = "take_the_role"
        )
        # pylint: disable-next = unused-argument
        async def button_callback_1(self, button, interaction):
            role = discord.utils.get(interaction.guild.roles, name = "ADMIN")
            await interaction.user.add_roles(role)
            await interaction.response.send_message("已領取身分組 `ヾ(≧▽≦*)o`", ephemeral = True)

    @discord.slash_command()
    async def create_role_button(self, ctx):
        if ctx.author.guild_permissions.administrator:
            embed = discord.Embed(color = 0x16b0fe)
            # pylint: disable-next = line-too-long
            embed.set_thumbnail(url = "https://emojiisland.com/cdn/shop/products/Nerd_with_Glasses_Emoji_2a8485bc-f136-4156-9af6-297d8522d8d1_large.png?v=1571606036")
            embed.add_field(name = "哈囉 點一下", value = "  ", inline = False)
            await ctx.respond(embed = embed, view = self.RoleView())

def setup(bot):
    bot.add_cog(AdminRole(bot))
