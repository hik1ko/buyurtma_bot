from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


async def admin_button():
    design = [
        [
            KeyboardButton(text="Admin tayinlash"),
            KeyboardButton(text="Adminlikni olish")
        ],
        [
            KeyboardButton(text="Yangi buyurtma qo'shish"),
            KeyboardButton(text="Buyurtmani tahrirlash")
        ],
        [
            KeyboardButton(text="Statistikani olish")
        ]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm

async def statistics_btn():
    design = [
        [
            KeyboardButton(text="Kunlik"),
            KeyboardButton(text="Haftalik"),
            KeyboardButton(text="Oylik"),
        ]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm

async def cancel_btn():
    design = [
        [
            KeyboardButton(text="Cancel")
        ]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm

async def comment_btn():
    design = [
        [
            KeyboardButton(text="Kommentariya yo'q"),
        ]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm

async def check_order_btn():
    design = [
        [
            KeyboardButton(text="To'g'ri"),
            KeyboardButton(text="Xatolik bor")
        ]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm

async def random_btn():
    design = [
        [ KeyboardButton(text="Ma'lumotlarni tekshirishga qaytish")]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm

async def delivery_status_btn():
    design = [
        [ KeyboardButton(text="Yetkazib berildi")]
    ]
    rkm = ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
    return rkm
