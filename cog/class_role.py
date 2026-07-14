# Future statements
from __future__ import annotations

# Standard imports
import json
import os
import typing

# Third-party imports
import discord
import discord.ext.commands

# Local imports
import build.build


def get_courses():
    try:
        with open(
            f"{os.getcwd()}/database/courses.json", "r", encoding="utf-8"
        ) as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def search_data(code):
    data = get_courses()
    if code in data:
        return data[code]

    return False


def add_data(code, new_data):
    data = get_courses()
    data[code] = new_data
    with open(f"{os.getcwd()}/database/courses.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


class ClassRole(build.build.Build):
    @discord.ext.commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.TokenVerifyButton())

    class TokenVerifyButton(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(
            label="輸入課程代碼",
            style=discord.ButtonStyle.blurple,
            emoji="🏷️",
            custom_id="button",
        )
        # pylint: disable-next = unused-argument
        async def button_callback(self, button, interaction):
            class TokenModal(discord.ui.Modal):
                def __init__(self, *args, **kwargs) -> None:
                    super().__init__(*args, **kwargs)

                    self.input_field = discord.ui.InputText(label="請輸入課程代碼")
                    self.add_item(self.input_field)

                async def callback(self, interaction: discord.Interaction):
                    user_code = self.input_field.value

                    if search_data(user_code):
                        data = get_courses()
                        role = discord.utils.get(
                            interaction.guild.roles, name=data[user_code]["name"]
                        )
                        await interaction.user.add_roles(role)
                        role_name = data[user_code]["name"]
                        theme = data[user_code]["theme"]
                        teacher = data[user_code]["teacher"]
                        time = data[user_code]["time"]
                        # embed
                        embed = discord.Embed(color=0x3DBD46)
                        # pylint: disable-next = line-too-long
                        embed.set_thumbnail(
                            url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/47298/check-mark-button-emoji-clipart-md.png"
                        )
                        embed.add_field(
                            name=f"已領取{role_name}身分組",
                            value=f" 課程主題：{theme}",
                            inline=False,
                        )
                        embed.add_field(
                            name=f"使用者：{interaction.user.name}",
                            value=f" 講師：{teacher}",
                            inline=False,
                        )
                        embed.set_footer(text=f"課程時間：{time}")
                        #
                        await interaction.response.send_message(
                            embed=embed, ephemeral=True
                        )
                    else:
                        embed = discord.Embed(color=0xBD3D3D)
                        # pylint: disable-next = line-too-long
                        embed.set_thumbnail(
                            url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/47329/cross-mark-button-emoji-clipart-md.png"
                        )
                        embed.add_field(name="領取失敗", value="", inline=False)
                        embed.add_field(
                            name=f"使用者：{interaction.user.name}",
                            value="請重新確認課程代碼",
                            inline=False,
                        )
                        embed.set_footer(text=" ")
                        await interaction.response.send_message(
                            embed=embed, ephemeral=True
                        )

                def clear_items(self) -> typing.Self:
                    """
                    Clear all InputText from the modal.

                    This should be implemented by the parent class in Pycord.
                    However, we're now fixing it here as a workaround.
                    """

                    try:
                        self._children.clear()
                        self.__weights.clear()
                    except ValueError:
                        pass

                    return self

            await interaction.response.send_modal(TokenModal(title="請輸入課程代碼"))

    @discord.slash_command(description="發送課程代碼兌換鈕")
    async def send_modal(self, ctx):
        if ctx.author.guild_permissions.administrator:
            embed = discord.Embed(color=0x4BE1EC)
            # pylint: disable-next = line-too-long
            embed.set_thumbnail(
                url="https://creazilla-store.fra1.digitaloceanspaces.com/emojis/56531/label-emoji-clipart-md.png"
            )
            embed.add_field(name="點下方按鈕輸入token", value="", inline=False)
            embed.add_field(name="領取課程身分組！", value="", inline=False)
            await ctx.send(embed=embed, view=self.TokenVerifyButton())

    @discord.slash_command(description="新增主題課程")
    # pylint: disable-next = too-many-arguments, too-many-positional-arguments
    async def add_class(
        self, ctx, class_code: str, name: str, theme: str, teacher: str, time: str
    ):
        if ctx.author.guild_permissions.administrator:
            d = {"name": name, "theme": theme, "teacher": teacher, "time": time}
            add_data(class_code, d)
            await ctx.respond(
                f"已將{name}新增至 JSON；主題：{theme}，講師：{teacher}，時間：{time}"
            )


def setup(bot: discord.Bot):
    bot.add_cog(ClassRole(bot))
