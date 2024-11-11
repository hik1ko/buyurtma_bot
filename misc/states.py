from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    main_menu = State()
    make_admin = State()
    revoke_admin = State()
    get_stats = State()

class GeneralStates(StatesGroup):
    start = State()

class OrderStates(StatesGroup):
    name = State()
    phone = State()
    address = State()
    location = State()
    product = State()
    price = State()
    quantity = State()
    payment_method = State()
    is_payment_successful = State()
    comment = State()
    checkout = State()
    change = State()
    new_data = State()
    after_change = State()

class EditOrderStates(StatesGroup):
    id = State()
    changing_field = State()
    new_value = State()