from datetime import datetime, date
import uuid
from app import db
from app.models.product import Product, StockLot
from app.models.warehouse import Warehouse, WarehouseStock, StockMovement
from app.services.audit_service import log_action

def generate_movement_code(prefix="STK"):
    unique = str(uuid.uuid4().hex[:8]).upper()
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d')}-{unique}"

def record_stock_movement(product_id, warehouse_id, movement_type, quantity, unit_price=0.0, 
                          target_warehouse_id=None, lot_id=None, reference_number=None, user_id=None, notes=None):
    """
    Executes atomic stock movement:
    - Movement Types: SATIN_ALMA_GIRISI, SATIS_CIKISI, DEPO_TRANSFERI, MANUEL_GIRIS, MANUEL_CIKIS, IADE, FIRE
    - Updates WarehouseStock
    - Creates StockMovement record
    """
    product = Product.query.get(product_id)
    warehouse = Warehouse.query.get(warehouse_id)
    
    if not product or not warehouse:
        raise ValueError("Ürün veya Depo bulunamadı.")

    # Get or create WarehouseStock
    ws = WarehouseStock.query.filter_by(warehouse_id=warehouse_id, product_id=product_id).first()
    if not ws:
        ws = WarehouseStock(warehouse_id=warehouse_id, product_id=product_id, quantity=0.0)
        db.session.add(ws)

    # Process movement according to type
    if movement_type in ['SATIN_ALMA_GIRISI', 'MANUEL_GIRIS', 'IADE']:
        ws.quantity += float(quantity)
    elif movement_type in ['SATIS_CIKISI', 'MANUEL_CIKIS', 'FIRE']:
        if ws.quantity < float(quantity):
            # Log warning or allow negative stock if configured
            pass
        ws.quantity -= float(quantity)
    elif movement_type == 'DEPO_TRANSFERI':
        if not target_warehouse_id:
            raise ValueError("Hedef depo belirtilmelidir.")
        
        target_wh = Warehouse.query.get(target_warehouse_id)
        if not target_wh:
            raise ValueError("Hedef depo bulunamadı.")
            
        # Deduct from source warehouse
        ws.quantity -= float(quantity)
        
        # Add to target warehouse
        target_ws = WarehouseStock.query.filter_by(warehouse_id=target_warehouse_id, product_id=product_id).first()
        if not target_ws:
            target_ws = WarehouseStock(warehouse_id=target_warehouse_id, product_id=product_id, quantity=0.0)
            db.session.add(target_ws)
        target_ws.quantity += float(quantity)

    code = generate_movement_code()
    movement = StockMovement(
        movement_code=code,
        movement_type=movement_type,
        product_id=product_id,
        warehouse_id=warehouse_id,
        target_warehouse_id=target_warehouse_id,
        lot_id=lot_id,
        quantity=float(quantity),
        unit_price=float(unit_price),
        reference_number=reference_number,
        user_id=user_id,
        notes=notes
    )
    db.session.add(movement)
    db.session.commit()
    
    log_action(
        action=f"Stok Hareketi: {movement_type}",
        module="Stok Yönetimi",
        description=f"{product.name} ({quantity} {product.unit.symbol if product.unit else 'Adet'}) - Depo: {warehouse.name}"
    )
    return movement


def create_or_update_lot(product_id, warehouse_id, lot_number, expiration_date, quantity, production_date=None):
    """
    Creates or updates a stock LOT with expiration date (SKT).
    """
    if isinstance(expiration_date, str):
        expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()
    if production_date and isinstance(production_date, str):
        production_date = datetime.strptime(production_date, '%Y-%m-%d').date()

    lot = StockLot.query.filter_by(
        product_id=product_id,
        warehouse_id=warehouse_id,
        lot_number=lot_number
    ).first()

    if lot:
        lot.quantity += float(quantity)
        if expiration_date:
            lot.expiration_date = expiration_date
    else:
        lot = StockLot(
            product_id=product_id,
            warehouse_id=warehouse_id,
            lot_number=lot_number,
            production_date=production_date,
            expiration_date=expiration_date,
            quantity=float(quantity)
        )
        db.session.add(lot)
    
    db.session.commit()
    return lot
