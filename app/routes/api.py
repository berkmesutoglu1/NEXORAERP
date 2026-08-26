from flask import Blueprint, jsonify
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models.sales import SalesOrder, SalesOrderItem
from app.models.product import Product, Category
from app.models.warehouse import WarehouseStock, Warehouse
from app.models.finance import Collection, Payment
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__)

@api_bp.route('/charts/dashboard-analytics')
@login_required
def dashboard_analytics():
    """
    Returns aggregated live JSON chart data for Chart.js:
    1. Monthly Sales Trend (Last 6 months)
    2. Top 5 Selling Products
    3. Category Sales Share
    4. Warehouse Stock Valuation/Quantities
    5. Collection vs Payment Flow
    """
    today = datetime.utcnow().date()

    # 1. Monthly Sales Trend (Last 6 Months)
    months_labels = []
    monthly_sales_data = []
    
    for i in range(5, -1, -1):
        # Calculate month date ranges
        first_day = (today.replace(day=1) - timedelta(days=i*28)).replace(day=1)
        if first_day.month == 12:
            last_day = first_day.replace(year=first_day.year+1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = first_day.replace(month=first_day.month+1, day=1) - timedelta(days=1)

        month_name = first_day.strftime('%b %Y')
        months_labels.append(month_name)

        sales_sum = db.session.query(func.sum(SalesOrder.grand_total))\
            .filter(SalesOrder.order_date >= first_day, SalesOrder.order_date <= last_day, SalesOrder.status != 'İptal').scalar() or 0.0
        monthly_sales_data.append(round(sales_sum, 2))

    # 2. Top 5 Selling Products
    top_products_query = db.session.query(
        Product.name,
        func.sum(SalesOrderItem.quantity).label('total_qty')
    ).join(SalesOrderItem, SalesOrderItem.product_id == Product.id)\
     .group_by(Product.id)\
     .order_by(func.sum(SalesOrderItem.quantity).desc())\
     .limit(5).all()

    top_products_labels = [p[0] for p in top_products_query]
    top_products_data = [float(p[1]) for p in top_products_query]

    # 3. Category Sales Distribution
    cat_query = db.session.query(
        Category.name,
        func.sum(SalesOrderItem.total_price)
    ).join(Product, Product.category_id == Category.id)\
     .join(SalesOrderItem, SalesOrderItem.product_id == Product.id)\
     .group_by(Category.id).all()

    cat_labels = [c[0] for c in cat_query]
    cat_data = [float(c[1]) for c in cat_query]

    # 4. Warehouse Stock Distribution
    wh_query = db.session.query(
        Warehouse.name,
        func.sum(WarehouseStock.quantity)
    ).join(WarehouseStock, WarehouseStock.warehouse_id == Warehouse.id)\
     .group_by(Warehouse.id).all()

    wh_labels = [w[0] for w in wh_query]
    wh_data = [float(w[1]) for w in wh_query]

    # 5. Collection vs Payment Flow
    col_sum = db.session.query(func.sum(Collection.amount)).scalar() or 0.0
    pay_sum = db.session.query(func.sum(Payment.amount)).scalar() or 0.0

    return jsonify({
        'monthly_sales': {
            'labels': months_labels,
            'data': monthly_sales_data
        },
        'top_products': {
            'labels': top_products_labels,
            'data': top_products_data
        },
        'category_sales': {
            'labels': cat_labels,
            'data': cat_data
        },
        'warehouse_stocks': {
            'labels': wh_labels,
            'data': wh_data
        },
        'cash_flow': {
            'collections': col_sum,
            'payments': pay_sum
        }
    })
