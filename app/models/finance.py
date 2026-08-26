from datetime import datetime
from app import db

class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    invoice_type = db.Column(db.String(20), nullable=False) # SATIS, ALIS
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    
    sales_order_id = db.Column(db.Integer, db.ForeignKey('sales_orders.id'), nullable=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=True)
    
    issue_date = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=True)
    
    subtotal = db.Column(db.Float, default=0.0)
    vat_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    
    payment_status = db.Column(db.String(30), default='ODENMEDI') # ODENMEDI, KISMEN_ODENDI, ODENDI
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")
    created_by = db.relationship('User', backref='created_invoices', lazy=True)

    @property
    def remaining_amount(self):
        return max(0.0, self.grand_total - self.paid_amount)

    def __repr__(self):
        return f'<Invoice {self.invoice_number} - Type: {self.invoice_type}>'


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    vat_rate = db.Column(db.Float, default=20.0)
    total_price = db.Column(db.Float, default=0.0)

    # Relationships
    product = db.relationship('Product', lazy=True)

    def __repr__(self):
        return f'<InvoiceItem Invoice:{self.invoice_id} Product:{self.product_id}>'


class CurrentAccount(db.Model):
    __tablename__ = 'current_accounts'

    id = db.Column(db.Integer, primary_key=True)
    party_type = db.Column(db.String(20), nullable=False) # MUSTERI, TEDARIKCI
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True, unique=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True, unique=True)
    
    total_debit = db.Column(db.Float, default=0.0)  # Borç (Müşterinin firmamıza veya firmamızın tedarikçiye olan borcu)
    total_credit = db.Column(db.Float, default=0.0) # Alacak (Yapılan ödemeler/tahsilatlar)
    balance = db.Column(db.Float, default=0.0)      # Bakiye (total_debit - total_credit)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('CurrentTransaction', backref='current_account', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<CurrentAccount Type:{self.party_type} Balance:{self.balance}>'


class CurrentTransaction(db.Model):
    __tablename__ = 'current_transactions'

    id = db.Column(db.Integer, primary_key=True)
    current_account_id = db.Column(db.Integer, db.ForeignKey('current_accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False) # FATURA, TAHSILAT, ODEME, IADE, MANUEL
    document_number = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    debit = db.Column(db.Float, default=0.0)  # Borç tutarı
    credit = db.Column(db.Float, default=0.0) # Alacak tutarı
    balance_after = db.Column(db.Float, default=0.0)
    
    description = db.Column(db.String(255), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    created_by = db.relationship('User', backref='created_transactions', lazy=True)

    def __repr__(self):
        return f'<CurrentTransaction Doc:{self.document_number} Debit:{self.debit} Credit:{self.credit}>'


class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    collection_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    current_account_id = db.Column(db.Integer, db.ForeignKey('current_accounts.id'), nullable=False)
    
    date = db.Column(db.Date, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # NAKIT, HAVALE_EFT, KREDI_KARTI, CEK
    reference_number = db.Column(db.String(100), nullable=True)
    cash_register_id = db.Column(db.Integer, db.ForeignKey('cash_registers.id'), nullable=True)
    
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_by = db.relationship('User', backref='created_collections', lazy=True)
    cash_register = db.relationship('CashRegister', backref='collections', lazy=True)

    def __repr__(self):
        return f'<Collection {self.collection_number} - Amount: {self.amount}>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    current_account_id = db.Column(db.Integer, db.ForeignKey('current_accounts.id'), nullable=False)
    
    date = db.Column(db.Date, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # NAKIT, HAVALE_EFT, KREDI_KARTI, CEK
    reference_number = db.Column(db.String(100), nullable=True)
    cash_register_id = db.Column(db.Integer, db.ForeignKey('cash_registers.id'), nullable=True)
    
    description = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_by = db.relationship('User', backref='created_payments', lazy=True)
    cash_register = db.relationship('CashRegister', backref='payments', lazy=True)

    def __repr__(self):
        return f'<Payment {self.payment_number} - Amount: {self.amount}>'


class CashRegister(db.Model):
    __tablename__ = 'cash_registers'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), default='NAKIT_KASA') # NAKIT_KASA, BANKA_HESABI
    currency = db.Column(db.String(10), default='TRY')
    balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<CashRegister {self.code} - {self.name} Balance:{self.balance}>'
