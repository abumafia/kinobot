import json
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command

# Bot token va admin ID
API_TOKEN = "8078122573:AAFcCioxw6TCi3BawTQIC1vF5trvMZ4WeiE"
ADMIN_ID = 6606638731

# Bot va dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Kino ma'lumotlarini saqlash uchun fayl
DATA_FILE = "kino_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

kino_data = load_data()

admin_state = {}

# Admin kod kiritadi
@dp.message(Command("add"))
async def add_code(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("❌ Sizda bu amalni bajarish huquqi yo‘q!")
        return
    
    await message.reply("📝 Iltimos, yangi kodni kiriting.")
    admin_state[message.from_user.id] = {"step": "waiting_for_code"}

# Admin video uzatadi yoki yuboradi
@dp.message()
async def process_admin_input(message: types.Message):
    user_id = message.from_user.id
    if user_id not in admin_state:
        await check_user_code(message)
        return
    
    state = admin_state[user_id]
    
    if state["step"] == "waiting_for_code":
        code = message.text.strip()
        if code in kino_data:
            await message.reply("❌ Bu kod allaqachon mavjud! Boshqa kod kiriting.")
            return
        
        admin_state[user_id] = {"step": "waiting_for_video", "code": code}
        await message.reply("📤 Endi kino videosini uzating yoki yuklang.")
    
    elif state["step"] == "waiting_for_video":
        if not message.video:
            await message.reply("❌ Iltimos, videoni jo‘nating yoki boshqa chatdan uzating!")
            return
        
        admin_state[user_id]["video_id"] = message.video.file_id
        admin_state[user_id]["step"] = "waiting_for_info"
        await message.reply("ℹ️ Endi kino haqida qisqacha ma'lumot yuboring.")
    
    elif state["step"] == "waiting_for_info":
        info = message.text.strip()
        code = admin_state[user_id]["code"]
        video_id = admin_state[user_id]["video_id"]
        
        kino_data[code] = {"video_id": video_id, "info": info}
        save_data(kino_data)
        
        del admin_state[user_id]
        await message.reply(f"✅ *Kino saqlandi!*\n\n*Kod:* `{code}`", parse_mode="Markdown")

# Foydalanuvchi kod yuborishi
async def check_user_code(message: types.Message):
    code = message.text.strip()
    if code in kino_data:
        data = kino_data[code]
        await bot.send_video(
            chat_id=message.chat.id,
            video=data["video_id"],
            caption=f"🎬 *Kino:* `{code}`\n📌 {data['info']}",
            parse_mode="Markdown"
        )
    else:
        await message.reply("❌ Bunday kod topilmadi! To‘g‘ri kod yuborganingizni tekshiring.")

# Botni ishga tushirish
async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
