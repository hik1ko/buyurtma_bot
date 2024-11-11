from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import update, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from buttons import admin_button, cancel_btn, payment_method_button, comment_btn, check_order_btn, \
    payment_done_btn, order_states_buttons, random_btn, edit_order_btn, delivery_status_btn, statistics_btn, \
    users_buttons
from db.models import User, Order
from misc import AdminStates, OrderStates, EditOrderStates
from utils import get_detailed_order_statistics

superuser = 5580965528
GROUP_ID = -4597645134

main_router = Router()


@main_router.message(AdminStates.main_menu, F.text == "Admin tayinlash")
async def admin_add_handler(message: Message, state: FSMContext):
    if message.from_user.id == superuser:
        await message.answer("Admin qilmoqchi bo'lgan odamning telegram smsini forward qiling")
        await state.set_state(AdminStates.make_admin)
    else:
        await message.answer("Faqatgina superadmin admin tayinlay oladi!")


@main_router.message(AdminStates.make_admin)
async def admin_make_handler(message: Message, state: FSMContext, session: Session):
    try:
        user_id = message.forward_origin.sender_user.id
        if user_id:
            is_exists = session.execute(select(User).where(User.tg_id == user_id)).scalar()
            if is_exists:
                await message.answer("Admin muvaffaqiyatli qo'shildi!", reply_markup=await admin_button())
                stmt = update(User).where(User.tg_id == user_id).values(is_admin=True)
                session.execute(stmt)
                session.commit()
                await message.bot.send_message(chat_id=user_id,
                                               text="Siz admin etib tayinlandingiz, botdan foydalanish uchun /start ni bosing",
                                               reply_markup=await admin_button())
                await state.set_state(AdminStates.main_menu)
            else:
                await message.answer("Admin qilmoqchi bo'lgan kishingiz botga start bosishi kerak!")
                await state.set_state(AdminStates.main_menu)
    except:
        await message.answer(
            "Bu kishini telegram idsini olib bo'lmadi, sozlamalarini (forwarded messages)ni hammaga ko'rinadigan qilib qo'yishi kerak",
            reply_markup=await admin_button())
        await state.set_state(AdminStates.main_menu)


@main_router.message(AdminStates.main_menu, F.text == "Adminlikni olish")
async def remove_handler(message: Message, state: FSMContext, session: Session):
    if message.from_user.id == superuser:
        users = session.query(User).filter(User.is_admin == True)
        await message.answer("Adminlikni olmoqchi bo'lganni tanlang", reply_markup=await users_buttons(users))
        await state.set_state(AdminStates.revoke_admin)
    else:
        await message.answer("Adminlikni faqat superadmin ola oladi!", reply_markup=await admin_button())


@main_router.callback_query(AdminStates.revoke_admin)
async def revoke_handler(query: CallbackQuery, state: FSMContext, session: Session):
    stmt = update(User).where(User.tg_id == int(query.data)).values(is_admin=False)
    session.execute(stmt)
    session.commit()
    await query.message.answer("Admin muvaffaqiyatli o'chirildi!", reply_markup=await admin_button())
    await state.set_state(AdminStates.main_menu)


@main_router.message(AdminStates.main_menu, F.text == "Yangi buyurtma qo'shish")
async def new_order_handler(message: Message, state: FSMContext):
    await message.answer("Mijozning ismini kiriting", reply_markup=await cancel_btn())
    await state.set_state(OrderStates.name)


@main_router.message(OrderStates.name, F.text)
async def name_handler(message: Message, state: FSMContext):
    await message.answer("Mijozning telefon raqamini kiriting", reply_markup=await cancel_btn())
    await state.update_data(client_name=message.text)
    await state.set_state(OrderStates.phone)


@main_router.message(OrderStates.phone, F.text)
async def phone_handler(message: Message, state: FSMContext):
    await message.answer("Mijozning manzilini kiriting", reply_markup=await cancel_btn())
    await state.update_data(phone=message.text)
    await state.set_state(OrderStates.address)


@main_router.message(OrderStates.address, F.text)
async def address_handler(message: Message, state: FSMContext):
    await message.answer("Mijozning lokatsiyasini jo'nating", reply_markup=await cancel_btn())
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.location)


@main_router.message(OrderStates.location, F.location)
async def location_handler(message: Message, state: FSMContext):
    await message.answer("Maxsulot nomini kiriting", reply_markup=await cancel_btn())
    await state.update_data(longitude=message.location.longitude, latitude=message.location.latitude)
    await state.set_state(OrderStates.product)


@main_router.message(OrderStates.product, F.text)
async def product_handler(message: Message, state: FSMContext):
    await message.answer("Maxsulotning narxini kiriting", reply_markup=await cancel_btn())
    await state.update_data(product=message.text)
    await state.set_state(OrderStates.price)


