from datetime import datetime
from app import db

class SalesQuote(db.Model):
    __tablename__ = 'sales_quotes'

    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    valid_until = db.Column(db.Date, nullable=True)
    
    subtotal = db.Column(db.Float, default=0.0)
    vat_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(50), default='Taslak') 
    # Taslak, Gönderildi, Onaylandı, Reddedildi, Siparişe Dönüştü
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('SalesQuoteItem', backref='quote', lazy=True, cascade="all, delete-orphan")
    created_by = db.relationship('User', backref='created_quotes', lazy=True)
    sales_orders = db.relationship('SalesOrder', backref='source_quote', lazy=True)

    def __repr__(self):
        return f'<SalesQuote {self.quote_number} - Status: {self.status}>'


class SalesQuoteItem(db.Model):
    __tablename__ = 'sales_quote_items'

    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('sales_quotes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    discount_rate = db.Column(db.Float, default=0.0) # %
    vat_rate = db.Column(db.Float, default=20.0)      # %
    total_price = db.Column(db.Float, default=0.0)

    # Relationships
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<SalesQuoteItem Quote:{self.quote_id} Product:{self.product_id}>'


class SalesOrder(db.Model):
    __tablename__ = 'sales_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('sales_quotes.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    
    order_date = db.Column(db.Date, default=datetime.utcnow)
    delivery_date = db.Column(db.Date, nullable=True)
    
    subtotal = db.Column(db.Float, default=0.0)
    vat_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    
    status = db.Column(db.String(50), default='Beklemede')
    # Taslak, Beklemede, Onaylandı, Hazırlanıyor, Sevk Edildi, Teslim Edildi, İptal
    
    shipping_address = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('SalesOrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    warehouse = db.relationship('Warehouse', backref='sales_orders', lazy=True)
    created_by = db.relationship('User', backref='created_orders', lazy=True)
    shipments = db.relationship('Shipment', backref='sales_order', lazy=True)
    invoices = db.relationship('Invoice', backref='sales_order', lazy=True)

    def __repr__(self):
        return f'<SalesOrder {self.order_number} - Status: {self.status}>'


class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    shipped_quantity = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    discount_rate = db.Column(db.Float, default=0.0)
    vat_rate = db.Column(db.Float, default=20.0)
    total_price = db.Column(db.Float, default=0.0)

    # Relationships
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<SalesOrderItem Order:{self.order_id} Product:{self.product_id}>'
