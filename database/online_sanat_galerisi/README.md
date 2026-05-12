# Online Sanat Galerisi

Flask ve PostgreSQL kullanılarak geliştirilmiş online sanat galerisi projesi.

## Kurulum

### 1. Gerekli Paketlerin Kurulumu
```bash
pip install -r requirements.txt
```

### 2. Veritabanı Kurulumu
PostgreSQL'i kurun ve yeni bir veritabanı oluşturun:
```sql
CREATE DATABASE online_sanat_galerisi;
```

### 3. Çevre Değişkenleri
`.env` dosyasını oluşturun:
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://username:password@localhost/online_sanat_galerisi
```

### 4. Veritabanı Migrasyonu
```bash
cd backend
python app.py
```

### 5. Uygulamayı Çalıştırma
```bash
python backend/app.py
```

## Proje Yapısı

```
online_sanat_galerisi/
├── backend/
│   └── app.py              # Flask uygulaması
├── frontend/
│   ├── templates/          # HTML şablonları
│   └── static/            # CSS, JS ve resimler
├── database/
│   └── migrations/        # Veritabanı migrasyonları
├── requirements.txt        # Python bağımlılıkları
├── .env.example           # Çevre değişkenleri şablonu
└── README.md              # Proje dokümantasyonu
```

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Sanat eseri yükleme ve sergileme
- Arama ve filtreleme
- Satış ve sipariş yönetimi
- Admin paneli
- Responsive tasarım

## Kullanılan Teknolojiler

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Veritabanı**: PostgreSQL
- **Frontend**: Bootstrap 5, JavaScript
- **Diğer**: Jinja2, Werkzeug

## API Endpoints

### Kullanıcı İşlemleri
- `POST /register` - Kullanıcı kayıt
- `POST /login` - Kullanıcı giriş
- `GET /profile` - Profil bilgileri
- `POST /logout` - Çıkış

### Sanat Eserleri
- `GET /` - Ana sayfa
- `GET /gallery` - Galeri sayfası
- `GET /artwork/<id>` - Eser detayı
- `POST /artwork/upload` - Eser yükleme

### Admin
- `GET /admin` - Admin paneli

## Lisans

MIT License
