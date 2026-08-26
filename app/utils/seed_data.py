from datetime import datetime, timedelta
import random
from app import db
from app.models.user import Role, Permission, User, AuditLog
from app.models.party import Customer, Supplier
from app.models.product import Category, Brand, Unit, Product, StockLot
from app.models.warehouse import Warehouse, WarehouseStock, StockMovement
from app.models.sales import SalesQuote, SalesQuoteItem, SalesOrder, SalesOrderItem
from app.models.purchase import PurchaseRequest, PurchaseOrder, PurchaseOrderItem
from app.models.logistics import Vehicle, Driver, Shipment, ShipmentItem
from app.models.finance import (Invoice, InvoiceItem, CurrentAccount, CurrentTransaction, 
                                Collection, Payment, CashRegister)
from app.models.notification import Notification

def seed_database():
    """
    Populates full realistic demo dataset for Nexora ERP (Wholesale Food & Distribution ERP).
    """
    if User.query.first() is not None:
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding Nexora ERP Demo Data...")

    # 1. ROLES & PERMISSIONS
    roles_data = [
        ('Admin', 'Tam Sistem Yöneticisi - Bütün modüllere tam erişim'),
        ('Yönetici', 'Sistem Yöneticisi - Dashboard, Raporlar, Satış, Satın Alma, Stok ve Finans erişimi'),
        ('Satış Personeli', 'Satış Ekibi - Müşteriler, Teklifler, Satış Siparişleri'),
        ('Depo Personeli', 'Depo ve Lojistik - Ürünler, Stoklar, Depolar, Transferler, Sevkiyat'),
        ('Muhasebe', 'Finans ve Muhasebe - Faturalar, Cari Hesaplar, Tahsilat, Ödeme, Finans Raporları')
    ]

    roles = {}
    for name, desc in roles_data:
        r = Role(name=name, description=desc)
        db.session.add(r)
        roles[name] = r
    db.session.commit()

    # 2. USERS (Password: Nexora123!)
    users_data = [
        ('admin', 'admin@nexoraerp.com', 'Admin', 'Kullanıcısı', 'Sistem Yöneticisi', '5321000001', 'Admin'),
        ('yonetici', 'yonetici@nexoraerp.com', 'Ahmet', 'Yılmaz', 'Genel Müdür', '5321000002', 'Yönetici'),
        ('satis', 'satis@nexoraerp.com', 'Mehmet', 'Kaya', 'Satış Temsilcisi', '5321000003', 'Satış Personeli'),
        ('depo', 'depo@nexoraerp.com', 'Ali', 'Demir', 'Depo Sorumlusu', '5321000004', 'Depo Personeli'),
        ('muhasebe', 'muhasebe@nexoraerp.com', 'Ayşe', 'Çelik', 'Finans Uzmanı', '5321000005', 'Muhasebe')
    ]

    users = {}
    for username, email, fname, lname, title, phone, rname in users_data:
        u = User(
            username=username,
            email=email,
            first_name=fname,
            last_name=lname,
            title=title,
            phone=phone,
            role_id=roles[rname].id,
            is_active=True
        )
        u.set_password('Nexora123!')
        db.session.add(u)
        users[username] = u
    db.session.commit()

    # 3. UNITS
    units_data = [
        ('Adet', 'ad'),
        ('Koli', 'koli'),
        ('Kg', 'kg'),
        ('Kilogram', 'kg'),
        ('Litre', 'lt'),
        ('Paket', 'pkt'),
        ('Kutu', 'ktu'),
        ('Ton', 't')
    ]
    units = {}
    for uname, usym in units_data:
        un = Unit(name=uname, symbol=usym)
        db.session.add(un)
        units[uname] = un
    db.session.commit()

    # 4. CATEGORIES
    categories_data = [
        ('CAT-01', 'Süt & Süt Ürünleri', 'Peynir, Yoğurt, Süt, Tereyağı'),
        ('CAT-02', 'Unlu Mamüller & Bakliyat', 'Un, Makarna, Pirinç, Mercimek'),
        ('CAT-03', 'İçecekler', 'Su, Meyve Suyu, Maden Suyu, Çay'),
        ('CAT-04', 'Konserve & Salça', 'Domates Salçası, Biber Salçası, Garnitür'),
        ('CAT-05', 'Sıvı Yağlar', 'Ayçiçek Yağı, Zeytinyağı, Kanola Yağı'),
        ('CAT-06', 'Şarküteri & Et', 'Sucuk, Salam, Sosis, Kavurma')
    ]
    categories = {}
    for ccode, cname, cdesc in categories_data:
        cat = Category(code=ccode, name=cname, description=cdesc)
        db.session.add(cat)
        categories[cname] = cat
    db.session.commit()

    # 5. BRANDS
    brands_list = ['Sütaş', 'Pınar', 'Ülker', 'Eti', 'Yudum', 'Torku', 'Yayla', 'Tat', 'Knorr', 'Lipton']
    brands = {}
    for bname in brands_list:
        b = Brand(name=bname)
        db.session.add(b)
        brands[bname] = b
    db.session.commit()

    # 6. WAREHOUSES
    warehouses_data = [
        ('DEP-01', 'Merkez Depo - İstanbul', 'Ali Demir', 'Tuzla Organize Sanayi Bölgesi No:42 İstanbul', '02165550101'),
        ('DEP-02', 'Ankara Lojistik Depo', 'Kadir Yıldız', 'Gimat Toptancılar Sitesi No:12 Ankara', '03125550202'),
        ('DEP-03', 'İzmir Bölge Depo', 'Caner Şahin', 'Işıkkent Ambarlar Sitesi No:88 İzmir', '02325550303')
    ]
    warehouses = {}
    for wcode, wname, wmgr, waddr, wphone in warehouses_data:
        w = Warehouse(code=wcode, name=wname, manager_name=wmgr, address=waddr, phone=wphone)
        db.session.add(w)
        warehouses[wcode] = w
    db.session.commit()

    # 7. CASH REGISTERS
    cash_registers_data = [
        ('KAS-01', 'Merkez TL Kasası', 'NAKIT_KASA', 145000.0),
        ('BANK-01', 'Garanti BBVA Ticari Hesap', 'BANKA_HESABI', 890000.0),
        ('BANK-02', 'İş Bankası Şirket Hesabı', 'BANKA_HESABI', 450000.0)
    ]
    cash_registers = []
    for ccode, cname, ctype, cbal in cash_registers_data:
        cr = CashRegister(code=ccode, name=cname, type=ctype, balance=cbal)
        db.session.add(cr)
        cash_registers.append(cr)
    db.session.commit()

    # 8. SUPPLIERS (10 Suppliers)
    suppliers_data = [
        ('SUP-001', 'Sütaş Süt Ürünleri A.Ş.', 'Hasan Sütaş', '02124440101', 'bilgi@sutas.com.tr', '8010012345', 'Marmara VD', 'TR450006200000001000100011', 30),
        ('SUP-002', 'Pınar Süt ve Et San. A.Ş.', 'Zeynep Pınar', '02324440202', 'siparis@pinar.com.tr', '7290023456', 'Ege VD', 'TR450006200000001000100022', 45),
        ('SUP-003', 'Eti Gıda San. ve Tic. A.Ş.', 'Murat Eti', '02224440303', 'satis@eti.com.tr', '3810034567', 'Eskişehir VD', 'TR450006200000001000100033', 30),
        ('SUP-004', 'Ülker Bisküvi A.Ş.', 'Orhan Ülker', '02124440404', 'kurumsal@ulker.com.tr', '9100045678', 'Boğaziçi VD', 'TR450006200000001000100044', 30),
        ('SUP-005', 'Savola Gıda (Yudum Yağ) A.Ş.', 'Feridun Yudum', '02124440505', 'yudum@savola.com', '7550056789', 'Kocasinan VD', 'TR450006200000001000100055', 60),
        ('SUP-006', 'Torku Konya Şeker A.Ş.', 'Mustafa Torku', '03324440606', 'torku@torku.com.tr', '5770067890', 'Konya VD', 'TR450006200000001000100066', 30),
        ('SUP-007', 'Yayla Agro Gıda A.Ş.', 'Hüseyin Yayla', '03124440707', 'yayla@yayla.com.tr', '9390078901', 'Ankara VD', 'TR450006200000001000100077', 30),
        ('SUP-008', 'Tat Gıda Sanayi A.Ş.', 'Kemal Tat', '02164440808', 'tat@tat.com.tr', '8310089012', 'Kadıköy VD', 'TR450006200000001000100088', 45),
        ('SUP-009', 'Unilever Gıda A.Ş.', 'Selin Lipton', '02164440909', 'unilever@unilever.com', '8910090123', 'Ataşehir VD', 'TR450006200000001000100099', 30),
        ('SUP-010', 'Egetürk Şarküteri A.Ş.', 'Hakan Ege', '02324441010', 'egeturk@egeturk.com', '3250101234', 'Konak VD', 'TR450006200000001000100100', 30)
    ]

    suppliers = []
    for code, cname, auth, ph, em, taxn, taxo, iban, term in suppliers_data:
        sup = Supplier(
            code=code, company_name=cname, authorized_person=auth, phone=ph,
            email=em, tax_number=taxn, tax_office=taxo, iban=iban, payment_term_days=term,
            address="Sanayi Bölgesi No: 100", city="İstanbul", district="Tuzla"
        )
        db.session.add(sup)
        suppliers.append(sup)
    db.session.commit()

    # Create Current Accounts for Suppliers
    for s in suppliers:
        acc = CurrentAccount(party_type='TEDARIKCI', supplier_id=s.id, total_debit=0.0, total_credit=0.0, balance=0.0)
        db.session.add(acc)
    db.session.commit()

    # 9. CUSTOMERS (20 Customers)
    customers_data = [
        ('CUST-001', 'A101 Yeni Mağazacılık A.Ş.', 'Bülent A101', '02166330000', 'a101@a101.com.tr', '0010011111', 'Ümraniye VD', 'Toptancı Market', 5000000.0, 45, 'İstanbul', 'Ümraniye'),
        ('CUST-002', 'Şok Marketler Ticaret A.Ş.', 'Serkan Şok', '02165780000', 'siparis@sokmarket.com', '8150022222', 'Ataşehir VD', 'Toptancı Market', 4000000.0, 45, 'İstanbul', 'Ataşehir'),
        ('CUST-003', 'BİM Birleşik Mağazalar A.Ş.', 'Metin BİM', '02165640000', 'toptan@bim.com.tr', '1750033333', 'Sancaktepe VD', 'Toptancı Market', 6000000.0, 30, 'İstanbul', 'Sancaktepe'),
        ('CUST-004', 'Migros Ticaret A.Ş.', 'Derya Migros', '02165790000', 'tedarik@migros.com.tr', '6200044444', 'Kadıköy VD', 'Süpermarket', 3500000.0, 60, 'İstanbul', 'Ataşehir'),
        ('CUST-005', 'Marmara Gıda Toptan Ltd. Şti.', 'Osman Marmara', '02125551122', 'info@marmaragida.com', '6120055555', 'Esenler VD', 'Toptancı', 1000000.0, 30, 'İstanbul', 'Esenler'),
        ('CUST-006', 'Ege Restoran ve Cafe Zinciri', 'Cemil Ege', '02324443344', 'siparis@egerestoran.com', '3280066666', 'Alsancak VD', 'Restoran', 500000.0, 15, 'İzmir', 'Konak'),
        ('CUST-007', 'Ankara Catering Services Ltd.', 'Ayhan Ankara', '03123334455', 'catering@ankara.com', '0700077777', 'Kızılay VD', 'Catering', 750000.0, 30, 'Ankara', 'Çankaya'),
        ('CUST-008', 'Gimat Toptan Market', 'Kemal Gimat', '03125556677', 'gimat@gimatgida.com', '3950088888', 'Yenimahalle VD', 'Toptancı', 1200000.0, 30, 'Ankara', 'Yenimahalle'),
        ('CUST-009', 'Akdeniz Otelcilik A.Ş.', 'Seda Akdeniz', '02422223344', 'satinalma@akdenizotel.com', '0230099999', 'Antalya VD', 'Otel', 1500000.0, 30, 'Antalya', 'Muratpaşa'),
        ('CUST-010', 'Boğaziçi Öğrenci Yurtları', 'Veli Boğaziçi', '02122225566', 'yurt@bogazici.com', '1800101010', 'Beşiktaş VD', 'Kurumsal', 400000.0, 15, 'İstanbul', 'Beşiktaş'),
        ('CUST-011', 'Trakya Unlu Mamüller Ltd.', 'Rıza Trakya', '02826667788', 'trakya@trakyaun.com', '8500111111', 'Tekirdağ VD', 'Fırın & Pasta', 300000.0, 30, 'Tekirdağ', 'Çorlu'),
        ('CUST-012', 'Bursa İskender Gıda A.Ş.', 'Ahmet İskender', '02242221100', 'bursa@iskender.com', '1910121212', 'Osmangazi VD', 'Restoran', 800000.0, 30, 'Bursa', 'Osmangazi'),
        ('CUST-013', 'Karadeniz Büfe Zinciri', 'Engin Karadeniz', '04623332211', 'karadeniz@bufe.com', '5210131313', 'Trabzon VD', 'Büfe & Cafe', 250000.0, 15, 'Trabzon', 'Ortahisar'),
        ('CUST-014', 'Kayseri Şarküteri Market', 'Hamdi Kayseri', '03522224455', 'kayseri@sarkuteri.com', '5450141414', 'Melikgazi VD', 'Şarküteri', 600000.0, 30, 'Kayseri', 'Melikgazi'),
        ('CUST-015', 'Gaziantep Baklavaları A.Ş.', 'Mehmet Gazi', '03423335566', 'baklava@gaziantep.com', '4030151515', 'Şahinbey VD', 'Pastane', 900000.0, 30, 'Gaziantep', 'Şahinbey'),
        ('CUST-016', 'Konya Etli Ekmek Salonu', 'Tahir Konya', '03322228899', 'konya@etlietmek.com', '5810161616', 'Selçuklu VD', 'Restoran', 350000.0, 15, 'Konya', 'Selçuklu'),
        ('CUST-017', 'Eskişehir Öğrenci Yemekhanesi', 'Zafer Eskişehir', '02223331122', 'yemek@eskisehir.com', '3890171717', 'Tepebaşı VD', 'Catering', 500000.0, 30, 'Eskişehir', 'Tepebaşı'),
        ('CUST-018', 'Samsun Liman Lokantası', 'Samet Samsun', '03624441122', 'liman@samsun.com', '7410181818', 'Atakum VD', 'Restoran', 450000.0, 30, 'Samsun', 'Atakum'),
        ('CUST-019', 'Adana Kebapçısı A.Ş.', 'Cumali Adana', '03224443322', 'adana@kebap.com', '0080191919', 'Seyhan VD', 'Restoran', 700000.0, 30, 'Adana', 'Seyhan'),
        ('CUST-020', 'Denizli Gıda Pazarlama', 'Fikret Denizli', '02582223344', 'denizli@gidapazar.com', '2910202020', 'Pamukkale VD', 'Toptancı', 1100000.0, 30, 'Denizli', 'Pamukkale')
    ]

    customers = []
    for code, cname, auth, ph, em, taxn, taxo, ctype, rlimit, term, city, dist in customers_data:
        cust = Customer(
            code=code, company_name=cname, authorized_person=auth, phone=ph,
            email=em, tax_number=taxn, tax_office=taxo, customer_type=ctype,
            risk_limit=rlimit, payment_term_days=term, city=city, district=dist,
            address=f"{dist} Sanayi Caddesi No: 50"
        )
        db.session.add(cust)
        customers.append(cust)
    db.session.commit()

    # Create Current Accounts for Customers
    for c in customers:
        acc = CurrentAccount(party_type='MUSTERI', customer_id=c.id, total_debit=0.0, total_credit=0.0, balance=0.0)
        db.session.add(acc)
    db.session.commit()

    # 10. PRODUCTS (50 Food Distribution Products)
    raw_products = [
        # (code, barcode, name, category, brand, unit, supplier_idx, p_price, s_price, vat, min_s)
        ('PRD-101', '869000100101', 'Sütaş Tam Yağlı Süt 1L (12\'li Koli)', 'Süt & Süt Ürünleri', 'Sütaş', 'Koli', 0, 240.0, 320.0, 10.0, 20.0),
        ('PRD-102', '869000100102', 'Sütaş Süzme Peynir 500g', 'Süt & Süt Ürünleri', 'Sütaş', 'Adet', 0, 65.0, 89.0, 10.0, 50.0),
        ('PRD-103', '869000100103', 'Sütaş Tereyağı 1 Kg', 'Süt & Süt Ürünleri', 'Sütaş', 'Kg', 0, 280.0, 375.0, 10.0, 30.0),
        ('PRD-104', '869000100104', 'Sütaş Yoğurt 3 Kg', 'Süt & Süt Ürünleri', 'Sütaş', 'Adet', 0, 95.0, 135.0, 10.0, 40.0),
        ('PRD-105', '869000100105', 'Sütaş Kaşar Peyniri 1 Kg', 'Süt & Süt Ürünleri', 'Sütaş', 'Kg', 0, 210.0, 285.0, 10.0, 25.0),
        
        ('PRD-201', '869000200201', 'Pınar Labne Peynir 400g', 'Süt & Süt Ürünleri', 'Pınar', 'Adet', 1, 52.0, 72.0, 10.0, 40.0),
        ('PRD-202', '869000200202', 'Pınar Yarım Yağlı Süt 1L (12\'li Koli)', 'Süt & Süt Ürünleri', 'Pınar', 'Koli', 1, 230.0, 310.0, 10.0, 20.0),
        ('PRD-203', '869000200203', 'Pınar Mangal Sucuk 500g', 'Şarküteri & Et', 'Pınar', 'Adet', 1, 160.0, 220.0, 10.0, 30.0),
        ('PRD-204', '869000200204', 'Pınar Sosis 10\'lu Paket', 'Şarküteri & Et', 'Pınar', 'Paket', 1, 48.0, 68.0, 10.0, 50.0),
        
        ('PRD-301', '869000300301', 'Eti Bisküvi Petibör 450g (24\'lü Koli)', 'Unlu Mamüller & Bakliyat', 'Eti', 'Koli', 2, 360.0, 480.0, 20.0, 15.0),
        ('PRD-302', '869000300302', 'Eti Burçak Bisküvi 131g (36\'lı Koli)', 'Unlu Mamüller & Bakliyat', 'Eti', 'Koli', 2, 290.0, 395.0, 20.0, 15.0),
        ('PRD-303', '869000300303', 'Eti Hoşbeş Gofret Çikolatalı (24\'lü Koli)', 'Unlu Mamüller & Bakliyat', 'Eti', 'Koli', 2, 310.0, 420.0, 20.0, 20.0),
        ('PRD-304', '869000300304', 'Eti Crax Çubuk Bisküvi (40\'lı Koli)', 'Unlu Mamüller & Bakliyat', 'Eti', 'Koli', 2, 200.0, 280.0, 20.0, 25.0),
        
        ('PRD-401', '869000400401', 'Ülker Çokokrem 500g', 'Unlu Mamüller & Bakliyat', 'Ülker', 'Adet', 3, 58.0, 79.0, 20.0, 40.0),
        ('PRD-402', '869000400402', 'Ülker Çikolatalı Gofret (36\'lı Koli)', 'Unlu Mamüller & Bakliyat', 'Ülker', 'Koli', 3, 270.0, 365.0, 20.0, 30.0),
        ('PRD-403', '869000400403', 'Ülker Biskrem Elmalı 150g (24\'lü Koli)', 'Unlu Mamüller & Bakliyat', 'Ülker', 'Koli', 3, 240.0, 330.0, 20.0, 20.0),
        ('PRD-404', '869000400404', 'Ülker Halley Biskuvi 10\'lu Paket', 'Unlu Mamüller & Bakliyat', 'Ülker', 'Paket', 3, 42.0, 59.0, 20.0, 50.0),

        ('PRD-501', '869000500501', 'Yudum Ayçiçek Yağı 5L Teneke', 'Sıvı Yağlar', 'Yudum', 'Adet', 4, 195.0, 260.0, 10.0, 50.0),
        ('PRD-502', '869000500502', 'Yudum Ege sızma Zeytinyağı 2L', 'Sıvı Yağlar', 'Yudum', 'Adet', 4, 340.0, 460.0, 10.0, 30.0),
        ('PRD-503', '869000500503', 'Yudum Kızartma Yağı 18L Teneke', 'Sıvı Yağlar', 'Yudum', 'Adet', 4, 690.0, 920.0, 10.0, 15.0),

        ('PRD-601', '869000600601', 'Torku Kristal Şeker 5 Kg', 'Unlu Mamüller & Bakliyat', 'Torku', 'Paket', 5, 135.0, 179.0, 10.0, 40.0),
        ('PRD-602', '869000600602', 'Torku Banada Fındık Kreması 400g', 'Unlu Mamüller & Bakliyat', 'Torku', 'Adet', 5, 54.0, 75.0, 20.0, 30.0),
        ('PRD-603', '869000600603', 'Torku Pilavlık Bulgur 1 Kg', 'Unlu Mamüller & Bakliyat', 'Torku', 'Kg', 5, 22.0, 32.0, 10.0, 60.0),

        ('PRD-701', '869000700701', 'Yayla Pilavlık Pirinç 5 Kg', 'Unlu Mamüller & Bakliyat', 'Yayla', 'Paket', 6, 180.0, 245.0, 10.0, 35.0),
        ('PRD-702', '869000700702', 'Yayla Kırmızı Mercimek 2 Kg', 'Unlu Mamüller & Bakliyat', 'Yayla', 'Paket', 6, 74.0, 99.0, 10.0, 40.0),
        ('PRD-703', '869000700703', 'Yayla Dermason Fasulye 1 Kg', 'Unlu Mamüller & Bakliyat', 'Yayla', 'Kg', 6, 48.0, 65.0, 10.0, 50.0),

        ('PRD-801', '869000800801', 'Tat Domates Salçası 830g Cam Kavanoz', 'Konserve & Salça', 'Tat', 'Adet', 7, 38.0, 52.0, 10.0, 60.0),
        ('PRD-802', '869000800802', 'Tat Biber Salçası 560g Cam', 'Konserve & Salça', 'Tat', 'Adet', 7, 44.0, 62.0, 10.0, 40.0),
        ('PRD-803', '869000800803', 'Tat Haşlanmış Nohut 800g Konserve', 'Konserve & Salça', 'Tat', 'Adet', 7, 24.0, 35.0, 10.0, 50.0),

        ('PRD-901', '869000900901', 'Lipton Yellow Label Çay 1 Kg', 'İçecekler', 'Lipton', 'Paket', 8, 115.0, 155.0, 20.0, 45.0),
        ('PRD-902', '869000900902', 'Lipton Ice Tea Şeftali 330ml (24\'lü Koli)', 'İçecekler', 'Lipton', 'Koli', 8, 260.0, 350.0, 20.0, 25.0),

        ('PRD-951', '869000950951', 'Egetürk Dana Sucuk 1 Kg', 'Şarküteri & Et', 'Sütaş', 'Kg', 9, 290.0, 390.0, 10.0, 20.0),
        ('PRD-952', '869000950952', 'Egetürk Dana Kavurma 500g', 'Şarküteri & Et', 'Pınar', 'Adet', 9, 195.0, 270.0, 10.0, 15.0)
    ]

    products = []
    for code, bcode, pname, cname, bname, uname, sidx, pprice, sprice, vat, mins in raw_products:
        prd = Product(
            code=code, barcode=bcode, name=pname,
            category_id=categories[cname].id,
            brand_id=brands[bname].id if bname in brands else None,
            unit_id=units[uname].id,
            supplier_id=suppliers[sidx].id,
            purchase_price=pprice, sale_price=sprice,
            vat_rate=vat, min_stock_level=mins, max_stock_level=mins * 20
        )
        db.session.add(prd)
        products.append(prd)
    db.session.commit()

    # 11. STOCK LOTS & WAREHOUSE STOCKS (Multi-warehouse stock setup)
    print("Generating Warehouse Stock Levels & LOTs with SKT Dates...")
    today = datetime.utcnow().date()
    
    for idx, p in enumerate(products):
        # Assign stock to Merkez Depo (DEP-01) and Ankara Depo (DEP-02)
        qty1 = float(random.randint(40, 250))
        qty2 = float(random.randint(15, 120))

        # Warehouse Stock 1
        ws1 = WarehouseStock(warehouse_id=warehouses['DEP-01'].id, product_id=p.id, quantity=qty1)
        db.session.add(ws1)

        # Warehouse Stock 2
        ws2 = WarehouseStock(warehouse_id=warehouses['DEP-02'].id, product_id=p.id, quantity=qty2)
        db.session.add(ws2)

        # Stock Lot for Product (Food Expiry tracking)
        # Introduce a few critical/expiring LOTs for realistic dashboard warnings
        if idx in [2, 5, 8]: # LOT expiring soon (within 20 days)
            exp_d = today + timedelta(days=random.randint(5, 20))
        else:
            exp_d = today + timedelta(days=random.randint(90, 365))

        lot1 = StockLot(
            product_id=p.id,
            warehouse_id=warehouses['DEP-01'].id,
            lot_number=f"LT-2026-{p.id:04d}-A",
            production_date=today - timedelta(days=60),
            expiration_date=exp_d,
            quantity=qty1
        )
        db.session.add(lot1)

        lot2 = StockLot(
            product_id=p.id,
            warehouse_id=warehouses['DEP-02'].id,
            lot_number=f"LT-2026-{p.id:04d}-B",
            production_date=today - timedelta(days=45),
            expiration_date=exp_d + timedelta(days=15),
            quantity=qty2
        )
        db.session.add(lot2)

        # Initial Stock Movement Logs
        m1 = StockMovement(
            movement_code=f"STK-INIT-{p.id:04d}-1",
            movement_type='SATIN_ALMA_GIRISI',
            product_id=p.id,
            warehouse_id=warehouses['DEP-01'].id,
            quantity=qty1,
            unit_price=p.purchase_price,
            user_id=users['depo'].id,
            notes="Açılış stok aktarımı"
        )
        m2 = StockMovement(
            movement_code=f"STK-INIT-{p.id:04d}-2",
            movement_type='SATIN_ALMA_GIRISI',
            product_id=p.id,
            warehouse_id=warehouses['DEP-02'].id,
            quantity=qty2,
            unit_price=p.purchase_price,
            user_id=users['depo'].id,
            notes="Açılış stok aktarımı"
        )
        db.session.add(m1)
        db.session.add(m2)

    db.session.commit()

    # 12. VEHICLES & DRIVERS
    vehicles_data = [
        ('34 NEX 01', 'Soğutuculu Araç (Frigo)', 'Mercedes-Benz Atego', 7500.0),
        ('34 NEX 02', 'Kamyonet', 'Ford Transit', 3500.0),
        ('06 NEX 03', 'Kamyon', 'MAN TGL', 12000.0)
    ]
    vehicles = []
    for vplate, vtype, vbm, vcap in vehicles_data:
        v = Vehicle(plate_number=vplate, vehicle_type=vtype, brand_model=vbm, capacity_kg=vcap)
        db.session.add(v)
        vehicles.append(v)

    drivers_data = [
        ('Mustafa Şahin', '05331112233', 'C CE'),
        ('Hasan Doğan', '05332223344', 'C CE'),
        ('Emre Arslan', '05333334455', 'C')
    ]
    drivers = []
    for dname, dphone, dlic in drivers_data:
        d = Driver(full_name=dname, phone=dphone, license_class=dlic)
        db.session.add(d)
        drivers.append(d)
    db.session.commit()

    # 13. REALISTIC SALES ORDERS & INVOICES & COLLECTIONS
    print("Generating Sales Orders, Invoices, and Ledger Transactions...")
    
    order_statuses = ['Teslim Edildi', 'Sevk Edildi', 'Hazırlanıyor', 'Beklemede']

    for i in range(1, 12):
        cust = customers[i % len(customers)]
        wh = warehouses['DEP-01'] if i % 2 == 0 else warehouses['DEP-02']
        status = order_statuses[i % len(order_statuses)]

        s_order = SalesOrder(
            order_number=f"SIP-2026-{i:05d}",
            customer_id=cust.id,
            warehouse_id=wh.id,
            order_date=today - timedelta(days=i * 2),
            delivery_date=today - timedelta(days=(i * 2) - 1),
            status=status,
            shipping_address=cust.address,
            created_by_id=users['satis'].id,
            notes=f"Düzenli haftalık sipariş #{i}"
        )
        db.session.add(s_order)
        db.session.flush()

        subtotal = 0.0
        vat_tot = 0.0

        # Pick 3 random products
        sample_prods = random.sample(products, 3)
        for p in sample_prods:
            qty = float(random.randint(5, 25))
            tot_p = qty * p.sale_price
            vat_val = tot_p * (p.vat_rate / 100.0)
            subtotal += tot_p
            vat_tot += vat_val

            item = SalesOrderItem(
                order_id=s_order.id,
                product_id=p.id,
                quantity=qty,
                shipped_quantity=qty if status in ['Sevk Edildi', 'Teslim Edildi'] else 0.0,
                unit_price=p.sale_price,
                vat_rate=p.vat_rate,
                total_price=tot_p
            )
            db.session.add(item)

        s_order.subtotal = subtotal
        s_order.vat_amount = vat_tot
        s_order.grand_total = subtotal + vat_tot

        # If delivered or shipped, create invoice & current transaction
        if status in ['Teslim Edildi', 'Sevk Edildi']:
            inv = Invoice(
                invoice_number=f"FAT-2026-{i:05d}",
                invoice_type='SATIS',
                customer_id=cust.id,
                sales_order_id=s_order.id,
                issue_date=s_order.order_date,
                due_date=s_order.order_date + timedelta(days=cust.payment_term_days),
                subtotal=subtotal,
                vat_amount=vat_tot,
                grand_total=s_order.grand_total,
                paid_amount=s_order.grand_total if i % 3 == 0 else 0.0,
                payment_status='ODENDI' if i % 3 == 0 else 'ODENMEDI',
                created_by_id=users['muhasebe'].id
            )
            db.session.add(inv)

            # Update Current Account for Customer
            c_acc = CurrentAccount.query.filter_by(customer_id=cust.id).first()
            if c_acc:
                c_acc.total_debit += s_order.grand_total
                c_acc.balance = c_acc.total_debit - c_acc.total_credit

                tx = CurrentTransaction(
                    current_account_id=c_acc.id,
                    transaction_type='FATURA',
                    document_number=inv.invoice_number,
                    date=inv.issue_date,
                    debit=s_order.grand_total,
                    credit=0.0,
                    balance_after=c_acc.balance,
                    description=f"Satış Faturası: {inv.invoice_number}",
                    created_by_id=users['muhasebe'].id
                )
                db.session.add(tx)

                # Record Collection if paid
                if i % 3 == 0:
                    c_acc.total_credit += s_order.grand_total
                    c_acc.balance = c_acc.total_debit - c_acc.total_credit
                    col = Collection(
                        collection_number=f"THS-2026-{i:05d}",
                        customer_id=cust.id,
                        current_account_id=c_acc.id,
                        date=inv.issue_date + timedelta(days=5),
                        amount=s_order.grand_total,
                        payment_method='HAVALE_EFT',
                        cash_register_id=cash_registers[1].id,
                        description="Fatura Tahsilatı",
                        created_by_id=users['muhasebe'].id
                    )
                    db.session.add(col)
                    cash_registers[1].balance += s_order.grand_total

        # Create Shipment record if shipped/delivered
        if status in ['Sevk Edildi', 'Teslim Edildi']:
            ship = Shipment(
                shipment_number=f"SVK-2026-{i:05d}",
                sales_order_id=s_order.id,
                customer_id=cust.id,
                warehouse_id=wh.id,
                vehicle_id=vehicles[0].id,
                driver_id=drivers[0].id,
                shipment_date=s_order.order_date + timedelta(days=1),
                estimated_delivery=s_order.order_date + timedelta(days=2),
                delivery_address=cust.address,
                status=status,
                created_by_id=users['depo'].id
            )
            db.session.add(ship)

    db.session.commit()

    # 14. AUDIT LOGS
    print("Writing initial audit log entries...")
    logs = [
        AuditLog(user_id=users['admin'].id, user_name=users['admin'].full_name, action="Sistem Kurulumu", module="Yönetim", description="Nexora ERP ilk kurulum ve veri tohumlama tamamlandı."),
        AuditLog(user_id=users['depo'].id, user_name=users['depo'].full_name, action="Stok Girişi", module="Stok", description="Merkez Depo ve Ankara Depo açılış stokları tanımlandı."),
        AuditLog(user_id=users['satis'].id, user_name=users['satis'].full_name, action="Sipariş Oluşturma", module="Satış", description="Yeni satış siparişleri sisteme girildi."),
        AuditLog(user_id=users['muhasebe'].id, user_name=users['muhasebe'].full_name, action="Fatura Kesildi", module="Finans", description="Teslim edilen siparişler faturalandırıldı.")
    ]
    db.session.add_all(logs)
    db.session.commit()

    print("=========================================================")
    print("  NEXORA ERP SEED DATA SUCCESSFULLY GENERATED!")
    print("=========================================================")
