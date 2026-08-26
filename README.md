# NEXORA ERP — Enterprise Resource Planning & Distribution Management System

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![MySQL](https://img.shields.io/badge/MySQL-Supported-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)

**NEXORA ERP**, insbesondere für **Toptan Gıda ve Dağıtım Şirketleri** operasyonlarını uçtan uca yönetmek üzere geliştirilmiş, tam kapsamlı, kurumsal seviyede bir **Full-Stack ERP ve Dağıtım Yönetim Sistemi** web uygulamasıdır.

Sistem sadece basit bir CRUD paneli veya taslak arayüz değil; **Kullanıcı Yetkilendirme (RBAC), Stok, Depo, Satın Alma, Satış, Müşteri, Tedarikçi, Sipariş, Sevkiyat, Faturalama, Cari Hesap, Finans, Raporlama ve Audit Logging** süreçlerini birbirine bağlı ve gerçek zamanlı iş kurallarıyla (Business Logic) yöneten profesyonel bir yazılım ürünüdür.

---

## 🌟 Öne Çıkan Modüller ve Özellikler

### 1. 🔐 Güvenlik ve Role-Based Access Control (RBAC)
- **Werkzeug Password Hashing**: Şifreler güvenli hash formatında saklanır.
- **Flask-Login Session Yönetimi**: Oturum ve beni hatırla mekanizması.
- **5 Hazır Sistem Rolü**:
  - `Admin`: Tüm modüllere ve ayarlar/işlem loglarına tam erişim.
  - `Yönetici`: Dashboard, raporlar, satış, satın alma, stok ve finans erişimi.
  - `Satış Personeli`: Müşteriler, teklifler, satış siparişleri.
  - `Depo Personeli`: Ürünler, stok hareketleri, depolar arası transfer, lot/SKT takibi, sevkiyat.
  - `Muhasebe`: Faturalar, cari hesaplar, tahsilat, ödeme ve finans raporları.
- **Backend seviyesinde yetkilendirme** (`@role_required` ve `@permission_required` dekoratörleri).

### 2. 📊 Canlı Dağıtım Gösterge Paneli (Dashboard)
- **Gerçek Zamanlı KPI Kartları**: Toplam Satış, Bugünkü Satış, Bekleyen Sipariş, Kritik Stok, Bekleyen Tahsilat ve Bu Ayki Ciro.
- **Chart.js Entegrasyonu**:
  - Aylık Satış Trend Grafiği (Çizgi Grafik)
  - En Çok Satan Ürünler (Çubuk Grafik)
  - Kategori Bazlı Satış Dağılımı (Halka Grafik)
  - Depo Stok Dağılımı (Pasta Grafik)

### 3. 🥛 Gıda ERP'sine Özel Lot & SKT (Son Kullanma Tarihi) Takibi
- Her ürünün Parti (LOT) numarası, Üretim Tarihi ve Son Kullanma Tarihi (SKT) takip edilir.
- **Otomatik SKT Uyarı Sistemi**: SKT'si 30 gün içinde dolacak ürünler dashboard ve üst bildirim çubuğunda uyarı olarak gösterilir.

### 4. 🏢 Çoklu Depo ve Depolar Arası Transfer
- Birden fazla fiziksel depo (Örn: *Merkez Depo - İstanbul, Ankara Lojistik Deposu, İzmir Bölge Deposu*).
- Depolar arası stok transfer süreci.

### 5. 🛒 Satış ve Sipariş Yönetimi Workflow
- **Akış**: `Teklif` &rarr; `Sipariş` &rarr; `Sevkiyat` &rarr; `Fatura` &rarr; `Tahsilat`.
- **Otomatik Stok Kontrolü**: Sipariş oluşturulurken depodaki stok miktarları kontrol edilir, yetersiz stok durumunda uyarı verir.
- Tekliflerin tek tıkla satış siparişine dönüştürülmesi.

### 6. 📦 Satın Alma ve Mal Kabul Süreci
- **Akış**: `Talep` &rarr; `Satın Alma Siparişi` &rarr; `Mal Kabul` &rarr; `Stok Girişi & LOT Tanımı`.
- Mal kabulü yapıldığında ilgili depodaki stok otomatik artar ve lot/SKT kayıtları oluşturulur.

### 7. 🚛 Sevkiyat ve Lojistik Yönetimi
- Dağıtım filosu araçları (Frigo soğutuculu kamyon, kamyonet, tır) ve şoför atamaları.
- Sevkiyat durumları: `Hazırlanıyor` &rarr; `Yolda` &rarr; `Teslim Edildi`.
- Teslim edildiğinde stok çıkışı otomatik gerçekleşir.

### 8. 💰 Faturalama, Cari Hesap ve Finans
- **Satış ve Alış Faturaları**: Fatura kesildiğinde ilgili müşterinin/tedarikçinin Cari Hesabına (Ledger) Borç/Alacak otomatik işlenir.
- **Tahsilat ve Ödemeler**: Nakit, Banka Havalesi/EFT, Kredi Kartı veya Çek yöntemleri. Tahsilat veya ödeme yapıldığında Kasa/Banka bakiyesi ve cari bakiye anında güncellenir.
- **Profesyonel Fatura Çıktısı**: Resmi fatura belgeleri için yazdırılabilir/PDF uyumlu görünüm.

### 9. 📈 Gelişmiş Raporlama
- **Satış Raporu**: Tarih, müşteri ve ürün bazlı filtreler.
- **Stok Değerleme Raporu**: Envanter maliyeti ve stok durumu.
- **Finans ve Nakit Akışı**: Gelir/Gider ve tahsilat/ödeme dengesi.
- **Kârlılık Raporu**: Ürün bazında Alış Fiyatı &rarr; Satış Fiyatı &rarr; Kâr ve Kâr Oranı (%) hesabı.

### 10. 🛡️ Audit Log (İşlem Geçmişi)
- Kullanıcıların gerçekleştirdiği kritik ekleme, güncelleme, silme ve giriş/çıkış işlemleri tarih, modül, kullanıcı ve IP adresi ile loglanır.

---

## 🛠️ Teknoloji Stack

* **Backend**: Python 3.14, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Werkzeug, python-dotenv
* **Database**: MySQL / SQLite (PyMySQL & SQLAlchemy ORM)
* **Frontend**: HTML5, CSS3 (Custom Dark/Light Theme), Bootstrap 5.3, Bootstrap Icons, Chart.js
* **Mimari**: Modular Blueprint MVC Architecture & Service Layer Pattern

---

## 💻 Kurulum Adımları (Installation Guide)

### 1. Repoyu Klonlayın
```bash
git clone https://github.com/username/NEXORAERP.git
cd NEXORAERP
```

### 2. Sanal Ortam (Virtual Environment) Oluşturun ve Aktif Edin
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Çevre Değişkenlerini (`.env`) Yapılandırın
Kök dizinde `.env` dosyası oluşturun (örnek `.env.example` dosyasında verilmiştir):
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=nexora-erp-super-secret-key-2026-production

# MySQL Bağlantısı Örneği:
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/nexora_erp

# SQLite Otomatik Fallback (Varsayılan):
DATABASE_URL=sqlite:///nexora_erp.db
```

### 5. Veritabanını Oluşturun ve Demo Verilerini Yükleyin
Uygulama ilk çalıştırıldığında veritabanı tablolarını otomatik oluşturur ve demo verilerini yükler. Dilerseniz manuel seed komutunu çalıştırabilirsiniz:
```bash
python seed_cli.py
```

### 6. Uygulamayı Çalıştırın
```bash
python run.py
```
Tarayıcınızdan `http://127.0.0.1:5000` adresine gidin.

---

## 🔑 Demo Kullanıcı Hesapları (Varsayılan Şifre: `Nexora123!`)

| Rol | Kullanıcı Adı | E-Posta | Şifre |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin@nexoraerp.com` | `Nexora123!` |
| **Yönetici** | `yonetici` | `yonetici@nexoraerp.com` | `Nexora123!` |
| **Satış Personeli** | `satis` | `satis@nexoraerp.com` | `Nexora123!` |
| **Depo Personeli** | `depo` | `depo@nexoraerp.com` | `Nexora123!` |
| **Muhasebe** | `muhasebe` | `muhasebe@nexoraerp.com` | `Nexora123!` |

---

## 📁 Proje Klasör Yapısı

```
NEXORAERP/
├── app/
│   ├── __init__.py          # Flask App Factory & extension init
│   ├── config.py            # Uygulama konfigürasyonu (.env entegrasyonu)
│   ├── models/              # İlişkisel SQLAlchemy Veritabanı Modelleri
│   │   ├── user.py          # User, Role, Permission, AuditLog
│   │   ├── party.py         # Customer, Supplier
│   │   ├── product.py       # Category, Brand, Unit, Product, StockLot
│   │   ├── warehouse.py     # Warehouse, WarehouseStock, StockMovement
│   │   ├── sales.py         # SalesQuote, SalesOrder
│   │   ├── purchase.py      # PurchaseRequest, PurchaseOrder
│   │   ├── logistics.py     # Vehicle, Driver, Shipment
│   │   ├── finance.py       # Invoice, CurrentAccount, Collection, Payment
│   │   └── notification.py  # Notification
│   ├── services/            # İş Mantığı Katmanı (Business Logic Services)
│   │   ├── stock_service.py # Stok düşümü, transfer, lot yönetimi
│   │   ├── sales_service.py # Sipariş dönüştürme ve stok kontrolü
│   │   ├── purchase_service.py # Mal kabul ve stok girişi
│   │   ├── finance_service.py  # Fatura kesme, cari ekstre ve kasa hareketi
│   │   └── report_service.py   # Raporlama hesaplamaları
│   ├── routes/              # Flask Blueprints
│   │   ├── auth.py, dashboard.py, customers.py, suppliers.py, products.py
│   │   ├── warehouses.py, inventory.py, sales.py, purchases.py, logistics.py
│   │   └── finance.py, reports.py, admin.py, api.py
│   ├── static/
│   │   ├── css/style.css    # Özel kurumsal Dark/Light CSS teması
│   │   ├── js/main.js       # Tema değiştirici, sidebar, toast bildirimleri
│   │   └── js/dashboard.js  # Chart.js canlı grafik yükleyici
│   └── templates/           # Jinja2 HTML5 Şablonları
├── seed_cli.py              # Demo veri yükleme CLI aracı
├── run.py                   # Uygulama ana başlatıcı
├── requirements.txt         # Python paket bağımlılıkları
└── README.md
```

---

## 🔒 Güvenlik Notları
- Şifreler hiçbir zaman düz metin olarak kaydedilmez (`werkzeug.security`).
- Hassas bilgiler `.env` dosyasında tutulur ve `.gitignore` ile kaynak koddan hariç tutulur.
- SQL Injection ve XSS saldırılarına karşı SQLAlchemy ORM ve Jinja2 escaping koruması mevcuttur.

---

## 📜 Lisans
Bu proje MIT Lisansı ile lisanslanmıştır.
