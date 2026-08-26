from datetime import datetime
from app import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(150), nullable=False, index=True)
    authorized_person = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    tax_number = db.Column(db.String(20), nullable=True)
    tax_office = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    customer_type = db.Column(db.String(50), default='Toptancı') # Toptancı, Market, Restoran, Otel, vb.
    risk_limit = db.Column(db.Float, default=0.0)
    payment_term_days = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    current_account = db.relationship('CurrentAccount', uselist=False, backref='customer', lazy=True)
    sales_quotes = db.relationship('SalesQuote', backref='customer', lazy=True)
    sales_orders = db.relationship('SalesOrder', backref='customer', lazy=True)
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    collections = db.relationship('Collection', backref='customer', lazy=True)
    shipments = db.relationship('Shipment', backref='customer', lazy=True)

    def __repr__(self):
        return f'<Customer {self.code} - {self.company_name}>'


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(150), nullable=False, index=True)
    authorized_person = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    tax_number = db.Column(db.String(20), nullable=True)
    tax_office = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    district = db.Column(db.String(50), nullable=True)
    payment_term_days = db.Column(db.Integer, default=30)
    iban = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    current_account = db.relationship('CurrentAccount', uselist=False, backref='supplier', lazy=True)
    products = db.relationship('Product', backref='supplier', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True)
    invoices = db.relationship('Invoice', backref='supplier', lazy=True)
    payments = db.relationship('Payment', backref='supplier', lazy=True)

    def __repr__(self):
        return f'<Supplier {self.code} - {self.company_name}>'
