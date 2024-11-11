from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone


from db.models import User, Order

TASHKENT_TZ = timezone(timedelta(hours=5))


async def get_admins(session: Session):
    users = session.execute(select(User).where(User.is_admin == True)).scalars().all()
    s_users: list[int] = []
    for user in users:
        s_users.append(user.tg_id)
    return s_users


def get_detailed_order_statistics(session):
    now = datetime.now(TASHKENT_TZ)

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday of current week
    month_start = today_start.replace(day=1)  # First day of current month

    daily_filter = (Order.created_at >= today_start, Order.created_at <= now)
    weekly_filter = (Order.created_at >= week_start, Order.created_at <= now)
    monthly_filter = (Order.created_at >= month_start, Order.created_at <= now)

    def get_stats(time_filter):
        total_products_sold = session.query(func.sum(Order.quantity)).filter(*time_filter).scalar() or 0

        revenue_cash = int(session.query(func.sum(Order.price * Order.quantity)).filter(
            *time_filter,
            Order.payment_method == 'cash'
        ).scalar() or 0)

        revenue_cashless = int(session.query(func.sum(Order.price * Order.quantity)).filter(
            *time_filter,
            Order.payment_method == 'transfer'
        ).scalar() or 0)

        successful_payments = session.query(func.count(Order.id)).filter(
            *time_filter,
            Order.is_payment_successful == True
        ).scalar() or 0

        unsuccessful_payments = session.query(func.count(Order.id)).filter(
            *time_filter,
            Order.is_payment_successful == False
        ).scalar() or 0

        delivered_orders = session.query(func.count(Order.id)).filter(
            *time_filter,
            Order.delivery_status == 'Yetkazib berildi'
        ).scalar() or 0

        in_progress_orders = session.query(func.count(Order.id)).filter(
            *time_filter,
            Order.delivery_status == 'Yetkazib berilmoqda'
        ).scalar() or 0

        total_orders = session.query(func.count(Order.id)).filter(*time_filter).scalar() or 0
        return {
            "Umumiy sotilgan maxsulotlar": total_products_sold,
            "Buyurtmalar soni": total_orders,
            "Sotilgan mahsulotlarning umumiy qiymati": {
                "Naqd": revenue_cash,
                "Karta orqali": revenue_cashless
            },
            "To'lovlar statusi": {
                "to'langan": successful_payments,
                "to'lanmagan": unsuccessful_payments
            },
            "Yetkazib berish statusi": {
                "Yetkazildi": delivered_orders,
                "Yetkazib berilmoqda": in_progress_orders
            }
        }


    daily_stats = get_stats(daily_filter)
    weekly_stats = get_stats(weekly_filter)
    monthly_stats = get_stats(monthly_filter)

    return {
        "daily": daily_stats,
        "weekly": weekly_stats,
        "monthly": monthly_stats
    }
