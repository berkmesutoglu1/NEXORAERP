from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.customers import customers_bp
from app.routes.suppliers import suppliers_bp
from app.routes.products import products_bp
from app.routes.warehouses import warehouses_bp
from app.routes.inventory import inventory_bp
from app.routes.sales import sales_bp
from app.routes.purchases import purchases_bp
from app.routes.logistics import logistics_bp
from app.routes.finance import finance_bp
from app.routes.reports import reports_bp
from app.routes.admin import admin_bp
from app.routes.api import api_bp

__all__ = [
    'auth_bp', 'dashboard_bp', 'customers_bp', 'suppliers_bp', 'products_bp',
    'warehouses_bp', 'inventory_bp', 'sales_bp', 'purchases_bp', 'logistics_bp',
    'finance_bp', 'reports_bp', 'admin_bp', 'api_bp'
]
