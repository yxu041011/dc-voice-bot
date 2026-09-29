import os
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

# 1. 建立 Web Server 通過 Render 健康檢查
async def handle_ping(request):
    return web.Response(text="Bot is active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server running on port {port}", flush=True)

# 2. 設定機器人權限 (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix=["!", "！"], intents=intents)

@bot.event
async def on_ready():
    print(f"----------------------------------------", flush=True)
    print(f"✅ 機器人成功登入：{bot.user} (ID: {bot.user.id})", flush=True)
    print(f"----------------------------------------", flush=True)
    await bot.change_presence(activity=discord.Game(name="24H 語音掛機中 | !join"))

@bot.command(name="join", aliases=["掛機", "進來"])
async def join(ctx):
    # 嘗試抓取發送者的語音頻道狀態
    author_member = ctx.guild.get_member(ctx.author.id) if ctx.guild else ctx.author
    
    if not author_member or not author_member.voice or not author_member.voice.channel:
        await ctx.send("❌ 你需要先進入一個語音頻道！")
        return
    
    channel = author_member.voice.channel
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"✅ 已移動至語音頻道：**{channel.name}**")
        else:
            await channel.connect()
            await ctx.send(f"✅ 已進入語音頻道：**{channel.name}** 開始掛機！")
    except Exception as e:
        await ctx.send(f"❌ 進入語音頻道失敗：`{e}`")
        print(f"❌ Voice connect error: {e}", flush=True)

@bot.command(name="leave", aliases=["退出", "離開"])
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 已離開語音頻道")
    else:
        await ctx.send("❌ 機器人目前不在任何語音頻道中！")

# 3. 啟動入口與錯誤排查
async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ 錯誤：Render 環境變數中完全找不到 BOT_TOKEN！", flush=True)
        return
    
    print("🚀 正在啟動 Web Server...", flush=True)
    await start_web_server()
    
    print("🔑 正在嘗試使用 BOT_TOKEN 登入 Discord...", flush=True)
    try:
        await bot.start(token)
    except discord.errors.LoginFailure:
        print("❌ 登入失敗：BOT_TOKEN 無效或已被重置，請到 Developer Portal 重新複製！", flush=True)
    except Exception as e:
        print(f"❌ 啟動遇到未預期錯誤：{e}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())