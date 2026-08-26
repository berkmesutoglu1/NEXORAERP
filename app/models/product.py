from datetime import datetime
from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    products = db.relationship('Product', backref='brand', lazy=True)

    def __repr__(self):
        return f'<Brand {self.name}>'


class Unit(db.Model):
    __tablename__ = 'units'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False) # Koli, Adet, Kg, Litre, Ton, Paket, Kutu
    symbol = db.Column(db.String(10), nullable=False)

    products = db.relationship('Product', backref='unit', lazy=True)

    def __repr__(self):
        return f'<Unit {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(50), unique=True, nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    
    purchase_price = db.Column(db.Float, default=0.0)
    sale_price = db.Column(db.Float, default=0.0)
    vat_rate = db.Column(db.Float, default=20.0) # KDV % (1, 10, 20)
    min_stock_level = db.Column(db.Float, default=10.0)
    max_stock_level = db.Column(db.Float, default=1000.0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    stock_lots = db.relationship('StockLot', backref='product', lazy=True, cascade="all, delete-orphan")
    warehouse_stocks = db.relationship('WarehouseStock', backref='product', lazy=True, cascade="all, delete-orphan")
    stock_movements = db.relationship('StockMovement', backref='product', lazy=True)

    @property
    def total_stock(self):
        return sum(ws.quantity for ws in self.warehouse_stocks)

    @property
    def profit_margin(self):
        if self.purchase_price and self.purchase_price > 0:
            return round(((self.sale_price - self.purchase_price) / self.purchase_price) * 100, 2)
        return 0.0

    def __repr__(self):
        return f'<Product {self.code} - {self.name}>'


class StockLot(db.Model):
    __tablename__ = 'stock_lots'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    lot_number = db.Column(db.String(50), nullable=False, index=True)
    production_date = db.Column(db.Date, nullable=True)
    expiration_date = db.Column(db.Date, nullable=False, index=True) # SKT
    quantity = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StockLot {self.lot_number} - Expiry: {self.expiration_date}>'
