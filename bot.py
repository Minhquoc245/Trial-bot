import discord
from discord.ext import commands, tasks
import cloudscraper
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

scraper = cloudscraper.create_scraper()
url = "https://hoang.cloud/status_trial_ugphone"

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập thành {bot.user}")
    check_trial_status.start()

def get_trial_status():
    try:
        html = scraper.get(url).text
        status = {
            "Singapore": "🔴",
            "Hong Kong": "🔴",
            "Japan": "🔴",
            "Germany": "🔴",
            "America": "🔴"
        }

        # Bạn có thể sửa logic này nếu web có định dạng khác
        if "Singapore ✅" in html: status["Singapore"] = "🟢"
        if "Hong Kong ✅" in html: status["Hong Kong"] = "🟢"
        if "Japan ✅" in html: status["Japan"] = "🟢"
        if "Germany ✅" in html: status["Germany"] = "🟢"
        if "America ✅" in html: status["America"] = "🟢"

        return status
    except Exception as e:
        print("Lỗi lấy dữ liệu:", e)
        return None

def create_embed(status):
    embed = discord.Embed(
        title="📱 Trạng thái UGPhone Trial",
        color=discord.Color.blue()
    )

    description = ""
    for country, icon in status.items():
        flag = {
            "Singapore": "🇸🇬",
            "Hong Kong": "🇭🇰",
            "Japan": "🇯🇵",
            "Germany": "🇩🇪",
            "America": "🇺🇸"
        }[country]
        description += f"{flag} | {country} - {icon}\n"

    description += "\n**Chú thích**\n🟢 Còn máy\n🔴 Hết máy"
    embed.description = description
    embed.set_footer(text="⏰ Bot tự động cập nhật mỗi 5 phút")
    return embed

@tasks.loop(minutes=5)
async def check_trial_status():
    channel = bot.get_channel(CHANNEL_ID)
    status = get_trial_status()
    if status:
        embed = create_embed(status)
        await channel.send(embed=embed)

@bot.command()
async def status(ctx):
    status = get_trial_status()
    if status:
        embed = create_embed(status)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Không thể lấy trạng thái, thử lại sau.")

bot.run(os.getenv("DISCORD_TOKEN"))