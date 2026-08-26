from datetime import datetime
import uuid
from app import db
from app.models.finance import (Invoice, InvoiceItem, CurrentAccount, 
                                CurrentTransaction, Collection, Payment, CashRegister)
from app.models.party import Customer, Supplier
from app.services.audit_service import log_action

def get_or_create_current_account(party_type, party_id):
    """
    Returns existing CurrentAccount or creates a new one for customer or supplier.
    """
    if party_type == 'MUSTERI':
        acc = CurrentAccount.query.filter_by(customer_id=party_id).first()
        if not acc:
            acc = CurrentAccount(party_type='MUSTERI', customer_id=party_id, total_debit=0.0, total_credit=0.0, balance=0.0)
            db.session.add(acc)
            db.session.commit()
        return acc
    elif party_type == 'TEDARIKCI':
        acc = CurrentAccount.query.filter_by(supplier_id=party_id).first()
        if not acc:
            acc = CurrentAccount(party_type='TEDARIKCI', supplier_id=party_id, total_debit=0.0, total_credit=0.0, balance=0.0)
            db.session.add(acc)
            db.session.commit()
        return acc
    return None


def record_current_transaction(current_account_id, transaction_type, document_number, debit=0.0, credit=0.0, description="", user_id=None):
    """
    Records a current transaction (Cari Hareket) and updates the CurrentAccount total_debit, total_credit, and balance.
    """
    acc = CurrentAccount.query.get(current_account_id)
    if not acc:
        raise ValueError("Cari hesap bulunamadı.")

    acc.total_debit += float(debit)
    acc.total_credit += float(credit)
    acc.balance = acc.total_debit - acc.total_credit

    tx = CurrentTransaction(
        current_account_id=acc.id,
        transaction_type=transaction_type,
        document_number=document_number,
        date=datetime.utcnow(),
        debit=float(debit),
        credit=float(credit),
        balance_after=acc.balance,
        description=description,
        created_by_id=user_id
    )
    db.session.add(tx)
    db.session.commit()
    return tx


def create_invoice_from_sales_order(sales_order_id, user_id=None):
    """
    Generates a Sales Invoice from SalesOrder and updates Customer Current Account ledger.
    """
    from app.models.sales import SalesOrder
    order = SalesOrder.query.get(sales_order_id)
    if not order:
        raise ValueError("Satış siparişi bulunamadı.")

    inv_num = f"FAT-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4().hex[:6]).upper()}"
    invoice = Invoice(
        invoice_number=inv_num,
        invoice_type='SATIS',
        customer_id=order.customer_id,
        sales_order_id=order.id,
        issue_date=datetime.utcnow().date(),
        due_date=datetime.utcnow().date(),
        subtotal=order.subtotal,
        vat_amount=order.vat_amount,
        discount_amount=order.discount_amount,
        grand_total=order.grand_total,
        paid_amount=0.0,
        payment_status='ODENMEDI',
        created_by_id=user_id,
        notes=f"Siparişten oluşturuldu: {order.order_number}"
    )
    db.session.add(invoice)
    db.session.flush()

    for sitem in order.items:
        iitem = InvoiceItem(
            invoice_id=invoice.id,
            product_id=sitem.product_id,
            quantity=sitem.quantity,
            unit_price=sitem.unit_price,
            vat_rate=sitem.vat_rate,
            total_price=sitem.total_price
        )
        db.session.add(iitem)

    # Update Customer Current Account: Sales Invoice adds Debit (Borç) to Customer
    acc = get_or_create_current_account('MUSTERI', order.customer_id)
    record_current_transaction(
        current_account_id=acc.id,
        transaction_type='FATURA',
        document_number=inv_num,
        debit=order.grand_total,
        credit=0.0,
        description=f"Satış Faturası: {inv_num}",
        user_id=user_id
    )

    db.session.commit()
    log_action("Satış Faturası Kesildi", "Finans & Fatura", f"Fatura: {inv_num} - Tutar: ₺{order.grand_total:,.2f}")
    return invoice


