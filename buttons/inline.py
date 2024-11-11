from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def users_buttons(users):
    ikm = InlineKeyboardBuilder()
    for user in users:
        ikm.button(text=user.full_name, callback_data=str(user.tg_id))
    ikm.adjust(1, repeat=True)
    return ikm.as_markup()

async def payment_method_button():
    ikm = InlineKeyboardBuilder()
    click = InlineKeyboardButton(text="Click", callback_data='transfer')
    cash = InlineKeyboardButton(text="Naqd", callback_data='cash')
    ikm.add(click, cash)
    ikm.adjust(2, repeat=True)
    return ikm.as_markup()

async def payment_done_btn():
    ikm = InlineKeyboardBuilder()
    yes = InlineKeyboardButton(text="Ha", callback_data='Ha')
    no = InlineKeyboardButton(text="Yo'q", callback_data="Yo'q")
    ikm.add(yes, no)
    ikm.adjust(2, repeat=True)
    return ikm.as_markup()

async def order_states_buttons():
    ikm = InlineKeyboardBuilder()
    name = InlineKeyboardButton(text="Ismi", callback_data='client_name')
    phone = InlineKeyboardButton(text="Telefon raqami", callback_data="phone")
    address = InlineKeyboardButton(text="Manzili", callback_data="address")
    location = InlineKeyboardButton(text="Lokatsiyasi", callback_data="location")
    product = InlineKeyboardButton(text="Maxsulot", callback_data="product")
    price = InlineKeyboardButton(text="Narxi", callback_data="price")
    quantity = InlineKeyboardButton(text="Soni", callback_data="quantity")
    payment_method = InlineKeyboardButton(text="To'lov turi", callback_data="payment_method")
    is_payment = InlineKeyboardButton(text="To'langanligi", callback_data="is_payment_successful")
    comment = InlineKeyboardButton(text="Komentariya", callback_data="comment")
    ikm.add( name, phone, address, location, product, price, quantity, payment_method, is_payment, comment)
    ikm.adjust(2, repeat=True)
    return ikm.as_markup()

async def edit_order_btn():
    ikm = InlineKeyboardBuilder()
    name = InlineKeyboardButton(text="Ismi", callback_data='client_name')
    phone = InlineKeyboardButton(text="Telefon raqami", callback_data="phone_number")
    address = InlineKeyboardButton(text="Manzili", callback_data="address")
    location = InlineKeyboardButton(text="Lokatsiyasi", callback_data="location")
    product = InlineKeyboardButton(text="Maxsulot", callback_data="product")
    price = InlineKeyboardButton(text="Narxi", callback_data="price")
    quantity = InlineKeyboardButton(text="Soni", callback_data="quantity")
    delivery_status = InlineKeyboardButton(text="Status", callback_data="delivery_status")
    payment_method = InlineKeyboardButton(text="To'lov turi", callback_data="payment_method")
    is_payment = InlineKeyboardButton(text="To'langanligi", callback_data="is_payment_successful")
    comment = InlineKeyboardButton(text="Komentariya", callback_data="comment")
    ikm.add(name, phone, address, location, product, price, quantity, delivery_status, payment_method, is_payment, comment)
    ikm.adjust(2, repeat=True)
    return ikm.as_markup()