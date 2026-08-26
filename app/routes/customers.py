from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.party import Customer
from app.models.finance import CurrentAccount, CurrentTransaction
from app.services.finance_service import get_or_create_current_account
from app.services.audit_service import log_action
from app.utils.decorators import role_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/')
@login_required
def list_customers():
    search = request.args.get('search', '').strip()
    city = request.args.get('city', '').strip()
    ctype = request.args.get('type', '').strip()

    query = Customer.query

    if search:
        query = query.filter(
            (Customer.company_name.ilike(f'%{search}%')) |
            (Customer.code.ilike(f'%{search}%')) |
            (Customer.authorized_person.ilike(f'%{search}%')) |
            (Customer.tax_number.ilike(f'%{search}%'))
        )
    if city:
        query = query.filter(Customer.city == city)
    if ctype:
        query = query.filter(Customer.customer_type == ctype)

    customers = query.order_by(Customer.created_at.desc()).all()
    cities = db.session.query(Customer.city).distinct().all()
    cities = [c[0] for c in cities if c[0]]

    return render_template(
        'customers/list.html',
        customers=customers,
        search=search,
        selected_city=city,
        selected_type=ctype,
        cities=cities
    )


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli')
def create_customer():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        company_name = request.form.get('company_name', '').strip()
        
        # Validation: Check unique code
        if Customer.query.filter_by(code=code).first():
            flash('Bu müşteri kodu zaten kullanılıyor.', 'danger')
            return render_template('customers/form.html', customer=None)

        cust = Customer(
            code=code,
            company_name=company_name,
            authorized_person=request.form.get('authorized_person', '').strip(),
            phone=request.form.get('phone', '').strip(),
            email=request.form.get('email', '').strip(),
            tax_number=request.form.get('tax_number', '').strip(),
            tax_office=request.form.get('tax_office', '').strip(),
            address=request.form.get('address', '').strip(),
            city=request.form.get('city', '').strip(),
            district=request.form.get('district', '').strip(),
            customer_type=request.form.get('customer_type', 'Toptancı').strip(),
            risk_limit=float(request.form.get('risk_limit') or 0.0),
            payment_term_days=int(request.form.get('payment_term_days') or 30)
        )
        db.session.add(cust)
        db.session.commit()

        # Initialize Current Account
        get_or_create_current_account('MUSTERI', cust.id)

        log_action("Yeni Müşteri Eklendi", "Müşteri Yönetimi", f"{cust.code} - {cust.company_name}")
        flash('Müşteri başarıyla eklendi.', 'success')
        return redirect(url_for('customers.detail', customer_id=cust.id))

    return render_template('customers/form.html', customer=None)


@customers_bp.route('/<int:customer_id>')
@login_required
def detail(customer_id):
    cust = Customer.query.get_or_404(customer_id)
    c_acc = get_or_create_current_account('MUSTERI', cust.id)
    transactions = CurrentTransaction.query.filter_by(current_account_id=c_acc.id)\
        .order_by(CurrentTransaction.date.desc()).all()

    return render_template(
        'customers/detail.html',
        customer=cust,
        current_account=c_acc,
        transactions=transactions
    )


@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Satış Personeli')
def edit_customer(customer_id):
    cust = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        cust.company_name = request.form.get('company_name', '').strip()
        cust.authorized_person = request.form.get('authorized_person', '').strip()
        cust.phone = request.form.get('phone', '').strip()
        cust.email = request.form.get('email', '').strip()
        cust.tax_number = request.form.get('tax_number', '').strip()
        cust.tax_office = request.form.get('tax_office', '').strip()
        cust.address = request.form.get('address', '').strip()
        cust.city = request.form.get('city', '').strip()
        cust.district = request.form.get('district', '').strip()
        cust.customer_type = request.form.get('customer_type', 'Toptancı').strip()
        cust.risk_limit = float(request.form.get('risk_limit') or 0.0)
        cust.payment_term_days = int(request.form.get('payment_term_days') or 30)
        cust.is_active = True if request.form.get('is_active') else False

        db.session.commit()
        log_action("Müşteri Güncellendi", "Müşteri Yönetimi", f"{cust.code} - {cust.company_name}")
        flash('Müşteri bilgileri güncellendi.', 'success')
        return redirect(url_for('customers.detail', customer_id=cust.id))

    return render_template('customers/form.html', customer=cust)
