from flask import Blueprint, render_template, request
from flask_login import login_required
from app.services.report_service import get_product_profitability_report
from app.models.sales import SalesOrder, SalesOrderItem
from app.models.product import Product, Category
from app.models.warehouse import WarehouseStock, Warehouse
from app.models.finance import Invoice, Collection, Payment
from app.utils.decorators import role_required

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/sales')
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli', 'Muhasebe')
def sales_report():
    orders = SalesOrder.query.order_by(SalesOrder.order_date.desc()).all()
    categories = Category.query.all()
    return render_template('reports/sales_report.html', orders=orders, categories=categories)


@reports_bp.route('/inventory')
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def inventory_report():
    products = Product.query.filter_by(is_active=True).all()
    warehouses = Warehouse.query.all()
    return render_template('reports/inventory_report.html', products=products, warehouses=warehouses)


@reports_bp.route('/finance')
@login_required
@role_required('Admin', 'Yönetici', 'Muhasebe')
def finance_report():
    invoices = Invoice.query.all()
    collections = Collection.query.all()
    payments = Payment.query.all()

    total_invoiced = sum(i.grand_total for i in invoices if i.invoice_type == 'SATIS')
    total_collected = sum(c.amount for c in collections)
    total_paid = sum(p.amount for p in payments)

    return render_template(
        'reports/finance_report.html',
        invoices=invoices,
        collections=collections,
        payments=payments,
        total_invoiced=total_invoiced,
        total_collected=total_collected,
        total_paid=total_paid
    )


@reports_bp.route('/profitability')
@login_required
@role_required('Admin', 'Yönetici')
def profitability_report():
    profitability_data = get_product_profitability_report()
    return render_template('reports/profitability_report.html', profitability=profitability_data)
