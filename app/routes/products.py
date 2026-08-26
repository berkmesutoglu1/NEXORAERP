from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.product import Product, Category, Brand, Unit, StockLot
from app.models.party import Supplier
from app.models.warehouse import WarehouseStock, StockMovement
from app.services.audit_service import log_action
from app.utils.decorators import role_required

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@login_required
def list_products():
    search = request.args.get('search', '').strip()
    cat_id = request.args.get('category_id', type=int)
    brand_id = request.args.get('brand_id', type=int)

    query = Product.query

    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) |
            (Product.code.ilike(f'%{search}%')) |
            (Product.barcode.ilike(f'%{search}%'))
        )
    if cat_id:
        query = query.filter(Product.category_id == cat_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)

    products = query.order_by(Product.name.asc()).all()
    categories = Category.query.all()
    brands = Brand.query.all()

    return render_template(
        'products/list.html',
        products=products,
        search=search,
        selected_category=cat_id,
        selected_brand=brand_id,
        categories=categories,
        brands=brands
    )


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def create_product():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        barcode = request.form.get('barcode', '').strip()

        if Product.query.filter_by(code=code).first():
            flash('Bu ürün kodu kullanılıyor.', 'danger')
            return redirect(url_for('products.create_product'))

        if barcode and Product.query.filter_by(barcode=barcode).first():
            flash('Bu barkod başka bir ürüne ait.', 'danger')
            return redirect(url_for('products.create_product'))

        prd = Product(
            code=code,
            barcode=barcode or None,
            name=request.form.get('name', '').strip(),
            category_id=int(request.form.get('category_id')),
            brand_id=int(request.form.get('brand_id')) if request.form.get('brand_id') else None,
            unit_id=int(request.form.get('unit_id')),
            supplier_id=int(request.form.get('supplier_id')) if request.form.get('supplier_id') else None,
            purchase_price=float(request.form.get('purchase_price') or 0.0),
            sale_price=float(request.form.get('sale_price') or 0.0),
            vat_rate=float(request.form.get('vat_rate') or 20.0),
            min_stock_level=float(request.form.get('min_stock_level') or 10.0),
            max_stock_level=float(request.form.get('max_stock_level') or 1000.0)
        )
        db.session.add(prd)
        db.session.commit()

        log_action("Yeni Ürün Eklendi", "Ürün Yönetimi", f"{prd.code} - {prd.name}")
        flash('Ürün kartı başarıyla oluşturuldu.', 'success')
        return redirect(url_for('products.detail', product_id=prd.id))

    categories = Category.query.all()
    brands = Brand.query.all()
    units = Unit.query.all()
    suppliers = Supplier.query.filter_by(is_active=True).all()

    return render_template(
        'products/form.html',
        product=None,
        categories=categories,
        brands=brands,
        units=units,
        suppliers=suppliers
    )


@products_bp.route('/<int:product_id>')
@login_required
def detail(product_id):
    prd = Product.query.get_or_404(product_id)
    warehouse_stocks = WarehouseStock.query.filter_by(product_id=prd.id).all()
    lots = StockLot.query.filter_by(product_id=prd.id).order_by(StockLot.expiration_date.asc()).all()
    movements = StockMovement.query.filter_by(product_id=prd.id).order_by(StockMovement.created_at.desc()).limit(20).all()

    return render_template(
        'products/detail.html',
        product=prd,
        warehouse_stocks=warehouse_stocks,
        lots=lots,
        movements=movements
    )


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici', 'Depo Personeli')
def edit_product(product_id):
    prd = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        prd.name = request.form.get('name', '').strip()
        prd.barcode = request.form.get('barcode', '').strip() or None
        prd.category_id = int(request.form.get('category_id'))
        prd.brand_id = int(request.form.get('brand_id')) if request.form.get('brand_id') else None
        prd.unit_id = int(request.form.get('unit_id'))
        prd.supplier_id = int(request.form.get('supplier_id')) if request.form.get('supplier_id') else None
        prd.purchase_price = float(request.form.get('purchase_price') or 0.0)
        prd.sale_price = float(request.form.get('sale_price') or 0.0)
        prd.vat_rate = float(request.form.get('vat_rate') or 20.0)
        prd.min_stock_level = float(request.form.get('min_stock_level') or 10.0)
        prd.max_stock_level = float(request.form.get('max_stock_level') or 1000.0)
        prd.is_active = True if request.form.get('is_active') else False

        db.session.commit()
        log_action("Ürün Güncellendi", "Ürün Yönetimi", f"{prd.code} - {prd.name}")
        flash('Ürün kartı güncellendi.', 'success')
        return redirect(url_for('products.detail', product_id=prd.id))

    categories = Category.query.all()
    brands = Brand.query.all()
    units = Unit.query.all()
    suppliers = Supplier.query.filter_by(is_active=True).all()

    return render_template(
        'products/form.html',
        product=prd,
        categories=categories,
        brands=brands,
        units=units,
        suppliers=suppliers
    )


@products_bp.route('/categories', methods=['GET', 'POST'])
@login_required
@role_required('Admin', 'Yönetici')
def categories():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        name = request.form.get('name', '').strip()
        desc = request.form.get('description', '').strip()

        if Category.query.filter_by(code=code).first():
            flash('Bu kategori kodu zaten mevcut.', 'danger')
        else:
            cat = Category(code=code, name=name, description=desc)
            db.session.add(cat)
            db.session.commit()
            log_action("Yeni Kategori Eklendi", "Ürün Yönetimi", f"Kategori: {name}")
            flash('Kategori eklendi.', 'success')

        return redirect(url_for('products.categories'))

    categories_list = Category.query.all()
    return render_template('products/categories.html', categories=categories_list)
