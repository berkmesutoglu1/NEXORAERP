from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import json
from app import db
from app.models.purchase import PurchaseRequest, PurchaseOrder, PurchaseOrderItem
from app.models.party import Supplier
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.services.purchase_service import process_goods_receipt
from app.services.sales_service import generate_document_number
from app.services.audit_service import log_action
from app.utils.decorators import role_required

purchases_bp = Blueprint('purchases', __name__)

@purchases_bp.route('/requests')
@login_required
def requests_list():
    reqs = PurchaseRequest.query.order_by(PurchaseRequest.created_at.desc()).all()
    return render_template('purchases/requests.html', requests=reqs)


@purchases_bp.route('/orders')
@login_required
def list_orders():
    orders = PurchaseOrder.query.order_by(PurchaseOrder.created_at.desc()).all()
    return render_template('purchases/orders.html', orders=orders)


@purchases_bp.route('/orders/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici')
def create_order():
    if request.method == 'POST':
        supplier_id = int(request.form.get('supplier_id'))
        warehouse_id = int(request.form.get('warehouse_id'))
        items_json = request.form.get('items_json')
        notes = request.form.get('notes', '').strip()

        items = json.loads(items_json) if items_json else []
        if not items:
            flash('En az bir ürün seçmelisiniz.', 'danger')
            return redirect(url_for('purchases.create_order'))

        p_num = generate_document_number("SAT")
        order = PurchaseOrder(
            order_number=p_num,
            supplier_id=supplier_id,
            warehouse_id=warehouse_id,
            order_date=datetime.utcnow().date(),
            status='Sipariş Verildi',
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

            pitem = PurchaseOrderItem(
                order_id=order.id,
                product_id=p_id,
                quantity=qty,
                unit_price=price,
                vat_rate=vat,
                total_price=tot,
                lot_number=item.get('lot_number'),
                expiration_date=datetime.strptime(item['expiration_date'], '%Y-%m-%d').date() if item.get('expiration_date') else None
            )
            db.session.add(pitem)

        order.subtotal = subtotal
        order.vat_amount = vat_tot
        order.grand_total = subtotal + vat_tot

        db.session.commit()
        log_action("Yeni Satın Alma Siparişi", "Satın Alma", f"Sipariş No: {p_num}")
        flash('Satın alma siparişi oluşturuldu.', 'success')
        return redirect(url_for('purchases.order_detail', order_id=order.id))

    suppliers = Supplier.query.filter_by(is_active=True).all()
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()

    return render_template('purchases/order_form.html', suppliers=suppliers, warehouses=warehouses, products=products)


@purchases_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)
    return render_template('purchases/order_detail.html', order=order)


@purchases_bp.route('/orders/<int:order_id>/goods-receipt', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def goods_receipt(order_id):
    order = PurchaseOrder.query.get_or_404(order_id)

    item_receipts = {}
    for item in order.items:
        qty = request.form.get(f'qty_{item.id}')
        lot = request.form.get(f'lot_{item.id}')
        exp = request.form.get(f'exp_{item.id}')
        if qty:
            item_receipts[str(item.id)] = {
                'quantity': qty,
                'lot_number': lot,
                'expiration_date': exp
            }

    try:
        process_goods_receipt(order.id, item_receipts, current_user.id)
        flash('Mal kabul yapıldı. Stoklar ve LOT bilgileri depoya işlendi!', 'success')
    except Exception as e:
        flash(f'Mal kabul hatası: {str(e)}', 'danger')

    return redirect(url_for('purchases.order_detail', order_id=order.id))