@main_router.message(OrderStates.price, F.text)
async def price_handler(message: Message, state: FSMContext):
    await message.answer("Maxsulot sonini kiriting", reply_markup=await cancel_btn())
    if message.text.find('.'):
        await state.update_data(price=message.text.replace('.', ''))
    else:
        await state.update_data(price=message.text)
    await state.set_state(OrderStates.quantity)


@main_router.message(OrderStates.quantity, F.text)
async def quantity_handler(message: Message, state: FSMContext):
    await message.answer("To'lov turini tanlang", reply_markup=await payment_method_button())
    await state.update_data(quantity=message.text)
    await state.set_state(OrderStates.payment_method)


@main_router.callback_query(OrderStates.payment_method)
async def payment_method_handler(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Puli to'langanmi?", reply_markup=await payment_done_btn())
    await state.update_data(payment_method=query.data)
    await state.set_state(OrderStates.is_payment_successful)


@main_router.callback_query(OrderStates.is_payment_successful)
async def is_payment_handler(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Komment bo'lsa kiriting", reply_markup=await comment_btn())
    if query.data == "Yo'q":
        await state.update_data(is_payment_successful=False)
    else:
        await state.update_data(is_payment_successful=True)
    await state.set_state(OrderStates.comment)


@main_router.message(OrderStates.after_change, F.text)
@main_router.message(OrderStates.comment, F.text)
async def comment_handler(message: Message, state: FSMContext):
    if message.text != "Yo'q" or message.text != "Kommentariya yo'q":
        await state.update_data(comment=message.text)
    else:
        await state.update_data(comment=None)
    order_data = await state.get_data()
    latitude = f"{order_data.get('latitude'):.6f}"
    longitude = f"{order_data.get('longitude'):.6f}"
    yandex_location_link = f"https://yandex.com/maps/?ll={longitude}%2C{latitude}&z=16&l=map&pt={longitude},{latitude}"
    google_location_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    payment = "Ha" if order_data.get('is_payment_successful') else "Yo'q"
    pay_meth = "Naqd" if order_data.get('payment_method') == 'cash' else "Click"
    overall_price = int(order_data['price']) * int(order_data['quantity'])
    data_fields = f"""Mijozning ismi: {order_data.get('client_name')}
Telefon raqami: {order_data.get('phone')}
Manzil: {order_data.get('address')}
Lokatsiya: [Yandex]({yandex_location_link}) [Google]({google_location_link})
Maxsulot: {order_data.get('product')}
Narxi: {int(order_data.get('price')):,}
Soni: {order_data.get('quantity')}
Puli to'langanmi: {payment}
To'lov turi: {pay_meth}
Kommentariya: {order_data.get('comment')}

Umumiy narx: {overall_price:,}"""
    await message.answer(data_fields, parse_mode="Markdown",
                         disable_web_page_preview=True)
    await state.update_data(data_fields=data_fields)
    await message.answer("Barcha ma'lumotlar to'g'rimi", reply_markup=await check_order_btn())
    await state.set_state(OrderStates.checkout)


@main_router.message(OrderStates.checkout, F.text)
async def checkout_handler(message: Message, state: FSMContext, session: Session):
    if message.text == "To'g'ri":
        order_data = await state.get_data()
        order = {
            "client_name": order_data.get('client_name'),
            "phone_number": order_data.get('phone'),
            "address": order_data.get('address'),
            "longitude": f"{order_data.get('longitude'):.6f}",
            "latitude": f"{order_data.get('latitude'):.6f}",
            "product": order_data.get('product'),
            "price": int(order_data.get('price')),
            "quantity": int(order_data.get('quantity')),
            "payment_method": order_data.get('payment_method'),
            "is_payment_successful": order_data.get('is_payment_successful'),
            "comment": order_data.get('comment')
        }
        session.execute(insert(Order).values(**order))
        session.commit()
        last_order = session.query(Order).order_by(Order.created_at.desc()).first()
        latitude = f"{order_data.get('latitude'):.6f}"
        longitude = f"{order_data.get('longitude'):.6f}"
        yandex_location_link = f"https://yandex.com/maps/?ll={longitude}%2C{latitude}&z=16&l=map&pt={longitude},{latitude}"
        google_location_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        payment = "Ha" if order_data.get('is_payment_successful') else "Yo'q"
        pay_meth = "Naqd" if order_data.get('payment_method') == 'cash' else "Click"
        overall_price = int(order_data['price']) * int(order_data['quantity'])
        data_fields = f"""Buyurtma raqam: {last_order.id}
Mijozning ismi: {order_data.get('client_name')}
Telefon raqami: {order_data.get('phone')}
Manzil: {order_data.get('address')}
Lokatsiya: [Yandex]({yandex_location_link}) [Google]({google_location_link})
Maxsulot: {order_data.get('product')}
Narxi: {int(order_data.get('price')):,}
Soni: {order_data.get('quantity')}
Puli to'langanmi: {payment}
To'lov turi: {pay_meth}
Kommentariya: {order_data.get('comment')}

Umumiy narx: {overall_price:,}"""
        order_message = await message.bot.send_message(
            chat_id=GROUP_ID,
            text=data_fields,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        await order_message.bot.pin_chat_message(
            chat_id=GROUP_ID,
            message_id=order_message.message_id
        )
        await message.answer(f"{last_order.id} - raqamli buyurtma muvaffaqiyatli qo'shildi",
                             reply_markup=await admin_button())

        # Clear the state and return to the main menu
        await state.clear()
        await state.set_state(AdminStates.main_menu)

    elif message.text == "Xatolik bor":
        await message.answer("O'zgartirmoqchi bo'lgan ma'lumotni belgilang", reply_markup=await order_states_buttons())
        await state.set_state(OrderStates.change)


@main_router.callback_query(OrderStates.change)
async def order_states_handler(query: CallbackQuery, state: FSMContext):
    await query.message.answer("Yangi ma'lumotni kiriting")
    await state.update_data(changing_field=query.data)
    await state.set_state(OrderStates.new_data)


@main_router.message(OrderStates.new_data)
async def new_data_handler(message: Message, state: FSMContext):
    await message.answer("Ma'lumot o'zgartirildi", reply_markup=await random_btn())
    states_data = await state.get_data()
    changing_field = states_data.get("changing_field")
    if message.text:
        await state.update_data({changing_field: message.text})
    if message.location:
        await state.update_data(latitude=message.location.latitude, longitude=message.location.longitude)
    await state.set_state(OrderStates.after_change)


@main_router.message(AdminStates.main_menu, F.text == "Buyurtmani tahrirlash")
async def edit_order(message: Message, state: FSMContext):
    await message.answer("O'zgartirmoqchi bo'lgan buyurtmani raqamini jo'nating")
    await state.set_state(EditOrderStates.id)


@main_router.message(EditOrderStates.id, F.text)
async def edit_order(message: Message, state: FSMContext, session: Session):
    order = session.query(Order).where(Order.id == int(message.text)).first()
    if order:
        payment = "Ha" if order.is_payment_successful else "Yo'q"
        pay_meth = "Naqd" if order.payment_method == 'cash' else "Click"
        yandex_location_link = f"https://yandex.com/maps/?ll={order.longitude}%2C{order.latitude}&z=16&l=map&pt={order.longitude},{order.latitude}"
        google_location_link = f"https://www.google.com/maps/search/?api=1&query={order.latitude},{order.longitude}"
        await message.answer(text=f"""Buyurtma № {order.id}
Mijoz: {order.client_name}
Mijoz raqami: {order.phone_number}
Manzil: {order.address}
Lokatsiya: [Yandex]({yandex_location_link}) [Google]({google_location_link})
Maxsulot: {order.product}
Maxsulot narxi: {order.price:,}
Maxsulot soni: {order.quantity}
Yetkazish status: {order.delivery_status}
To'lov turi: {pay_meth}
To'langanmi: {payment}
Kommentariya: {order.comment}""", parse_mode="Markdown",
                             disable_web_page_preview=True)
        await message.answer("O'zgartirmoqchi bo'lgan ma'lumotni tanlang", reply_markup=await edit_order_btn())
        await state.set_state(EditOrderStates.changing_field)
        await state.update_data(order_id=message.text)
    else:
        await message.answer("Bu id bilan buyurtma topilmadi, iltimos tekshirib qaytadan jo'nating.",
                             reply_markup=await cancel_btn())
        await state.set_state(EditOrderStates.id)


@main_router.callback_query(EditOrderStates.changing_field)
async def edit_order_field(message: CallbackQuery, state: FSMContext):
    if message.data == 'delivery_status':
        await message.message.answer("Tanlang", reply_markup=await delivery_status_btn())
    elif message.data == 'is_payment_successful':
        await message.message.answer("Puli to'landimi", reply_markup=await payment_done_btn())
    elif message.data == 'payment_method':
        await message.message.answer("To'lov turini tanlang", reply_markup=await payment_method_button())
    else:
        await message.message.answer("Yangi ma'lumotni kiriting", reply_markup=await cancel_btn())
    await state.update_data(order_changing_field=message.data)
    await state.set_state(EditOrderStates.new_value)


@main_router.callback_query(EditOrderStates.new_value)
async def edit_order_field(message: CallbackQuery, state: FSMContext, session: Session):
    data = await state.get_data()

    # Determine what field to update based on message.data
    if message.data == 'Ha':
        session.execute(update(Order).where(Order.id == data.get('order_id')).values(is_payment_successful=True))
    elif message.data == "Yo'q":
        session.execute(update(Order).where(Order.id == data.get('order_id')).values(is_payment_successful=False))
    elif message.data == "transfer":
        session.execute(update(Order).where(Order.id == data.get('order_id')).values(payment_method='transfer'))
    elif message.data == "cash":
        session.execute(update(Order).where(Order.id == data.get('order_id')).values(payment_method='cash'))

    # Commit the changes to the database
    session.commit()

    order = session.query(Order).where(Order.id == data.get('order_id')).first()


    payment = "Ha" if order.is_payment_successful else "Yo'q"
    pay_meth = "Naqd" if order.payment_method == 'cash' else "Click"

    # Prepare the location links
    yandex_location_link = f"https://yandex.com/maps/?ll={order.longitude}%2C{order.latitude}&z=16&l=map"
    google_location_link = f"https://www.google.com/maps/search/?api=1&query={order.latitude},{order.longitude}"

    # Prepare the message text to send
    message_text = f"""Buyurtma № {order.id}
Mijoz: {order.client_name}
Telefon: {order.phone_number}
Manzil: {order.address}
Lokatsiya: [Yandex]({yandex_location_link}) | [Google]({google_location_link})
Maxsulot: {order.product}
Narxi: {order.price:,}
Soni: {order.quantity}
Yetkazish status: {order.delivery_status}
To'lov turi: {pay_meth}
To'langanmi: {payment}
Kommentariya: {order.comment}"""

    # Send the message to the admin (message.answer)
    await message.message.answer(message_text, parse_mode="Markdown", disable_web_page_preview=True,
                         reply_markup=await admin_button())

    # Clear the state and reset to main menu
    await state.clear()
    await state.set_state(AdminStates.main_menu)


@main_router.message(EditOrderStates.new_value, F.text)
async def new_value_handler(message: Message, state: FSMContext, session: Session):
    new_data = await state.get_data()
    changing_field = new_data.get("order_changing_field")
    order_id = new_data.get("order_id")
    await message.bot.send_message(chat_id=GROUP_ID, text=f"{order_id} -buyurtma ma'lumotlari yangilandi")
    if message.location:
        await message.bot.send_location(longitude=message.location.longitude, latitude=message.location.latitude)

        session.execute(
            update(Order).where(Order.id == order_id).values(
                longitude=message.location.longitude,
                latitude=message.location.latitude
            )
        )
    else:
        await message.bot.send_message(chat_id=GROUP_ID, text=f"{changing_field}: {message.text}")
        session.execute(
            update(Order).where(Order.id == order_id).values(
                **{changing_field: message.text}
            )
        )

    session.commit()
    await message.answer("Ma'lumotlar muvaffaqiyatli yangilandi.", reply_markup=await admin_button())
    await state.clear()
    await state.set_state(AdminStates.main_menu)


@main_router.message(AdminStates.main_menu, F.text == "Statistikani olish")
async def statistics_handler(message: Message, state: FSMContext):
    await message.answer("Marhamat quyidagilardan birini tanlang", reply_markup=await statistics_btn())
    await state.set_state(AdminStates.get_stats)


@main_router.message(AdminStates.get_stats, F.text)
async def statistics_type(message: Message, state: FSMContext, session: Session):
    stats = get_detailed_order_statistics(session)
    if message.text == "Kunlik":
        stat = stats["daily"]
    elif message.text == "Haftalik":
        stat = stats["weekly"]
    elif message.text == "Oylik":
        stat = stats["monthly"]

    text = f"""Umumiy buyurtmalar soni: {stat['Buyurtmalar soni']}
Umumiy sotilgan maxsulotlar: {stat['Umumiy sotilgan maxsulotlar']}
Sotilgan maxsulotlarning umumiy qiymati: {stat["Sotilgan mahsulotlarning umumiy qiymati"]['Naqd'] + stat["Sotilgan mahsulotlarning umumiy qiymati"]['Karta orqali']:,}
Naqd pulda: {stat["Sotilgan mahsulotlarning umumiy qiymati"]['Naqd']:,}
Karta orqali: {stat["Sotilgan mahsulotlarning umumiy qiymati"]['Karta orqali']:,}
To'langan: {stat["To'lovlar statusi"]["to'langan"]} 
To'lanmagan: {stat["To'lovlar statusi"]["to'lanmagan"]} 
Yetkazildi: {stat["Yetkazib berish statusi"]["Yetkazildi"]} 
Yetkazib berilmoqda: {stat["Yetkazib berish statusi"]["Yetkazib berilmoqda"]} 
    """
    await message.answer(text, reply_markup=await admin_button())
    await state.set_state(AdminStates.main_menu)


@main_router.message(F.text == "Cancel")
async def cancel_cancel_handler(message: Message, state: FSMContext):
    await message.answer("Jarayon to'xtatildi", reply_markup=await admin_button())
    await state.set_state(AdminStates.main_menu)
