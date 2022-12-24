import discord
import firebase_admin
from discord import commands
from discord.ext import commands, pages
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


def error_embed(des:str):
    embed = discord.Embed(title='오류', description=des, colour=discord.Colour.red())
    return embed


def db_check(user_id: int):
    dir = db.reference().get()
    if dir['aMail']['People'].get(str(user_id)) is None:
        return False
    else:
        return True


class GetPassword(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="아이디 설정",
                placeholder="aMail 로그인 시 사용할 아이디를 여기에 입력하세요.",
            ),

            discord.ui.InputText(
                label="비밀번호 설정",
                placeholder="aMail 로그인 시 사용할 비밀번호를 여기에 입력하세요.",
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        # self.children[0].value 이 입력한 값
        if str(self.children[0].value).isdigit():
            return await interaction.response.send_message(embed=error_embed('아이디는 숫자로 설정할 수 없습니다.'))
        today = date.today()
        today = today.strftime('%Y.%m.%d')
        complete = discord.Embed(title='메일 등록 완료', description='', colour=discord.Colour.blurple())
        complete.add_field(name='메일 주소', value=f'{self.children[0].value}@aemail', inline=False)
        complete.add_field(name='비밀번호', value='방금 작성하셨던 것이 비밀번호입니다.', inline=False)
        complete.set_footer(text='메일 주소와 비밀번호는 로그인 시 사용됩니다.')
        dir = db.reference('aMail/ID/')
        dir.update({str(self.children[0].value): f'{str(interaction.user.id)}/{str(self.children[1].value)}'})
        dir = db.reference("aMail/People/")
        dir.update({str(interaction.user.id): str(self.children[0].value)})
        dir = db.reference("aMail/JoinedAt/")
        dir.update({str(self.children[0].value): {today}})
        await interaction.response.send_message(embed=complete)


class WriteMail(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="받는 사람 설정",
                placeholder="aMail 아이디를 여기에 입력하세요. \n(디스코드 아이디 입력불가)",
            ),

            discord.ui.InputText(
                label="메일 제목 설정",
                placeholder="메일의 제목을 여기에 입력하세요.",
            ),

            discord.ui.InputText(
                label="메일 내용 입력",
                placeholder="메일의 내용을 여기에 입력하세요.",
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction: discord.Interaction):
        dir = db.reference().get()
        if dir['aMail']['ID'].get(str(self.children[0].value)) is None:
            return await interaction.channel.send(embed=error_embed('메일 수신자가 aMail 아이디를 생성하지 않았습니다.'))
        today = date.today()
        today = today.strftime('%Y.%m.%d')
        randomkey = create(10)
        upload(randomkey)
        sender = dir['aMail']['People'].get(str(interaction.user.id))
        to = dir['aMail']['ID'].get(str(self.children[0].value)).split('/')[0]
        mails = db.reference('aMail/Mails')
        mails.update({randomkey: {
            "Content": str(self.children[2].value),
            "From": f"{interaction.user.id}/{sender}",
            "To": f"{to}/{str(self.children[0].value)}",
            "Title": f"{self.children[1].value}",
            "WroteAt": f"{today}"
        }})
        # 사용자 DM으로 보내는 embed
        to_dm = discord.Embed(title='메일 전송 완료', description='', colour=discord.Colour.blurple())
        to_dm.add_field(name='받는 사람', value=f'{self.children[0].value}@amail', inline=False)
        to_dm.add_field(name='메일 제목', value=f'{self.children[1].value}', inline=False)
        to_dm.add_field(name='메일 내용', value=f'{self.children[2].value}', inline=False)
        to_dm.set_footer(text=f'발송 시기 : {today}')
        await interaction.user.send(embed=to_dm)

        #채널로 보내는 embed
        to_channel = discord.Embed(title='메일 전송 완료',
                                   description='메일이 전송되었습니다.\n메일 정보는 DM으로 전송되었습니다.',
                                   colour=discord.Colour.blurple())
        to_channel.set_footer(text=f'발송 시기 : {today}')
        await interaction.response.send_message(embed=to_channel)


def create(length=10):
    result = ""
    string_pool = string.ascii_letters + string.digits
    for i in range(length):
        result += random.choice(string_pool)
    return result


def upload(the_key):
    if the_key is None:
        return False
    else:
        data = db.reference('aMail/RandomKeys/')
        data.update({str(the_key): str(the_key)})
        return True


@bot.slash_command(name='메일생성')
async def signup(ctx: commands.context):
    if not db_check(user_id=ctx.author.id):
        modal = GetPassword(title="메일 생성하기")
        await ctx.send_modal(modal)
    else:
        return await ctx.respond(embed=error_embed('이미 메일이 존재합니다.'))


@bot.slash_command(name='메일작성')
async def write_mail(ctx: commands.context):
    if db_check(ctx.author.id):
        modal = WriteMail(title='메일 작성하기')
        await ctx.send_modal(modal)
    else:
        await ctx.respond(embed=error_embed('등록된 메일이 없습니다.\n`/메일생성` 커맨드로 메일을 생성하여주세요.'))


@bot.slash_command(name='메일보기')
async def check_mymails(ctx: commands.context):
    if db_check(ctx.author.id):
        mails_list = []
        data = db.reference().get()
        randomkeys = data['aMail']['RandomKeys']

        for i in randomkeys:  # 나에게 전송된 메일의 RandomKey들을 리스트에 저장하는 과정
            if data['aMail']['Mails'][i]['To'].split("/")[0] == str(ctx.author.id):
                mails_list.append(i)
            else:
                pass
        page = []  # 메일 리스트를 보여줄 Embed list
        for i in mails_list:  # mails_list는 randomkey가 저장되어있음
            data = db.reference().get()
            the_mail = data['aMail']['Mails'][i]
            sender_id = the_mail["From"].split('/')[0]
            sender_mail_id = the_mail['From'].split('/')[1]
            sender = await bot.fetch_user(int(sender_id))
            embed = discord.Embed(
                title=the_mail['Title'],
                description=f'보낸 사람: {sender.name}#{sender.discriminator}({sender_mail_id})\n받는 사람 : 나',
                colour=discord.Colour.blurple()
            )
            embed.add_field(
                name='내용',
                value=f'{the_mail["Content"]}',
                inline=False
            )
            embed.add_field(
                name='메일 고유 키',
                value=f'{i} / 고유 키는 메일을 삭제 할 때 이용됩니다.',
                inline=False
            )
            embed.set_footer(text=f'작성 날짜 : {the_mail["WroteAt"]}')
            page.append(embed)

        paginator = pages.Paginator(pages=page)
        await paginator.respond(ctx.interaction, ephemeral=False)

    else:
        await ctx.respond(embed=error_embed('등록된 메일이 없습니다.\n`/메일생성` 커맨드로 메일을 생성하여주세요.'))


@bot.slash_command(name='아이디찾기')
async def find_my_id(ctx: commands.context):
    if db_check(ctx.author.id):
        data = db.reference().get()
        embed = discord.Embed(
            title=f'{ctx.author.name}님의 아이디',
            description=f'{ctx.author.name}님의 아이디는 `{data["aMail"]["People"][str(ctx.author.id)]}`입니다.',
            colour=discord.Colour.blurple()
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(embed=error_embed('등록된 메일이 없습니다.\n`/메일생성` 커맨드로 메일을 생성하여주세요.'))


@bot.slash_command(name='비밀번호찾기')
async def find_password(ctx: commands.context):
    if db_check(ctx.author.id):
        data = db.reference().get()
        mail_id = data["aMail"]["People"][str(ctx.author.id)]

        embed = discord.Embed(
            title=f'{ctx.author.name}님의 비밀번호',
            description=f'{ctx.author.name}님의 비밀번호는 ||{data["aMail"]["ID"][mail_id].split("/")[1]}||입니다.',
            colour=discord.Colour.blurple()
        )
        await ctx.author.send(embed=embed)

        embed = discord.Embed(
            title=f'{ctx.author.name}님의 비밀번호',
            description=f"{ctx.author.name}님의 비밀번호가 DM으로 전송되었습니다.",
            colour=discord.Colour.blurple()
        )
        await ctx.respond(embed=embed)
    else:
        await ctx.respond(embed=error_embed('등록된 메일이 없습니다.\n`/메일생성` 커맨드로 메일을 생성하여주세요.'))


bot.run("MTA1NjA2OTEwMDY3OTQ4MzUxMw.G3ozwz.1aZDbm-oKjsQ062joB2hxkCWmoFBZvg6VBqjt8")
