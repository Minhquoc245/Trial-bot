import discord
from discord.ext import tasks
import cloudscraper
import datetime
import os

# === LẤY TOKEN VÀ CHANNEL_ID TỪ ENVIRONMENT VARIABLES (Render.com) ===
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# === KHỞI TẠO BOT ===
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# Lưu trạng thái cũ để tránh spam
last_status = None

# === SỰ KIỆN: KHI BOT ONLINE ===
@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập: {bot.user}")
    check_status.start()  # Bắt đầu kiểm tra mỗi phút

# === HÀM KIỂM TRA TRẠNG THÁI MÁY ===
@tasks.loop(minutes=1)
async def check_status():
    global last_status

    url = "https://hoang.cloud/status_trial_ugphone"
    scraper = cloudscraper.create_scraper()  # vượt Cloudflare

    try:
        response = scraper.get(url, timeout=15)
        html = response.text

        # Kiểm tra nếu có bất kỳ quốc gia nào hiển thị "🟢" hoặc "Còn máy"
        has_stock = "🟢" in html or "Còn máy" in html

        # Nếu trạng thái thay đổi thì gửi thông báo
        if has_stock != last_status:
            last_status = has_stock

            channel = bot.get_channel(CHANNEL_ID)
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
            time_str = now.strftime("%H:%M:%S - %d/%m/%Y")

            if has_stock:
                msg = (
                    f"📱 **Phát hiện có thể có máy Trial mới!**\n"
                    f"🕓 Cập nhật: `{time_str}`\n"
                    f"🔗 {url}"
                )
            else:
                msg = (
                    f"❌ **Hiện chưa có máy Trial.**\n"
                    f"🕓 Cập nhật: `{time_str}`\n"
                    f"🔗 {url}"
                )

            await channel.send(msg)

        # Ghi log để xem trên Render
        print(f"[{datetime.datetime.now()}] Check done, stock = {has_stock}")

    except Exception as e:
        print(f"⚠️ Lỗi khi kiểm tra: {e}")

# === CHẠY BOT ===
bot.run(TOKEN)