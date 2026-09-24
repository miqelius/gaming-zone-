import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, Device, TournamentMatch
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = os.getenv("BOT_TOKEN", "8643225967:AAF-sfnrFJc_-f36OzeM-BAas9SUkYiZMy4")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Gio1088888888")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(dp.start_polling(bot))
    yield

app = FastAPI(title="Gaming Zone API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/devices")
def get_devices(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return {
        "pcs": [
            {
                "id": d.id,
                "name": d.name,
                "type": d.device_type,
                "is_vip": d.is_vip,
                "status": d.status
            } for d in devices if d.device_type == "PC"
        ],
        "ps5s": [
            {
                "id": d.id,
                "name": d.name,
                "type": d.device_type,
                "is_vip": d.is_vip,
                "status": d.status
            } for d in devices if d.device_type == "PS5"
        ]
    }

@app.get("/api/v1/tournament/bracket")
def get_bracket(db: Session = Depends(get_db)):
    return db.query(TournamentMatch).all()

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not message.from_user or message.from_user.username != ADMIN_USERNAME:
        return
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🖥️ PC სტატუსები (28)", callback_data="list_PC")
    builder.button(text="🎮 PS5 სტატუსები (28)", callback_data="list_PS5")
    builder.adjust(1)
    
    await message.answer(
        "🎮 **Gaming Zone - Admin Panel**\n\nაირჩიეთ კატეგორია მოწყობილობების შესამოწმებლად და სტატუსების შესაცვლელად:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("list_"))
async def list_devices(callback: types.CallbackQuery):
    if not callback.from_user or callback.from_user.username != ADMIN_USERNAME:
        await callback.answer("წვდომა უარყოფილია!", show_alert=True)
        return

    dev_type = callback.data.split("_")[1]
    db = SessionLocal()
    devices = db.query(Device).filter(Device.device_type == dev_type).all()
    db.close()

    builder = InlineKeyboardBuilder()
    for d in devices:
        status_icon = "🟢" if d.status == "FREE" else "🔴"
        vip_tag = "⭐" if d.is_vip else ""
        btn_text = f"{status_icon} {d.name} {vip_tag}"
        builder.button(text=btn_text, callback_data=f"toggle_{d.id}")
    
    builder.adjust(4)
    await callback.message.edit_text(
        f"📊 **{dev_type} სტატუსები**\n🟢 = თავისუფალია | 🔴 = დაკავებულია\n*(დააჭირეთ ღილაკს სტატუსის შესაცვლელად)*:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_device_status(callback: types.CallbackQuery):
    if not callback.from_user or callback.from_user.username != ADMIN_USERNAME:
        await callback.answer("წვდომა უარყოფილია!", show_alert=True)
        return

    dev_id = int(callback.data.split("_")[1])
    db = SessionLocal()
    device = db.query(Device).filter(Device.id == dev_id).first()
    
    if device:
        device.status = "OCCUPIED" if device.status == "FREE" else "FREE"
        db.commit()
        dev_type = device.device_type
        db.close()
        
        callback.data = f"list_{dev_type}"
        await list_devices(callback)
    else:
        db.close()
