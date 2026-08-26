from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.services.report_service import get_dashboard_kpis
from app.models.product import Product, StockLot
from app.models.sales import SalesOrder
from app.models.logistics import Shipment
from app.models.finance import Invoice
from app.models.user import AuditLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    kpis = get_dashboard_kpis()
    
    # Recent Activities & Audit Logs
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(7).all()
    
    # Recent Sales Orders
    recent_orders = SalesOrder.query.order_by(SalesOrder.order_date.desc()).limit(5).all()

    # Expiring LOTs (SKT within 30 days)
    today = datetime.utcnow().date()
    thirty_days = today + timedelta(days=30)
    expiring_lots = StockLot.query.filter(
        StockLot.expiration_date <= thirty_days,
        StockLot.quantity > 0
    ).order_by(StockLot.expiration_date.asc()).limit(6).all()

    # Critical Products List
    products = Product.query.filter_by(is_active=True).all()
    critical_products = [p for p in products if p.total_stock <= p.min_stock_level][:6]

    return render_template(
        'dashboard/index.html',
        kpis=kpis,
        recent_logs=recent_logs,
        recent_orders=recent_orders,
        expiring_lots=expiring_lots,
        critical_products=critical_products
    )
