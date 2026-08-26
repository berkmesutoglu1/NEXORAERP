from datetime import datetime
from app import db

class PurchaseRequest(db.Model):
    __tablename__ = 'purchase_requests'

    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    needed_by_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='Beklemede') # Beklemede, Onaylandı, Reddedildi
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requested_by = db.relationship('User', backref='purchase_requests', lazy=True)
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<PurchaseRequest {self.request_number} - Status: {self.status}>'


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    
    order_date = db.Column(db.Date, default=datetime.utcnow)
    delivery_date = db.Column(db.Date, nullable=True)
    
    subtotal = db.Column(db.Float, default=0.0)
    vat_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(50), default='Beklemede') 
    # Taslak, Beklemede, Sipariş Verildi, Mal Kabul Yapıldı, Tamamlandı, İptal
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('PurchaseOrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    warehouse = db.relationship('Warehouse', backref='purchase_orders', lazy=True)
    created_by = db.relationship('User', backref='created_purchase_orders', lazy=True)
    invoices = db.relationship('Invoice', backref='purchase_order', lazy=True)

    def __repr__(self):
        return f'<PurchaseOrder {self.order_number} - Status: {self.status}>'


class PurchaseOrderItem(db.Model):
    __tablename__ = 'purchase_order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    received_quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    discount_rate = db.Column(db.Float, default=0.0)
    vat_rate = db.Column(db.Float, default=20.0)
    total_price = db.Column(db.Float, default=0.0)
    
    lot_number = db.Column(db.String(50), nullable=True)
    expiration_date = db.Column(db.Date, nullable=True) # SKT

    # Relationships
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<PurchaseOrderItem Order:{self.order_id} Product:{self.product_id}>'
