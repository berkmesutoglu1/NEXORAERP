from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.logistics import Shipment, ShipmentItem, Vehicle, Driver
from app.models.sales import SalesOrder
from app.services.stock_service import record_stock_movement
from app.services.sales_service import generate_document_number
from app.services.audit_service import log_action
from app.utils.decorators import role_required

logistics_bp = Blueprint('logistics', __name__)

@logistics_bp.route('/shipments')
@login_required
def shipments():
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()

    query = Shipment.query

    if search:
        query = query.filter(Shipment.shipment_number.ilike(f'%{search}%'))
    if status:
        query = query.filter(Shipment.status == status)

    shipments_list = query.order_by(Shipment.created_at.desc()).all()
    return render_template('logistics/shipments.html', shipments=shipments_list, search=search, selected_status=status)


@logistics_bp.route('/shipments/create/<int:sales_order_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def create_shipment(sales_order_id):
    order = SalesOrder.query.get_or_404(sales_order_id)

    vehicle_id = request.form.get('vehicle_id', type=int)
    driver_id = request.form.get('driver_id', type=int)

    s_num = generate_document_number("SVK")
    shipment = Shipment(
        shipment_number=s_num,
        sales_order_id=order.id,
        customer_id=order.customer_id,
        warehouse_id=order.warehouse_id,
        vehicle_id=vehicle_id,
        driver_id=driver_id,
        shipment_date=datetime.utcnow(),
        delivery_address=order.shipping_address,
        status='Hazırlanıyor',
        created_by_id=current_user.id
    )
    db.session.add(shipment)
    db.session.flush()

    for oitem in order.items:
        sitem = ShipmentItem(
            shipment_id=shipment.id,
            product_id=oitem.product_id,
            quantity=oitem.quantity
        )
        db.session.add(sitem)

    order.status = 'Hazırlanıyor'
    db.session.commit()

    log_action("Sevkiyat Oluşturuldu", "Lojistik Modülü", f"Sevkiyat: {s_num} (Sipariş: {order.order_number})")
    flash('Sevkiyat kaydı oluşturuldu.', 'success')
    return redirect(url_for('logistics.shipment_detail', shipment_id=shipment.id))


@logistics_bp.route('/shipments/<int:shipment_id>')
@login_required
def shipment_detail(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    vehicles = Vehicle.query.filter_by(is_active=True).all()
    drivers = Driver.query.filter_by(is_active=True).all()
    return render_template('logistics/shipment_detail.html', shipment=shipment, vehicles=vehicles, drivers=drivers)


@logistics_bp.route('/shipments/<int:shipment_id>/status', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def update_shipment_status(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    new_status = request.form.get('status')

    old_status = shipment.status
    shipment.status = new_status

    if new_status == 'Teslim Edildi' and old_status != 'Teslim Edildi':
        # Deduct stock from warehouse when delivered!
        for sitem in shipment.items:
            record_stock_movement(
                product_id=sitem.product_id,
                warehouse_id=shipment.warehouse_id,
                movement_type='SATIS_CIKISI',
                quantity=sitem.quantity,
                reference_number=shipment.shipment_number,
                user_id=current_user.id,
                notes=f"Sevkiyat teslim edildi: {shipment.shipment_number}"
            )
        if shipment.sales_order:
            shipment.sales_order.status = 'Teslim Edildi'

    db.session.commit()
    log_action("Sevkiyat Durumu Güncellendi", "Lojistik Modülü", f"Sevkiyat: {shipment.shipment_number} -> {new_status}")
    flash(f'Sevkiyat durumu "{new_status}" olarak güncellendi.', 'success')
    return redirect(url_for('logistics.shipment_detail', shipment_id=shipment.id))


@logistics_bp.route('/vehicles')
@login_required
def vehicles():
    vehicles_list = Vehicle.query.all()
    drivers_list = Driver.query.all()
    return render_template('logistics/vehicles.html', vehicles=vehicles_list, drivers=drivers_list)
