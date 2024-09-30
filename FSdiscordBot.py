import discord
from discord.ext import commands, tasks
import serial
import dotenv, os
import asyncio
import sys
token = str(os.getenv("TOKEN"))
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# ser = serial.Serial('COM3')
ser = serial.Serial()
class buttonView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.self_feeding = discord.ui.Button(emoji="💧",label="수동 급수", style=discord.ButtonStyle.primary)
        self.self_feeding.callback = self.self_feeding_callback
        self.add_item(self.self_feeding)
        
    async def self_feeding_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("버튼이 클릭되었습니다!", ephemeral=True)
        await ser.write(b"feed")
    def disabling(self):
        self.self_feeding.disabled = True
    def abling(self):
        self.self_feeding.disabled = False
class DropView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MyDropdown())

class MyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='10 sec(for test)', description='To test, short term'),
            discord.SelectOption(label='15 min', description='Feeding in 15-minute cycles'),
            discord.SelectOption(label='30 min', description='Feeding in 30-minute cycles'),
            discord.SelectOption(label='1 hour', description='Feeding in a hour cycles', default=True),
            discord.SelectOption(label='2 hour', description='Feeding in 2-hour cycles'),
            discord.SelectOption(label='1 day', description='Feeding in a day cycles')
        ]
        super().__init__(placeholder='Choose an cycles', max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # await ser.write(b"changecycle")
        # selected = self.values[0].encode()
        # await ser.write(selected)
        await interaction.response.send_message(f'You selected: {self.values[0]}', ephemeral=True)
        

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online")
    
@bot.command()
async def sendbtn(ctx):
    global BV
    channel_id = 1288751209179512875
    channel = bot.get_channel(channel_id)
    BV = buttonView()  #버튼포함 view 인스턴스 생성
    embed = discord.Embed(
        color=discord.Color.dark_teal()
    )
    embed.add_field(name="온도", value="27.87°C", inline=False) #잔여 물
    embed.add_field(name="온도", value="27.87°C", inline=False) #다음 주기까지 남은시간 / 현재 주기
    embed.add_field(name="전에 준 시간!", value="27.87°C", inline=False) #다음 주기까지 남은시간 / 현재 주기
    
    if channel:
        await channel.send(view=BV, embed=embed)  # 입력된 메시지를 해당 채널에 보냄
        await ctx.send(f"메시지가 <#{channel.id}>에 전송되었습니다.")  # 명령어를 입력한 채팅에 피드백을 전송
    else:
        await ctx.send(f"채널 {channel_id}를 찾을 수 없습니다.")
@bot.command()
async def senddrop(ctx):
    global DV
    channel_id = 1288751209179512875
    channel = bot.get_channel(channel_id)
    DV = DropView()  #버튼포함 view 인스턴스 생성
    if channel:
        await channel.send("주기설정: ",view=DV)  # 입력된 메시지를 해당 채널에 보냄
        await ctx.send(f"메시지가 <#{channel.id}>에 전송되었습니다.")  # 명령어를 입력한 채팅에 피드백을 전송
    else:
        await ctx.send(f"채널 {channel_id}를 찾을 수 없습니다.")

@tasks.loop(seconds=2)
async def event_check():
    if ser.in_waiting > 0:  # 수신할 데이터가 있으면
        data_bytes = ser.readline()  # 데이터를 한 줄 읽음 (줄 바꿈 기준)
        data_str = data_bytes.decode('utf-8').rstrip()  # 데이터를 'utf-8'로 디코딩하여 문자열로 변환하고 개행 문자 제거
        if data_str == "forbidFeeding":
            BV.disabling()
        elif data_str == "allowFeeding":
            BV.abling()

bot.run(token)