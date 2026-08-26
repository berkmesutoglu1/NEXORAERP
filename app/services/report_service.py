from sqlalchemy import func
from app import db
from app.models.sales import SalesOrder, SalesOrderItem
from app.models.product import Product, Category, StockLot
from app.models.warehouse import WarehouseStock, Warehouse
from app.models.finance import Invoice, Collection, Payment, CurrentAccount
from datetime import datetime, timedelta

def get_dashboard_kpis():
    """
    Returns live dynamic KPI counts from MySQL/SQLite DB:
    - Toplam Satış (Total Sales revenue)
    - Bugünkü Satış (Today's Sales revenue)
    - Bekleyen Sipariş (Pending Sales Orders count)
    - Kritik Stok (Products below min_stock_level count)
    - Bekleyen Tahsilat (Total open balance of all customer current accounts)
    - Bu Ayki Ciro (Monthly Sales revenue)
    """
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)

    total_sales = db.session.query(func.sum(SalesOrder.grand_total)).scalar() or 0.0

    todays_sales = db.session.query(func.sum(SalesOrder.grand_total))\
        .filter(SalesOrder.order_date == today).scalar() or 0.0

    monthly_sales = db.session.query(func.sum(SalesOrder.grand_total))\
        .filter(SalesOrder.order_date >= start_of_month).scalar() or 0.0

    pending_orders = SalesOrder.query.filter(SalesOrder.status.in_(['Beklemede', 'Hazırlanıyor'])).count()

    # Count products whose total warehouse stock is below their minimum stock level
    products = Product.query.filter_by(is_active=True).all()
    critical_stock_count = sum(1 for p in products if p.total_stock <= p.min_stock_level)

    # Total uncollected customer debt
    pending_collections = db.session.query(func.sum(CurrentAccount.balance))\
        .filter(CurrentAccount.party_type == 'MUSTERI', CurrentAccount.balance > 0).scalar() or 0.0

    return {
        'total_sales': total_sales,
        'todays_sales': todays_sales,
        'monthly_sales': monthly_sales,
        'pending_orders': pending_orders,
        'critical_stock_count': critical_stock_count,
        'pending_collections': pending_collections
    }

def get_product_profitability_report():
    """
    Calculates profit, profit margin %, total quantity sold, and revenue per product.
    """
    products = Product.query.filter_by(is_active=True).all()
    report = []
    
    for p in products:
        sales_qty = db.session.query(func.sum(SalesOrderItem.quantity))\
            .join(SalesOrder)\
            .filter(SalesOrderItem.product_id == p.id, SalesOrder.status != 'İptal').scalar() or 0.0
            
        sales_rev = db.session.query(func.sum(SalesOrderItem.total_price))\
            .join(SalesOrder)\
            .filter(SalesOrderItem.product_id == p.id, SalesOrder.status != 'İptal').scalar() or 0.0
            
        total_cost = sales_qty * (p.purchase_price or 0.0)
        total_profit = sales_rev - total_cost
        margin_pct = ((p.sale_price - p.purchase_price) / p.purchase_price * 100) if p.purchase_price else 0.0

        report.append({
            'product_code': p.code,
            'product_name': p.name,
            'category_name': p.category.name if p.category else '-',
            'unit_name': p.unit.name if p.unit else 'Adet',
            'purchase_price': p.purchase_price,
            'sale_price': p.sale_price,
            'margin_pct': round(margin_pct, 2),
            'total_sold_qty': sales_qty,
            'total_revenue': sales_rev,
            'total_cost': total_cost,
            'total_profit': total_profit
        })

    return report
