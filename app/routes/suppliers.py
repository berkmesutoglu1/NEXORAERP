from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.party import Supplier
from app.models.finance import CurrentAccount, CurrentTransaction
from app.services.finance_service import get_or_create_current_account
from app.services.audit_service import log_action
from app.utils.decorators import role_required

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/')
@login_required
def list_suppliers():
    search = request.args.get('search', '').strip()
    query = Supplier.query

    if search:
        query = query.filter(
            (Supplier.company_name.ilike(f'%{search}%')) |
            (Supplier.code.ilike(f'%{search}%')) |
            (Supplier.authorized_person.ilike(f'%{search}%'))
        )

    suppliers = query.order_by(Supplier.created_at.desc()).all()
    return render_template('suppliers/list.html', suppliers=suppliers, search=search)


@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici')
def create_supplier():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        if Supplier.query.filter_by(code=code).first():
            flash('Bu tedarikçi kodu zaten mevcut.', 'danger')
            return render_template('suppliers/form.html', supplier=None)

        sup = Supplier(
            code=code,
            company_name=request.form.get('company_name', '').strip(),
            authorized_person=request.form.get('authorized_person', '').strip(),
            phone=request.form.get('phone', '').strip(),
            email=request.form.get('email', '').strip(),
            tax_number=request.form.get('tax_number', '').strip(),
            tax_office=request.form.get('tax_office', '').strip(),
            address=request.form.get('address', '').strip(),
            city=request.form.get('city', '').strip(),
            district=request.form.get('district', '').strip(),
            payment_term_days=int(request.form.get('payment_term_days') or 30),
            iban=request.form.get('iban', '').strip()
        )
        db.session.add(sup)
        db.session.commit()

        get_or_create_current_account('TEDARIKCI', sup.id)
        log_action("Yeni Tedarikçi Eklendi", "Tedarikçi Yönetimi", f"{sup.code} - {sup.company_name}")
        flash('Tedarikçi eklendi.', 'success')
        return redirect(url_for('suppliers.detail', supplier_id=sup.id))

    return render_template('suppliers/form.html', supplier=None)


@suppliers_bp.route('/<int:supplier_id>')
@login_required
def detail(supplier_id):
    sup = Supplier.query.get_or_404(supplier_id)
    s_acc = get_or_create_current_account('TEDARIKCI', sup.id)
    transactions = CurrentTransaction.query.filter_by(current_account_id=s_acc.id)\
        .order_by(CurrentTransaction.date.desc()).all()

    return render_template('suppliers/detail.html', supplier=sup, current_account=s_acc, transactions=transactions)


@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici')
def edit_supplier(supplier_id):
    sup = Supplier.query.get_or_404(supplier_id)

    if request.method == 'POST':
        sup.company_name = request.form.get('company_name', '').strip()
        sup.authorized_person = request.form.get('authorized_person', '').strip()
        sup.phone = request.form.get('phone', '').strip()
        sup.email = request.form.get('email', '').strip()
        sup.tax_number = request.form.get('tax_number', '').strip()
        sup.tax_office = request.form.get('tax_office', '').strip()
        sup.address = request.form.get('address', '').strip()
        sup.city = request.form.get('city', '').strip()
        sup.district = request.form.get('district', '').strip()
        sup.payment_term_days = int(request.form.get('payment_term_days') or 30)
        sup.iban = request.form.get('iban', '').strip()
        sup.is_active = True if request.form.get('is_active') else False

        db.session.commit()
        log_action("Tedarikçi Güncellendi", "Tedarikçi Yönetimi", f"{sup.code} - {sup.company_name}")
        flash('Tedarikçi bilgileri güncellendi.', 'success')
        return redirect(url_for('suppliers.detail', supplier_id=sup.id))

    return render_template('suppliers/form.html', supplier=sup)
