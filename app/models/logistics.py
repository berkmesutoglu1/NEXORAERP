from datetime import datetime
from app import db

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    vehicle_type = db.Column(db.String(50), default='Kamyonet') # Kamyonet, Kamyon, Tır, Soğutuculu Araç (Frigo)
    brand_model = db.Column(db.String(100), nullable=True)
    capacity_kg = db.Column(db.Float, default=3500.0)
    is_active = db.Column(db.Boolean, default=True)

    shipments = db.relationship('Shipment', backref='vehicle', lazy=True)

    def __repr__(self):
        return f'<Vehicle {self.plate_number} - {self.vehicle_type}>'


class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    license_class = db.Column(db.String(20), default='C CE')
    is_active = db.Column(db.Boolean, default=True)

    shipments = db.relationship('Shipment', backref='driver', lazy=True)

    def __repr__(self):
        return f'<Driver {self.full_name}>'


class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    shipment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    
    shipment_date = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_delivery = db.Column(db.Date, nullable=True)
    delivery_address = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(50), default='Hazırlanıyor')
    # Hazırlanıyor, Yolda, Teslim Edildi, İptal
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('ShipmentItem', backref='shipment', lazy=True, cascade="all, delete-orphan")
    warehouse = db.relationship('Warehouse', backref='shipments', lazy=True)
    created_by = db.relationship('User', backref='created_shipments', lazy=True)

    def __repr__(self):
        return f'<Shipment {self.shipment_number} - Status: {self.status}>'


class ShipmentItem(db.Model):
    __tablename__ = 'shipment_items'

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('stock_lots.id'), nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=1.0)

    # Relationships
    product = db.relationship('Product', lazy=True)
    lot = db.relationship('StockLot', lazy=True)

    def __repr__(self):
        return f'<ShipmentItem Shipment:{self.shipment_id} Product:{self.product_id}>'
