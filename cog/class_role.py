import discord
from build.build import build
from discord.ext import commands
import json
import os
def getCLS():
    try:
        with open("./database/clas.json", "r") as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def search_data(code):
    data = getCLS()
    if code in data:
        return data[code]
    else:
        return False

def add_data(code, new_data):
    data = getCLS()
    data[code] = new_data
    with open(f'{os.getcwd()}/DataBase/clas.json', 'w') as file:
        json.dump(data, file, indent=2,ensure_ascii=False)



class class_role(build):

    class token_verify_button(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
        @discord.ui.button(label="輸入課程代碼",style=discord.ButtonStyle.blurple,emoji="🏷️",custom_id="button")
        async def button_callback(self, button, interaction):
            class token_modal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)

                    self.input_field = discord.ui.InputText(label="課程代碼輸入")
                    self.add_item(self.input_field)

                async def callback(self, interaction: discord.Interaction):
                    user_code = self.input_field.value
                    
                    if search_data(user_code):
                        data = getCLS()
                        role = discord.utils.get(interaction.guild.roles, name=data[user_code]["name"])
                        await interaction.user.add_roles(role)
                        role_name = data[user_code]["name"]
                        theme = data[user_code]["theme"]
                        teacher = data[user_code]["teacher"]
                        time = data[user_code]["time"]
                        #embed
                        embed=discord.Embed(color=0x3dbd46)
                        embed.set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/47298/check-mark-button-emoji-clipart-md.png")
                        embed.add_field(name=f"已領取{role_name}身分組", value=f" 課程主題: {theme}", inline=False)
                        embed.add_field(name=f"用戶: {interaction.user.name}", value=f" 講師: {teacher}", inline=False)
                        embed.set_footer(text=f"課程時間: {time}")
                        #
                        await interaction.response.send_message(embed=embed,ephemeral=True)
                    else:
                        embed=discord.Embed(color=0xbd3d3d)
                        embed.set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/47329/cross-mark-button-emoji-clipart-md.png")
                        embed.add_field(name="領取失敗", value="", inline=False)
                        embed.add_field(name=f"用戶: {interaction.user.name}", value="請重新確認課程代碼", inline=False)
                        embed.set_footer(text=" ")
                        await interaction.response.send_message(embed=embed,ephemeral=True)
            await interaction.response.send_modal(token_modal(title="請輸入課程代碼"))

    @discord.slash_command(description="發送課程代碼兌換鈕")
    async def send_modal(self,ctx):
        if ctx.author.guild_permissions.administrator:
            embed=discord.Embed(color=0x4be1ec)
            embed.set_thumbnail(url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/56531/label-emoji-clipart-md.png")
            embed.add_field(name="點下方按鈕輸入token", value="", inline=False)
            embed.add_field(name="領取課程身分組!", value="", inline=False)
            await ctx.respond(embed=embed,view=self.token_verify_button())
        
    @discord.slash_command(description="新增主題課程")
    async def add_class(self, ctx, class_code: str, name: str, theme: str, teacher: str, time: str):
        if ctx.author.guild_permissions.administrator:
            d = {
                "name": name,
                "theme": theme,
                "teacher": teacher,
                "time": time
            }
            add_data(class_code, d)
            await ctx.respond(f"已添加 {name} 至 JSON 中 主題: {theme}, 講師: {teacher}, 時間: {time}")

        

def setup(bot):
    bot.add_cog(class_role(bot))