import discord
import asyncio
import cloudscraper  # dùng để vượt Cloudflare
import os

TOKEN = os.getenv("DISCORD_TOKEN")  # token sẽ lưu trong biến môi trường
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID kênh Discord của bạn
URL = "https://hoang.cloud/status_trial_ugphone"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

last_status = None

async def check_trial():
    global last_status
    scraper = cloudscraper.create_scraper()  # giúp bypass Cloudflare

    while True:
        try:
            response = scraper.get(URL, timeout=15)
            text = response.text.strip()

            # Kiểm tra sự thay đổi nội dung
            if last_status != text:
                last_status = text

                if "trial" in text.lower():
                    channel = client.get_channel(CHANNEL_ID)
                    await channel.send(
                        f"📱 **Có thể có máy trial mới!**\n```{text[:1000]}```\n🔗 {URL}"
                    )
                else:
                    print("Chưa có trial mới.")
        except Exception as e:
            print("Lỗi:", e)

        await asyncio.sleep(180)  # kiểm tra lại sau 3 phút

@client.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập: {client.user}")
    client.loop.create_task(check_trial())

client.run(TOKEN)