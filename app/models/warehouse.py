from datetime import datetime
from app import db

class Warehouse(db.Model):
    __tablename__ = 'warehouses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    manager_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    stocks = db.relationship('WarehouseStock', backref='warehouse', lazy=True, cascade="all, delete-orphan")
    lots = db.relationship('StockLot', backref='warehouse', lazy=True)
    movements_from = db.relationship('StockMovement', foreign_keys='StockMovement.warehouse_id', backref='source_warehouse', lazy=True)
    movements_to = db.relationship('StockMovement', foreign_keys='StockMovement.target_warehouse_id', backref='target_warehouse', lazy=True)

    def __repr__(self):
        return f'<Warehouse {self.code} - {self.name}>'


class WarehouseStock(db.Model):
    __tablename__ = 'warehouse_stocks'

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    reserved_quantity = db.Column(db.Float, default=0.0)

    __table_args__ = (
        db.UniqueConstraint('warehouse_id', 'product_id', name='_warehouse_product_uc'),
    )

    @property
    def available_quantity(self):
        return max(0.0, self.quantity - self.reserved_quantity)

    def __repr__(self):
        return f'<WarehouseStock Warehouse:{self.warehouse_id} Product:{self.product_id} Qty:{self.quantity}>'


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    movement_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    movement_type = db.Column(db.String(50), nullable=False) 
    # SATIN_ALMA_GIRISI, SATIS_CIKISI, DEPO_TRANSFERI, MANUEL_GIRIS, MANUEL_CIKIS, IADE, FIRE
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    target_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('stock_lots.id'), nullable=True)
    
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, default=0.0)
    reference_number = db.Column(db.String(100), nullable=True) # Invoice / Order / Document No
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    lot = db.relationship('StockLot', backref='movements', lazy=True)
    user = db.relationship('User', backref='stock_movements', lazy=True)

    def __repr__(self):
        return f'<StockMovement {self.movement_code} - Type: {self.movement_type}>'
