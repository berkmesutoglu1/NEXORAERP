from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json
from app import db
from app.models.sales import SalesQuote, SalesQuoteItem, SalesOrder, SalesOrderItem
from app.models.party import Customer
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.services.sales_service import (convert_quote_to_order, validate_order_stock, 
                                        generate_document_number)
from app.services.finance_service import create_invoice_from_sales_order
from app.services.audit_service import log_action
from app.utils.decorators import role_required

sales_bp = Blueprint('sales', __name__)

# --- QUOTES ---
@sales_bp.route('/quotes')
@login_required
def list_quotes():
    quotes = SalesQuote.query.order_by(SalesQuote.created_at.desc()).all()
    return render_template('sales/quotes.html', quotes=quotes)


@sales_bp.route('/quotes/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli')
def create_quote():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        items_json = request.form.get('items_json')
        notes = request.form.get('notes', '').strip()

        items = json.loads(items_json) if items_json else []
        if not items:
            flash('En az bir ürün eklemelisiniz.', 'danger')
            return redirect(url_for('sales.create_quote'))

        q_num = generate_document_number("TEK")
        quote = SalesQuote(
            quote_number=q_num,
            customer_id=customer_id,
            date=datetime.utcnow().date(),
            status='Taslak',
            created_by_id=current_user.id,
            notes=notes
        )
        db.session.add(quote)
        db.session.flush()

        subtotal = 0.0
        vat_tot = 0.0

        for item in items:
            p_id = int(item['product_id'])
            qty = float(item['quantity'])
            price = float(item['unit_price'])
            vat = float(item['vat_rate'])
            
            tot = qty * price
            v_val = tot * (vat / 100.0)
            subtotal += tot
            vat_tot += v_val

            qitem = SalesQuoteItem(
                quote_id=quote.id,
                product_id=p_id,
                quantity=qty,
                unit_price=price,
                vat_rate=vat,
                total_price=tot
            )
            db.session.add(qitem)

        quote.subtotal = subtotal
        quote.vat_amount = vat_tot
        quote.grand_total = subtotal + vat_tot

        db.session.commit()
        log_action("Yeni Teklif Oluşturuldu", "Satış Modülü", f"Teklif No: {q_num}")
        flash('Teklif başarıyla oluşturuldu.', 'success')
        return redirect(url_for('sales.list_quotes'))

    customers = Customer.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()
    return render_template('sales/quote_form.html', customers=customers, products=products)


@sales_bp.route('/quotes/<int:quote_id>/convert', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli')
def convert_quote(quote_id):
    warehouse_id = int(request.form.get('warehouse_id'))
    try:
        order = convert_quote_to_order(quote_id, warehouse_id, current_user.id)
        flash(f'Teklif başarıyla {order.order_number} numaralı siparişe dönüştürüldü.', 'success')
        return redirect(url_for('sales.order_detail', order_id=order.id))
    except Exception as e:
        flash(f'Dönüştürme hatası: {str(e)}', 'danger')
        return redirect(url_for('sales.list_quotes'))


# --- ORDERS ---
@sales_bp.route('/orders')
@login_required
def list_orders():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    query = SalesOrder.query

    if search:
        query = query.join(Customer).filter(
            (SalesOrder.order_number.ilike(f'%{search}%')) |
            (Customer.company_name.ilike(f'%{search}%'))
        )
    if status:
        query = query.filter(SalesOrder.status == status)

    orders = query.order_by(SalesOrder.created_at.desc()).all()
    return render_template('sales/orders.html', orders=orders, search=search, selected_status=status)


@sales_bp.route('/orders/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli')
def create_order():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        warehouse_id = int(request.form.get('warehouse_id'))
        items_json = request.form.get('items_json')
        notes = request.form.get('notes', '').strip()

        items = json.loads(items_json) if items_json else []
        if not items:
            flash('En az bir ürün eklenmelidir.', 'danger')
            return redirect(url_for('sales.create_order'))

        cust = Customer.query.get(customer_id)
        o_num = generate_document_number("SIP")

        order = SalesOrder(
            order_number=o_num,
            customer_id=customer_id,
            warehouse_id=warehouse_id,
            order_date=datetime.utcnow().date(),
            status='Beklemede',
            shipping_address=cust.address if cust else None,
            created_by_id=current_user.id,
            notes=notes
        )
        db.session.add(order)
        db.session.flush()

        subtotal = 0.0
        vat_tot = 0.0

        for item in items:
            p_id = int(item['product_id'])
            qty = float(item['quantity'])
            price = float(item['unit_price'])
            vat = float(item['vat_rate'])

            tot = qty * price
            v_val = tot * (vat / 100.0)
            subtotal += tot
            vat_tot += v_val

            oitem = SalesOrderItem(
                order_id=order.id,
                product_id=p_id,
                quantity=qty,
                unit_price=price,
                vat_rate=vat,
                total_price=tot
            )
            db.session.add(oitem)

        order.subtotal = subtotal
        order.vat_amount = vat_tot
        order.grand_total = subtotal + vat_tot

        db.session.commit()

        # Check stock validity
        has_stock, warnings = validate_order_stock(order.id)
        if not has_stock:
            flash(f"Sipariş kaydedildi fakat STOK UYARISI var: {', '.join(warnings)}", 'warning')
        else:
            flash('Satış siparişi başarıyla eklendi.', 'success')

        log_action("Yeni Satış Siparişi", "Satış Modülü", f"Sipariş No: {o_num}")
        return redirect(url_for('sales.order_detail', order_id=order.id))

    customers = Customer.query.filter_by(is_active=True).all()
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()

    return render_template('sales/order_form.html', customers=customers, warehouses=warehouses, products=products)


@sales_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    has_stock, warnings = validate_order_stock(order.id)
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    return render_template('sales/order_detail.html', order=order, has_stock=has_stock, warnings=warnings, warehouses=warehouses)


@sales_bp.route('/orders/<int:order_id>/approve', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli')
def approve_order(order_id):
    order = SalesOrder.query.get_or_404(order_id)
    order.status = 'Onaylandı'
    db.session.commit()
    log_action("Sipariş Onaylandı", "Satış Modülü", f"Sipariş: {order.order_number}")
    flash('Sipariş başarıyla onaylandı.', 'success')
    return redirect(url_for('sales.order_detail', order_id=order.id))


@sales_bp.route('/orders/<int:order_id>/invoice', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Muhasebe')
def create_invoice(order_id):
    try:
        inv = create_invoice_from_sales_order(order_id, current_user.id)
        flash(f'Satış Faturası ({inv.invoice_number}) başarıyla oluşturuldu ve cari hesaba işlendi.', 'success')
        return redirect(url_for('finance.invoice_detail', invoice_id=inv.id))
    except Exception as e:
        flash(f'Fatura hatası: {str(e)}', 'danger')
        return redirect(url_for('sales.order_detail', order_id=order_id))
