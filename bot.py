import asyncio
import json
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8772901246:AAGUllaiGBUwlxMMIF9JkKIiMOcXR4rOaws")
LEADS_CHAT_ID = int(os.environ.get("LEADS_CHAT_ID", "-1001221667561"))
PORT = int(os.environ.get("PORT", "8080"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

async def handle_lead(request):
    if request.method == 'OPTIONS':
        return web.Response(headers=CORS_HEADERS)
    try:
        data = await request.json()
        name = data.get('name', '—')
        phone = data.get('phone', '—')

        text = (
            f"🔥 *НОВИЙ ЛІД — КРУЇЗ*\n\n"
            f"👤 Імʼя: {name}\n"
            f"📞 Телефон: {phone}\n\n"
            f"🚢 Тур: 4 Канарські острови + Мадейра · Costa Smeralda\n"
            f"📅 Дати: 22–29 листопада 2026\n"
            f"📍 Джерело: Mini App"
        )

        await bot.send_message(LEADS_CHAT_ID, text, parse_mode="Markdown")
        print(f"✅ Лід отримано: {name} {phone}")
        return web.json_response({"ok": True}, headers=CORS_HEADERS)
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return web.json_response({"ok": False, "error": str(e)}, headers=CORS_HEADERS, status=500)

async def handle_health(request):
    return web.json_response({"status": "ok", "service": "TurBonjour CruiseBot"})

@dp.message(F.text == "/start")
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="🚢 Відкрити круїз",
                web_app=WebAppInfo(
                    url="https://maksymtsyhanok.github.io/cruise-mini-app/"
                )
            )
        ]],
        resize_keyboard=True
    )
    await message.answer(
        "👋 Привіт! Натисни кнопку нижче щоб переглянути круїз Канари + Мадейра 🌴",
        reply_markup=kb
    )

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        name = data.get('name', '—')
        phone = data.get('phone', '—')

        text = (
            f"🔥 *НОВИЙ ЛІД — КРУЇЗ (через бота)*\n\n"
            f"👤 Імʼя: {name}\n"
            f"📞 Телефон: {phone}\n\n"
            f"🚢 Тур: 4 Канарські острови + Мадейра · Costa Smeralda\n"
            f"📅 Дати: 22–29 листопада 2026\n"
            f"📍 Джерело: KeyboardButton Mini App"
        )
        await bot.send_message(LEADS_CHAT_ID, text, parse_mode="Markdown")
        await message.answer("Дякуємо! Наш менеджер звʼяжеться з вами ✅")
    except Exception as e:
        print(f"❌ Помилка web_app_data: {e}")

async def main():
    app = web.Application()
    app.router.add_route('GET',     '/health', handle_health)
    app.router.add_route('OPTIONS', '/lead',   handle_lead)
    app.router.add_route('POST',    '/lead',   handle_lead)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"✅ Сервер запущено на порту {PORT}")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
