from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.warehouse import StockMovement, Warehouse, WarehouseStock
from app.models.product import StockLot, Product
from app.services.stock_service import record_stock_movement
from app.services.audit_service import log_action
from app.utils.decorators import role_required

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/movements')
@login_required
def movements():
    search = request.args.get('search', '').strip()
    m_type = request.args.get('movement_type', '').strip()
    wh_id = request.args.get('warehouse_id', type=int)

    query = StockMovement.query

    if search:
        query = query.join(Product).filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.code.ilike(f'%{search}%')) |
            (StockMovement.movement_code.ilike(f'%{search}%')) |
            (StockMovement.reference_number.ilike(f'%{search}%'))
        )
    if m_type:
        query = query.filter(StockMovement.movement_type == m_type)
    if wh_id:
        query = query.filter(StockMovement.warehouse_id == wh_id)

    movements_list = query.order_by(StockMovement.created_at.desc()).all()
    warehouses = Warehouse.query.all()

    return render_template(
        'inventory/movements.html',
        movements=movements_list,
        search=search,
        selected_type=m_type,
        selected_warehouse=wh_id,
        warehouses=warehouses
    )


@inventory_bp.route('/lots')
@login_required
def lots():
    search = request.args.get('search', '').strip()
    wh_id = request.args.get('warehouse_id', type=int)

    query = StockLot.query.join(Product)

    if search:
        query = query.filter(
            (StockLot.lot_number.ilike(f'%{search}%')) |
            (Product.name.ilike(f'%{search}%')) |
            (Product.code.ilike(f'%{search}%'))
        )
    if wh_id:
        query = query.filter(StockLot.warehouse_id == wh_id)

    lots_list = query.order_by(StockLot.expiration_date.asc()).all()
    warehouses = Warehouse.query.all()
    today = datetime.utcnow().date()

    return render_template(
        'inventory/lots.html',
        lots=lots_list,
        today=today,
        search=search,
        selected_warehouse=wh_id,
        warehouses=warehouses
    )


@inventory_bp.route('/adjust', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def adjust():
    if request.method == 'POST':
        product_id = int(request.form.get('product_id'))
        warehouse_id = int(request.form.get('warehouse_id'))
        adj_type = request.form.get('adjustment_type') # MANUEL_GIRIS, MANUEL_CIKIS, FIRE
        quantity = float(request.form.get('quantity') or 0.0)
        notes = request.form.get('notes', '').strip()

        try:
            record_stock_movement(
                product_id=product_id,
                warehouse_id=warehouse_id,
                movement_type=adj_type,
                quantity=quantity,
                user_id=current_user.id,
                notes=f"Düzeltme/Fire: {notes}"
            )
            flash('Stok düzeltme işlemi kaydedildi ve loglandı.', 'success')
            return redirect(url_for('inventory.movements'))
        except Exception as e:
            flash(f'İşlem hatası: {str(e)}', 'danger')

    products = Product.query.filter_by(is_active=True).all()
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    return render_template('inventory/adjust.html', products=products, warehouses=warehouses)
