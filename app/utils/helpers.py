from datetime import datetime, timedelta
from app.models.product import Product, StockLot
from app.models.sales import SalesOrder
from app.models.finance import Invoice

def format_currency(value):
    if value is None:
        return "₺0,00"
    return f"₺{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(value, fmt="%d.%m.%Y"):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    return value.strftime(fmt)

def get_system_notifications():
    """
    Dynamically generates system notification badges & alerts from live database queries:
    - Critical stock level alerts
    - Expiring LOTs (SKT within 30 days)
    - Pending shipments / orders
    - Overdue invoices
    """
    alerts = []
    
    # 1. Critical stock alerts
    products = Product.query.filter_by(is_active=True).all()
    critical_products = [p for p in products if p.total_stock <= p.min_stock_level]
    if critical_products:
        alerts.append({
            'level': 'danger',
            'icon': 'bi-exclamation-triangle-fill',
            'title': 'Kritik Stok Uyarısı',
            'message': f"{len(critical_products)} ürün kritik stok seviyesinde veya altında!",
            'link': '/inventory/movements'
        })

    # 2. Expiring LOTs within 30 days
    today = datetime.utcnow().date()
    thirty_days_later = today + timedelta(days=30)
    expiring_lots = StockLot.query.filter(
        StockLot.expiration_date <= thirty_days_later,
        StockLot.quantity > 0
    ).all()
    if expiring_lots:
        alerts.append({
            'level': 'warning',
            'icon': 'bi-clock-history',
            'title': 'SKT Uyarısı',
            'message': f"{len(expiring_lots)} lot/parti ürününün SKT'si 30 gün içinde doluyor!",
            'link': '/inventory/lots'
        })

    # 3. Pending sales orders
    pending_orders_count = SalesOrder.query.filter_by(status='Beklemede').count()
    if pending_orders_count > 0:
        alerts.append({
            'level': 'info',
            'icon': 'bi-truck',
            'title': 'Bekleyen Siparişler',
            'message': f"{pending_orders_count} satış siparişi onay ve sevkiyat bekliyor.",
            'link': '/sales/orders'
        })

    # 4. Unpaid invoices past due date
    overdue_invoices_count = Invoice.query.filter(
        Invoice.payment_status != 'ODENDI',
        Invoice.due_date < today
    ).count()
    if overdue_invoices_count > 0:
        alerts.append({
            'level': 'warning',
            'icon': 'bi-receipt',
            'title': 'Vadesi Geçmiş Fatura',
            'message': f"{overdue_invoices_count} faturanın ödeme vadesi geçti!",
            'link': '/finance/invoices'
        })

    return alerts
