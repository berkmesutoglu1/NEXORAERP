from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.finance import (Invoice, InvoiceItem, CurrentAccount, CurrentTransaction, 
                                Collection, Payment, CashRegister)
from app.models.party import Customer, Supplier
from app.services.finance_service import process_collection, process_payment
from app.services.audit_service import log_action
from app.utils.decorators import role_required

finance_bp = Blueprint('finance', __name__)

# --- INVOICES ---
@finance_bp.route('/invoices')
@login_required
def list_invoices():
    search = request.args.get('search', '').strip()
    inv_type = request.args.get('type', '').strip()
    status = request.args.get('status', '').strip()

    query = Invoice.query

    if search:
        query = query.filter(Invoice.invoice_number.ilike(f'%{search}%'))
    if inv_type:
        query = query.filter(Invoice.invoice_type == inv_type)
    if status:
        query = query.filter(Invoice.payment_status == status)

    invoices = query.order_by(Invoice.created_at.desc()).all()
    return render_template('finance/invoices.html', invoices=invoices, search=search, selected_type=inv_type, selected_status=status)


@finance_bp.route('/invoices/<int:invoice_id>')
@login_required
def invoice_detail(invoice_id):
    inv = Invoice.query.get_or_404(invoice_id)
    return render_template('finance/invoice_detail.html', invoice=inv)


# --- CURRENT ACCOUNTS (CARİ HESAPLAR) ---
@finance_bp.route('/current-accounts')
@login_required
def current_accounts():
    party_type = request.args.get('type', '').strip()
    search = request.args.get('search', '').strip()

    query = CurrentAccount.query

    if party_type:
        query = query.filter(CurrentAccount.party_type == party_type)

    accounts = query.all()
    return render_template('finance/current_accounts.html', accounts=accounts, selected_type=party_type, search=search)


# --- COLLECTIONS (TAHSİLAT) ---
@finance_bp.route('/collections', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Muhasebe')
def collections():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        amount = float(request.form.get('amount') or 0.0)
        payment_method = request.form.get('payment_method')
        ref_num = request.form.get('reference_number', '').strip()
        cash_reg_id = int(request.form.get('cash_register_id')) if request.form.get('cash_register_id') else None
        desc = request.form.get('description', '').strip()

        try:
            col = process_collection(
                customer_id=customer_id,
                amount=amount,
                payment_method=payment_method,
                reference_number=ref_num,
                cash_register_id=cash_reg_id,
                description=desc,
                user_id=current_user.id
            )
            flash(f'Tahsilat ({col.collection_number}) başarıyla kaydedildi.', 'success')
            return redirect(url_for('finance.collections'))
        except Exception as e:
            flash(f'Tahsilat kaydedilemedi: {str(e)}', 'danger')

    collections_list = Collection.query.order_by(Collection.created_at.desc()).all()
    customers = Customer.query.filter_by(is_active=True).all()
    cash_registers = CashRegister.query.filter_by(is_active=True).all()

    return render_template('finance/collections.html', collections=collections_list, customers=customers, cash_registers=cash_registers)


# --- PAYMENTS (ÖDEME) ---
@finance_bp.route('/payments', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Muhasebe')
def payments():
    if request.method == 'POST':
        supplier_id = int(request.form.get('supplier_id'))
        amount = float(request.form.get('amount') or 0.0)
        payment_method = request.form.get('payment_method')
        ref_num = request.form.get('reference_number', '').strip()
        cash_reg_id = int(request.form.get('cash_register_id')) if request.form.get('cash_register_id') else None
        desc = request.form.get('description', '').strip()

        try:
            pay = process_payment(
                supplier_id=supplier_id,
                amount=amount,
                payment_method=payment_method,
                reference_number=ref_num,
                cash_register_id=cash_reg_id,
                description=desc,
                user_id=current_user.id
            )
            flash(f'Ödeme ({pay.payment_number}) başarıyla kaydedildi.', 'success')
            return redirect(url_for('finance.payments'))
        except Exception as e:
            flash(f'Ödeme hatası: {str(e)}', 'danger')

    payments_list = Payment.query.order_by(Payment.created_at.desc()).all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    cash_registers = CashRegister.query.filter_by(is_active=True).all()

    return render_template('finance/payments.html', payments=payments_list, suppliers=suppliers, cash_registers=cash_registers)
