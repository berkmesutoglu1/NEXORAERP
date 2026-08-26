from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.warehouse import Warehouse, WarehouseStock, StockMovement
from app.models.product import Product
from app.services.stock_service import record_stock_movement
from app.services.audit_service import log_action
from app.utils.decorators import role_required

warehouses_bp = Blueprint('warehouses', __name__)

@warehouses_bp.route('/')
@login_required
def list_warehouses():
    warehouses = Warehouse.query.all()
    return render_template('warehouses/list.html', warehouses=warehouses)


@warehouses_bp.route('/create', methods=['POST'])
@login_required
@role_required('Admin', 'Yönetici')
def create_warehouse():
    code = request.form.get('code', '').strip()
    name = request.form.get('name', '').strip()
    manager = request.form.get('manager_name', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()

    if Warehouse.query.filter_by(code=code).first():
        flash('Bu depo kodu kullanılıyor.', 'danger')
        return redirect(url_for('warehouses.list_warehouses'))

    wh = Warehouse(code=code, name=name, manager_name=manager, address=address, phone=phone)
    db.session.add(wh)
    db.session.commit()

    log_action("Yeni Depo Tanımlandı", "Depo Yönetimi", f"{wh.code} - {wh.name}")
    flash('Depo başarıyla tanımlandı.', 'success')
    return redirect(url_for('warehouses.list_warehouses'))


@warehouses_bp.route('/<int:warehouse_id>')
@login_required
def detail(warehouse_id):
    wh = Warehouse.query.get_or_404(warehouse_id)
    stocks = WarehouseStock.query.filter_by(warehouse_id=wh.id).all()
    return render_template('warehouses/detail.html', warehouse=wh, stocks=stocks)


@warehouses_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def transfer():
    if request.method == 'POST':
        source_wh_id = int(request.form.get('source_warehouse_id'))
        target_wh_id = int(request.form.get('target_warehouse_id'))
        product_id = int(request.form.get('product_id'))
        quantity = float(request.form.get('quantity') or 0.0)
        notes = request.form.get('notes', '').strip()

        if source_wh_id == target_wh_id:
            flash('Kaynak depo ile hedef depo aynı olamaz.', 'danger')
            return redirect(url_for('warehouses.transfer'))

        # Check source warehouse stock
        ws = WarehouseStock.query.filter_by(warehouse_id=source_wh_id, product_id=product_id).first()
        if not ws or ws.available_quantity < quantity:
            flash('Kaynak depoda yeterli stok bulunmuyor!', 'danger')
            return redirect(url_for('warehouses.transfer'))

        try:
            record_stock_movement(
                product_id=product_id,
                warehouse_id=source_wh_id,
                movement_type='DEPO_TRANSFERI',
                quantity=quantity,
                target_warehouse_id=target_wh_id,
                user_id=current_user.id,
                notes=notes
            )
            flash('Depolar arası stok transferi başarıyla tamamlandı.', 'success')
            return redirect(url_for('inventory.movements'))
        except Exception as e:
            flash(f'Transfer sırasında hata oluştu: {str(e)}', 'danger')

    warehouses = Warehouse.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()
    return render_template('warehouses/transfer.html', warehouses=warehouses, products=products)
