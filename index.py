import discord
import firebase_admin
from discord import commands
from firebase_admin import credentials
from firebase_admin import db
import string
import random
from datetime import date


bot = discord.Bot(intents=discord.Intents().all())
cred = credentials.Certificate("./amail-3dd96-firebase-adminsdk-aiuab-854aa11a67.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://amail-3dd96-default-rtdb.asia-southeast1.firebasedatabase.app'
})
data = db.reference()


class GetPassword(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="아이디 설정",
                placeholder="ReMail 로그인 시 사용할 아이디를 여기에 입력하세요.",
            ),

            discord.ui.InputText(
                label="비밀번호 설정",
                placeholder="ReMail 로그인 시 사용할 비밀번호를 여기에 입력하세요.",
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        # self.children[0].value 이 입력한 값
        today = date.today()
        today = today.strftime('%Y.%m.%d')
        complete = discord.Embed(title='메일 등록 완료', description='', colour=discord.Colour.blurple())
        complete.add_field(name='메일 주소', value=f'{self.children[0].value}@remail', inline=False)
        complete.add_field(name='비밀번호', value='방금 작성하셨던 것이 비밀번호입니다.', inline=False)
        complete.set_footer(text='메일 주소와 비밀번호는 로그인 시 사용됩니다.')
        dir = db.reference('aMail/ID/')
        dir.update({str(self.children[0].value): f'{str(interaction.user.id)}/{today}'})
        dir = db.reference("aMail/People/")
        dir.update({str(interaction.user.id): str(self.children[0].value)})
        await interaction.response.send_message(embed=complete)


class RandomKey:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    def create(self, length=10):
        result = ""
        string_pool = string.ascii_letters + string.digits
        for i in range(length):
            result += random.choice(string_pool)
        return result

    def upload(self, the_key):
        if the_key is None:
            return False
        else:
            data = db.reference('aMail/RandomKeys/')
            data.update({'RandomKeys': {str(the_key): str(the_key)}})
            return True


@bot.slash_command(name='아이디')
async def hello(ctx):
    await ctx.respond(f"{ctx.author.name}님의 아이디는 `{ctx.author.id}`입니다.")


@bot.slash_command(name='메일생성')
async def signup(ctx: commands.context):
    dir = db.reference().get()
    if dir['aMail']['People'].get(str(ctx.author.id)) is None:
        modal = GetPassword(title="메일 생성하기")
        await ctx.send_modal(modal)
    else:
        return await ctx.respond('이미 메일이 있습니다.')


bot.run("token")