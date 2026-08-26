from datetime import datetime
import uuid
from app import db
from app.models.purchase import PurchaseOrder, PurchaseOrderItem
from app.services.stock_service import record_stock_movement, create_or_update_lot
from app.services.audit_service import log_action

def process_goods_receipt(order_id, item_receipts, user_id=None):
    """
    Processes goods receipt (Mal Kabul Yapıldı):
    - Increases stock in target warehouse via SATIN_ALMA_GIRISI movement
    - Creates LOT record with expiration date
    - Updates order item received_quantity and status
    """
    order = PurchaseOrder.query.get(order_id)
    if not order:
        raise ValueError("Satın alma siparişi bulunamadı.")

    all_received = True
    for item in order.items:
        receipt = item_receipts.get(str(item.id)) or item_receipts.get(item.id)
        if receipt:
            qty_received = float(receipt.get('quantity', 0))
            lot_num = receipt.get('lot_number')
            exp_date = receipt.get('expiration_date')

            if qty_received > 0:
                item.received_quantity += qty_received
                item.lot_number = lot_num or f"LOT-{datetime.utcnow().strftime('%Y%m%d')}-{item.id}"
                
                # Create stock lot if expiration date is present
                lot_obj = None
                if exp_date:
                    lot_obj = create_or_update_lot(
                        product_id=item.product_id,
                        warehouse_id=order.warehouse_id,
                        lot_number=item.lot_number,
                        expiration_date=exp_date,
                        quantity=qty_received
                    )

                # Record stock movement
                record_stock_movement(
                    product_id=item.product_id,
                    warehouse_id=order.warehouse_id,
                    movement_type='SATIN_ALMA_GIRISI',
                    quantity=qty_received,
                    unit_price=item.unit_price,
                    lot_id=lot_obj.id if lot_obj else None,
                    reference_number=order.order_number,
                    user_id=user_id,
                    notes=f"Mal kabul yapıldı: {order.order_number}"
                )

        if item.received_quantity < item.quantity:
            all_received = False

    if all_received:
        order.status = 'Mal Kabul Yapıldı'
    else:
        order.status = 'Kısmi Mal Kabul'

    db.session.commit()
    log_action("Mal Kabul Yapıldı", "Satın Alma", f"Sipariş: {order.order_number} Mal kabul edildi.")
    return order