def process_collection(customer_id, amount, payment_method, reference_number=None, cash_register_id=None, description="", user_id=None):
    """
    Processes Customer Collection (Tahsilat):
    - Creates Collection record
    - Updates Customer Current Account (Adds Credit / Alacak, reduces debt)
    - Updates CashRegister balance
    - Allocates to unpaid invoices
    """
    customer = Customer.query.get(customer_id)
    if not customer:
        raise ValueError("Müşteri bulunamadı.")

    col_num = f"THS-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4().hex[:6]).upper()}"
    acc = get_or_create_current_account('MUSTERI', customer_id)

    collection = Collection(
        collection_number=col_num,
        customer_id=customer_id,
        current_account_id=acc.id,
        date=datetime.utcnow().date(),
        amount=float(amount),
        payment_method=payment_method,
        reference_number=reference_number,
        cash_register_id=cash_register_id,
        description=description,
        created_by_id=user_id
    )
    db.session.add(collection)

    # Update Cash Register balance if specified
    if cash_register_id:
        cr = CashRegister.query.get(cash_register_id)
        if cr:
            cr.balance += float(amount)

    # Record Current Transaction: Collection adds Credit (Alacak)
    record_current_transaction(
        current_account_id=acc.id,
        transaction_type='TAHSILAT',
        document_number=col_num,
        debit=0.0,
        credit=float(amount),
        description=f"Tahsilat ({payment_method}): {description or col_num}",
        user_id=user_id
    )

    # Auto-allocate to unpaid sales invoices
    unpaid_invoices = Invoice.query.filter_by(customer_id=customer_id, invoice_type='SATIS')\
        .filter(Invoice.payment_status != 'ODENDI').order_by(Invoice.issue_date.asc()).all()
    
    remaining_col = float(amount)
    for inv in unpaid_invoices:
        if remaining_col <= 0:
            break
        needed = inv.grand_total - inv.paid_amount
        if remaining_col >= needed:
            inv.paid_amount += needed
            inv.payment_status = 'ODENDI'
            remaining_col -= needed
        else:
            inv.paid_amount += remaining_col
            inv.payment_status = 'KISMEN_ODENDI'
            remaining_col = 0.0

    db.session.commit()
    log_action("Tahsilat Alındı", "Finans & Tahsilat", f"Müşteri: {customer.company_name} - Tutar: ₺{amount:,.2f}")
    return collection


def process_payment(supplier_id, amount, payment_method, reference_number=None, cash_register_id=None, description="", user_id=None):
    """
    Processes Supplier Payment (Ödeme):
    - Creates Payment record
    - Updates Supplier Current Account
    - Updates CashRegister balance
    """
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        raise ValueError("Tedarikçi bulunamadı.")

    pay_num = f"ODM-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4().hex[:6]).upper()}"
    acc = get_or_create_current_account('TEDARIKCI', supplier_id)

    payment = Payment(
        payment_number=pay_num,
        supplier_id=supplier_id,
        current_account_id=acc.id,
        date=datetime.utcnow().date(),
        amount=float(amount),
        payment_method=payment_method,
        reference_number=reference_number,
        cash_register_id=cash_register_id,
        description=description,
        created_by_id=user_id
    )
    db.session.add(payment)

    if cash_register_id:
        cr = CashRegister.query.get(cash_register_id)
        if cr:
            cr.balance -= float(amount)

    # Record Current Transaction: Supplier payment adds Credit (Alacak) for supplier
    record_current_transaction(
        current_account_id=acc.id,
        transaction_type='ODEME',
        document_number=pay_num,
        debit=0.0,
        credit=float(amount),
        description=f"Tedarikçi Ödemesi ({payment_method}): {description or pay_num}",
        user_id=user_id
    )

    db.session.commit()
    log_action("Tedarikçi Ödemesi Yapıldı", "Finans & Ödeme", f"Tedarikçi: {supplier.company_name} - Tutar: ₺{amount:,.2f}")
    return payment
