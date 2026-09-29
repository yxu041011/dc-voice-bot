import os
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

# 設定完整的 Intents 讓機器人能精準讀取成員語音狀態
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix=["!", "！"], intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot successfully logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="24H 語音掛機中 | !join"))

@bot.command(name="join", aliases=["掛機", "進來"])
async def join(ctx):
    # 嘗試抓取發送者的語音狀態
    user_voice = ctx.author.voice or (ctx.guild.get_member(ctx.author.id).voice if ctx.guild else None)
    
    if not user_voice or not user_voice.channel:
        await ctx.send("❌ 你需要先進入一個語音頻道！")
        return
    
    channel = user_voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"✅ 已移動至語音頻道：**{channel.name}**")
    else:
        await channel.connect()
        await ctx.send(f"✅ 已進入語音頻道：**{channel.name}** 開始掛機！")

@bot.command(name="leave", aliases=["退出", "離開"])
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 已離開語音頻道")
    else:
        await ctx.send("❌ 機器人目前不在任何語音頻道中！")

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ 錯誤：找不到 BOT_TOKEN 環境變數！")
        return
    
    await start_web_server()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())