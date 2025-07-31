from flask import Blueprint, jsonify
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from App.models import Order
from App.extensions import db
from App.models import OrderItem, Animal
from App.models import Order, User


admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('orders/metrics', methods=['GET'])
def get_order_metrics():
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=29)  # 30 days including today

    # Query: group by DATE(created_at), count number of orders
    results = (
        db.session.query(
            cast(Order.created_at, Date).label('date'),
            func.count(Order.id).label('count')
        )
        .filter(cast(Order.created_at, Date) >= start_date)
        .group_by(cast(Order.created_at, Date))
        .order_by('date')
        .all()
    )

    # Build dict of actual results
    order_dict = {r.date.strftime("%Y-%m-%d"): r.count for r in results}

    # Fill in missing dates with 0
    data = []
    for i in range(30):
        day = start_date + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        data.append({
            "date": day_str,
            "count": order_dict.get(day_str, 0)
        })

    return jsonify(data), 200


@admin_bp.route('//orders/best-sellers', methods=['GET'])
def get_best_selling_animals():
    results = (
        db.session.query(
            Animal.type,
            func.sum(OrderItem.quantity).label("total_sold")
        )
        .join(Animal, Animal.id == OrderItem.animal_id)
        .group_by(Animal.type)
        .order_by(func.sum(OrderItem.quantity).desc())
        .all()
    )

    data = [
        {"type": row.type, "count": int(row.total_sold)}
        for row in results
    ]
    return jsonify(data), 200


@admin_bp.route('/orders/grouped', methods=['GET'])
def get_orders_grouped_by_date():
    results = (
        db.session.query(
            cast(Order.created_at, Date).label('date'),
            Order.id,
            Order.user_id,
            Order.amount,
            Order.total,
            Order.status,
            Order.paid,
            Order.delivered,
            Order.payment_method,
            Order.delivery_method,
            Order.created_at,
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    grouped = {}
    for row in results:
        date_str = row.date.strftime('%Y-%m-%d')
        if date_str not in grouped:
            grouped[date_str] = []
        grouped[date_str].append({
            "id": str(row.id),
            "user_id": str(row.user_id),
            "amount": float(row.amount),
            "total": float(row.total),
            "status": row.status,
            "paid": row.paid,
            "delivered": row.delivered,
            "payment_method": row.payment_method,
            "delivery_method": row.delivery_method,
            "created_at": row.created_at.isoformat(),
        })

    # Sort by date descending and convert to list format
    data = [
        {"date": date, "orders": grouped[date]}
        for date in sorted(grouped.keys(), reverse=True)
    ]

    return jsonify(data), 200

@admin_bp.route("/sales/summary", methods=["GET"])
def daily_sales_summary():
    results = (
        db.session.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total).label("total_sales")
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    data = [{"date": str(row.date), "total_sales": float(row.total_sales)} for row in results]
    return jsonify(data), 200