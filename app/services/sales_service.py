from datetime import datetime
import uuid
from app import db
from app.models.sales import SalesQuote, SalesQuoteItem, SalesOrder, SalesOrderItem
from app.models.warehouse import WarehouseStock
from app.services.stock_service import record_stock_movement
from app.services.audit_service import log_action

def generate_document_number(prefix="SO"):
    unique = str(uuid.uuid4().hex[:6]).upper()
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m')}-{unique}"

def validate_order_stock(order_id):
    """
    Checks if warehouse has enough available stock for all order items.
    Returns (bool, list_of_warnings).
    """
    order = SalesOrder.query.get(order_id)
    if not order:
        return False, ["Sipariş bulunamadı."]

    warnings = []
    has_enough = True

    for item in order.items:
        ws = WarehouseStock.query.filter_by(warehouse_id=order.warehouse_id, product_id=item.product_id).first()
        available = ws.available_quantity if ws else 0.0
        if available < item.quantity:
            has_enough = False
            product_name = item.product.name if item.product else f"Ürün #{item.product_id}"
            warnings.append(f"'{product_name}' için stok yetersiz. İstenen: {item.quantity}, Mevcut: {available}")

    return has_enough, warnings


def convert_quote_to_order(quote_id, warehouse_id, user_id=None):
    """
    Converts approved SalesQuote to SalesOrder.
    """
    quote = SalesQuote.query.get(quote_id)
    if not quote:
        raise ValueError("Teklif bulunamadı.")

    order_num = generate_document_number("SIP")
    order = SalesOrder(
        order_number=order_num,
        quote_id=quote.id,
        customer_id=quote.customer_id,
        warehouse_id=warehouse_id,
        order_date=datetime.utcnow().date(),
        subtotal=quote.subtotal,
        vat_amount=quote.vat_amount,
        discount_amount=quote.discount_amount,
        grand_total=quote.grand_total,
        status='Beklemede',
        created_by_id=user_id,
        notes=f"Tekliften aktarıldı: {quote.quote_number}"
    )
    db.session.add(order)
    db.session.flush()

    for qitem in quote.items:
        oitem = SalesOrderItem(
            order_id=order.id,
            product_id=qitem.product_id,
            quantity=qitem.quantity,
            unit_price=qitem.unit_price,
            discount_rate=qitem.discount_rate,
            vat_rate=qitem.vat_rate,
            total_price=qitem.total_price
        )
        db.session.add(oitem)

    quote.status = 'Siparişe Dönüştü'
    db.session.commit()

    log_action("Teklif Siparişe Dönüştürüldü", "Satış Modülü", f"Teklif: {quote.quote_number} -> Sipariş: {order.order_number}")
    return order
