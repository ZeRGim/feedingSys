import discord
from discord.ext import commands, tasks
from discord.ui.item import Item
import serial
import dotenv, os
import asyncio
token = str(os.getenv("TOKEN"))
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ser = serial.Serial('COM3')
ser = serial.Serial()

temper = 0
humid = 0
water = 0
curfeed = 0
curhr = 0
curmin =0
cursec = 0
class buttonView(discord.ui.View):
    def __init__(self, *items: Item, timeout: float | None = None, disable_on_timeout: bool = False):
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
        self.self_feeding = discord.ui.Button(emoji="💧",label="수동 급수", style=discord.ButtonStyle.primary, custom_id="selffeed")
        self.self_feeding.callback = self.self_feeding_callback
        self.add_item(self.self_feeding)
        
    async def self_feeding_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("급수!", ephemeral=True)
        ser.write(b"feed")
    def disabling(self):
        self.self_feeding.disabled = True
    def abling(self):
        self.self_feeding.disabled = False
# class DropView(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.add_item(MyDropdown())

# class MyDropdown(discord.ui.Select):
#     def __init__(self):
#         options = [
#             discord.SelectOption(label='10', description='10sec'),
#             discord.SelectOption(label='900', description='Feeding in 15-minute cycles'),
#             discord.SelectOption(label='1800', description='Feeding in 30-minute cycles'),
#             discord.SelectOption(label='3600', description='Feeding in a hour cycles', default=True),
#             discord.SelectOption(label='7200', description='Feeding in 2-hour cycles'),
#             discord.SelectOption(label='86400', description='Feeding in a day cycles')
#         ]
#         super().__init__(placeholder='Choose an cycles', max_values=1, min_values=1, options=options,custom_id="cycle")

#     async def callback(self, interaction: discord.Interaction):
#         await ser.write(b"changecycle")
#         selected = self.values[0].encode()
#         await ser.write(selected)
#         await interaction.response.send_message(f'You selected: {self.values[0]}', ephemeral=True)
class DropView(discord.ui.View):
    def __init__(self, *items: Item, timeout: float | None = None, disable_on_timeout: bool = False):
        super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
    @discord.ui.select(
        placeholder='Choose an cycles',
        max_values=1, 
        min_values=1,
        custom_id="cycle",
        options = [
            discord.SelectOption(label='10', description='To test, short term'),
            discord.SelectOption(label='15', description='To test, short term'),
            discord.SelectOption(label='30', description='To test, short term'),
            discord.SelectOption(label='900', description='Feeding in 15-minute cycles'),
            discord.SelectOption(label='1800', description='Feeding in 30-minute cycles'),
            discord.SelectOption(label='3600', description='Feeding in a hour cycles', default=True),
            discord.SelectOption(label='7200', description='Feeding in 2-hour cycles'),
            discord.SelectOption(label='86400', description='Feeding in a day cycles')
        ]
    )
    async def select_callback(self,select: discord.ui.Select, interaction: discord.Interaction):
        ser.write(b"changecycle")
        await asyncio.sleep(0.1)
        # selected = select.values[0].encode()
        ser.write(int(select.values[0]))
        await interaction.response.send_message(f'주기: {select.values[0]}초', ephemeral=True)
        

@bot.command()
async def 비활(ctx):
    await disa(int(os.getenv("CHANNEL_ID")),int(os.getenv("MESSAGE_ID")))
@bot.command()
async def 재활(ctx):
    await ab(int(os.getenv("CHANNEL_ID")),int(os.getenv("MESSAGE_ID")))

@bot.event
async def on_ready():
    bot.add_view(DropView())
    bot.add_view(buttonView())
    event_check.start()
    print(f"{bot.user} is ready and online")

