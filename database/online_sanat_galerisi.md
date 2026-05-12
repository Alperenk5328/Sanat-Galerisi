# Online Sanat Galerisi Projesi

## Proje Açıklaması
Bu proje, kullanıcıların sanat eserlerini sergileyebileceği, keşfedebileceği ve satın alabileceği bir online sanat galerisi platformudur.

## Temel Özellikler

### 1. Kullanıcı Yönetimi
- Kullanıcı kayıt ve giriş sistemi
- Sanatçı ve koleksiyoncu profilleri
- Kullanıcı profillerinin düzenlenmesi

### 2. Sanat Eseri Yönetimi
- Sanat eserleri yükleme (resim, başlık, açıklama, fiyat)
- Kategorilere ayırma (tablo, heykel, fotoğraf, dijital sanat vb.)
- Etiketleme sistemi
- Arama ve filtreleme özellikleri

### 3. Galeri Özellikleri
- Sanat eserlerini grid/liste görünümünde sergileme
- Detaylı eser sayfaları
- Sanatçı profilleri ve eserleri
- Sanat eserlerini beğenme/favorilere ekleme
- Yorum ve değerlendirme sistemi

### 4. Satış ve Alışveriş
- Sepet sistemi
- Ödeme entegrasyonu
- Sipariş takibi
- Sanatçıya komisyon sistemi

### 5. Admin Paneli
- Kullanıcı yönetimi
- Sanat eseri onay sistemi
- Kategori yönetimi
- Satış raporları

## Teknoloji Kullanımı

### Frontend
- HTML5, CSS3, JavaScript
- Responsive tasarım
- Modern UI framework (Bootstrap veya Tailwind CSS)

### Backend
- Node.js veya Python (Django/Flask)
- RESTful API
- Veritabanı entegrasyonu

### Veritabanı
- PostgreSQL veya MySQL
- Kullanıcı, eser, kategori, sipariş tabloları

## Proje Yapısı

```
online_sanat_galerisi/
├── frontend/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── assets/
├── backend/
│   ├── api/
│   ├── models/
│   ├── controllers/
│   └── config/
├── database/
│   └── migrations/
└── docs/
```

## Geliştirme Aşamaları

1. **Aşama 1**: Temel proje yapısı ve veritabanı tasarımı
2. **Aşama 2**: Kullanıcı kayıt/giriş sistemi
3. **Aşama 3**: Sanat eseri yükleme ve galeri görünümü
4. **Aşama 4**: Arama ve filtreleme özellikleri
5. **Aşama 5**: Satış ve ödeme sistemi
6. **Aşama 6**: Admin paneli ve raporlama

## Veritabanı Şeması

### Users Tablosu
- id (PK)
- username
- email
- password
- user_type (artist, collector, admin)
- profile_image
- bio
- created_at
- updated_at

### Artworks Tablosu
- id (PK)
- title
- description
- price
- image_url
- artist_id (FK)
- category_id (FK)
- tags
- status (active, sold, pending)
- created_at
- updated_at

### Categories Tablosu
- id (PK)
- name
- description
- created_at

### Orders Tablosu
- id (PK)
- user_id (FK)
- artwork_id (FK)
- total_price
- status (pending, completed, cancelled)
- created_at

## API Endpoints

### Kullanıcı İşlemleri
- POST /api/register - Kullanıcı kayıt
- POST /api/login - Kullanıcı giriş
- GET /api/profile - Profil bilgileri
- PUT /api/profile - Profil güncelleme

### Sanat Eserleri
- GET /api/artworks - Tüm eserleri listele
- GET /api/artworks/:id - Eser detayı
- POST /api/artworks - Yeni eser ekle
- PUT /api/artworks/:id - Eser güncelle
- DELETE /api/artworks/:id - Eser sil

### Kategoriler
- GET /api/categories - Kategorileri listele
- POST /api/categories - Yeni kategori ekle

## Güvenlik Özellikleri
- JWT token authentication
- Input validation ve sanitization
- File upload güvenliği
- SQL injection koruması
- XSS koruması

## Performans Optimizasyonu
- Image lazy loading
- Database indexing
- Caching sistemi
- CDN entegrasyonu

## Deployment
- Cloud platform (AWS, Google Cloud, Azure)
- CI/CD pipeline
- Monitoring ve logging
