import os
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

# 建立 Web Server 通過 Render 健康檢查
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

# 設定 Bot 權限
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=["!", "！"], intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot successfully logged in as {bot.user}")

@bot.command(name="join", aliases=["掛機", "進來"])
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("❌ 你需要先進入一個語音頻道！")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(f"✅ 已進入語音頻道：**{channel.name}** 開始掛機！")

@bot.command(name="leave", aliases=["退出", "離開"])
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 已離開語音頻道")

async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ 錯誤：找不到 BOT_TOKEN！")
        return
    await start_web_server()
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())