@bot.command()
async def sendbtn(ctx):
    channel_id = int(os.getenv("CHANNEL_ID"))
    channel = bot.get_channel(channel_id)
    BV = buttonView()  #버튼포함 view 인스턴스 생성
    embed = discord.Embed(
        color=discord.Color.dark_teal()
    )
    embed.add_field(name="온도", value=temper, inline=False) #잔여 물
    embed.add_field(name="습도", value=humid, inline=False) #다음 주기까지 남은시간 / 현재 주기
    embed.add_field(name="남은 물 양", value=water, inline=False) #다음 주기까지 남은시간 / 현재 주기
    embed.add_field(name="전에 준 시간!", value=f"2024-10-04 {curhr}:{curmin}:{cursec}", inline=False) #다음 주기까지 남은시간 / 현재 주기
    
    if channel:
        await channel.send(view=BV, embed=embed)  # 입력된 메시지를 해당 채널에 보냄
        await ctx.send(f"메시지가 <#{channel.id}>에 전송되었습니다.")  # 명령어를 입력한 채팅에 피드백을 전송
    else:
        await ctx.send(f"채널 {channel_id}를 찾을 수 없습니다.")
@bot.command()
async def senddrop(ctx):
    global DV
    channel_id = int(os.getenv("CHANNEL_ID"))
    channel = bot.get_channel(channel_id)
    DV = DropView()  #버튼포함 view 인스턴스 생성
    if channel:
        await channel.send("주기설정: ",view=DV)  # 입력된 메시지를 해당 채널에 보냄
        await ctx.send(f"메시지가 <#{channel.id}>에 전송되었습니다.")  # 명령어를 입력한 채팅에 피드백을 전송
    else:
        await ctx.send(f"채널 {channel_id}를 찾을 수 없습니다.")

async def gangsin(chid:int, meid:int):
    channel = bot.get_channel(chid)
    msg = await channel.fetch_message(meid)
    embed = discord.Embed(
        color=discord.Color.dark_teal()
    )
    embed.add_field(name="온도", value=temper, inline=False) #잔여 물
    embed.add_field(name="습도", value=humid, inline=False) #다음 주기까지 남은시간 / 현재 주기
    embed.add_field(name="남은 물 양", value=water, inline=False) #다음 주기까지 남은시간 / 현재 주기
    embed.add_field(name="전에 준 시간!", value=f"2024-10-04 {curhr}:{curmin}:{cursec}", inline=False) #다음 주기까지 남은시간 / 현재 주기
    
    await msg.edit(embed=embed)

async def disa(chid:int, meid:int):
    channel = bot.get_channel(chid)
    msg = await channel.fetch_message(meid)
    BV = buttonView()
    BV.disabling()
    await msg.edit(view=BV)
async def ab(chid:int, meid:int):
    channel = bot.get_channel(chid)
    msg = await channel.fetch_message(meid)
    BV = buttonView()
    BV.abling()
    await msg.edit(view=BV)
@bot.command()
async def gang(ctx):
    await gangsin(int(os.getenv("CHANNEL_ID")), int(os.getenv("MESSAGE_ID")))

@tasks.loop(seconds=2)
async def event_check():
    global temper
    global humid    
    global water
    global curfeed
    global curhr
    global curmin
    global cursec
    while ser.in_waiting > 0:  # 수신할 데이터가 있으면
        data_bytes = ser.readline()  # 데이터를 한 줄 읽음 (줄 바꿈 기준)
        data_str = data_bytes.decode('utf-8').rstrip()  # 데이터를 'utf-8'로 디코딩하여 문자열로 변환하고 개행 문자 제거
        if data_str == "forbidFeeding":
            await disa(int(os.getenv("CHANNEL_ID")),int(os.getenv("MESSAGE_ID")))
        elif data_str == "allowFeeding":
            await ab(int(os.getenv("CHANNEL_ID")),int(os.getenv("MESSAGE_ID")))
        elif "tem" in data_str:
            temper = float(data_str[3:])
        elif "hum" in data_str:
            humid = float(data_str[3:])
        elif "wat" in data_str: 
            water = int(data_str[3:])
        elif "cur" in data_str:
            curfeed = int(data_str[3:])
            curhr = curfeed//(60*60)
            curfeed = curfeed%(60*60)
            curmin = curfeed//(60)
            curfeed = curfeed%60
            cursec = curfeed
            await gangsin(int(os.getenv("CHANNEL_ID")), int(os.getenv("MESSAGE_ID")))

bot.run(token)