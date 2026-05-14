#!/usr/bin/env python3
"""
Sample data creator for Online Sanat Galerisi
"""

from backend.app import app, db, User, Category, Artwork, Event, Discount
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample data for the application"""
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create Categories
        categories = [
            Category(name="Tablo", description="Dijital ve geleneksel tablolar"),
            Category(name="Heykel", description="3 boyutlu sanat eserleri"),
            Category(name="Fotoğraf", description="Profesyonel ve amatör fotoğraflar"),
            Category(name="Dijital Sanat", description="Dijital ortamda oluşturulan eserler"),
            Category(name="Seramik", description="Seramik sanat eserleri"),
            Category(name="Takı", description="El yapımı takılar"),
        ]
        
        for category in categories:
            db.session.add(category)
        db.session.commit()
        
        # Create Users
        users = [
            {
                'username': 'admin',
                'email': 'admin@galeri.com',
                'password': 'admin123',
                'user_type': 'admin',
                'bio': 'Sistem yöneticisi'
            },
            {
                'username': 'ahmet_sanatci',
                'email': 'ahmet@example.com',
                'password': 'sanat123',
                'user_type': 'artist',
                'bio': 'Profesyonel ressam, 15 yıllık deneyim'
            },
            {
                'username': 'ayse_sanatci',
                'email': 'ayse@example.com',
                'password': 'sanat123',
                'user_type': 'artist',
                'bio': 'Heykel ve seramik uzmanı'
            },
            {
                'username': 'mehmet_koleksiyoncu',
                'email': 'mehmet@example.com',
                'password': 'kole123',
                'user_type': 'collector',
                'bio': 'Modern sanat koleksiyoneri'
            },
            {
                'username': 'zeynep_koleksiyoncu',
                'email': 'zeynep@example.com',
                'password': 'kole123',
                'user_type': 'collector',
                'bio': 'Çağdaş sanat tutkunu'
            }
        ]
        
        created_users = []
        for user_data in users:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                user_type=user_data['user_type'],
                bio=user_data['bio']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users.append(user)
        
        db.session.commit()
        
        # Get artist users
        artists = [u for u in created_users if u.user_type == 'artist']
        
        # Create Artworks
        artworks_data = [
            {
                'title': 'Gün Batımı',
                'description': 'Ege kıyılarında gün batımının büyüleyici anları',
                'price': 250000,
                'image_url': 'artwork1.jpg',
                'artist': artists[0],
                'category': categories[0],  # Tablo
                'tags': 'gün batımı,deniz,manzara'
            },
            {
                'title': 'Şehir Işıkları',
                'description': 'Modern şehrin neon ışıkları altındaki hayat',
                'price': 320000,
                'image_url': 'artwork2.jpg',
                'artist': artists[0],
                'category': categories[3],  # Dijital Sanat
                'tags': 'şehir,ışık,modern'
            },
            {
                'title': 'Doğa Formu',
                'description': 'Organik formların heykelsel yorumu',
                'price': 450000,
                'image_url': 'artwork3.jpg',
                'artist': artists[1],
                'category': categories[1],  # Heykel
                'tags': 'doğa,heykel,organik'
            },
            {
                'title': 'Anı Yakala',
                'description': 'Sokak fotoğrafçılığının özgün örnekleri',
                'price': 180000,
                'image_url': 'artwork4.jpg',
                'artist': artists[0],
                'category': categories[2],  # Fotoğraf
                'tags': 'sokak,fotoğraf,an'
            },
            {
                'title': 'Mavi Seramik',
                'description': 'El yapımı seramik vazo, geleneksel tekniklerle',
                'price': 120000,
                'image_url': 'artwork5.jpg',
                'artist': artists[1],
                'category': categories[4],  # Seramik
                'tags': 'seramik,vazo,el yapımı'
            },
            {
                'title': 'Dijital Rüya',
                'description': 'Yapay zeka ile oluşturulan dijital sanat eseri',
                'price': 280000,
                'image_url': 'artwork6.jpg',
                'artist': artists[0],
                'category': categories[3],  # Dijital Sanat
                'tags': 'dijital,yapay zeka,rüya'
            }
        ]
        
        for artwork_data in artworks_data:
            artwork = Artwork(
                title=artwork_data['title'],
                description=artwork_data['description'],
                price=artwork_data['price'],
                image_url=artwork_data['image_url'],
                artist_id=artwork_data['artist'].id,
                category_id=artwork_data['category'].id,
                tags=artwork_data['tags']
            )
            db.session.add(artwork)
        
        db.session.commit()
        
        # Create Events/Workshops
        events_data = [
            {
                'title': 'Akrilik Boya Atölyesi',
                'description': 'Başlangıç seviyesi için akrilik boya teknikleri',
                'image_url': 'workshop1.jpg',
                'instructor': artists[0],
                'category': categories[0],  # Tablo
                'event_date': datetime.now() + timedelta(days=7),
                'duration_hours': 3,
                'max_participants': 12,
                'price': 35000,
                'location': 'Sanat Galerisi Atölyesi'
            },
            {
                'title': 'Seramik Temel Kursu',
                'description': 'Çamurdan sanat eseri oluşturma temelleri',
                'image_url': 'workshop2.jpg',
                'instructor': artists[1],
                'category': categories[4],  # Seramik
                'event_date': datetime.now() + timedelta(days=14),
                'duration_hours': 4,
                'max_participants': 8,
                'price': 45000,
                'location': 'Seramik Atölyesi'
            },
            {
                'title': 'Sokak Fotoğrafçılığı',
                'description': 'Şehir hayatını ölümsüzleştirme sanatı',
                'image_url': 'workshop3.jpg',
                'instructor': artists[0],
                'category': categories[2],  # Fotoğraf
                'event_date': datetime.now() + timedelta(days=21),
                'duration_hours': 5,
                'max_participants': 15,
                'price': 28000,
                'location': 'Şehir Merkezi'
            },
            {
                'title': 'Dijital Sanat Intro',
                'description': 'Dijital sanat araçlarını tanıma ve kullanma',
                'image_url': 'workshop4.jpg',
                'instructor': artists[0],
                'category': categories[3],  # Dijital Sanat
                'event_date': datetime.now() + timedelta(days=10),
                'duration_hours': 2,
                'max_participants': 20,
                'price': 20000,
                'location': 'Online'
            }
        ]
        
        for event_data in events_data:
            event = Event(
                title=event_data['title'],
                description=event_data['description'],
                image_url=event_data['image_url'],
                instructor_id=event_data['instructor'].id,
                category_id=event_data['category'].id,
                event_date=event_data['event_date'],
                duration_hours=event_data['duration_hours'],
                max_participants=event_data['max_participants'],
                price=event_data['price'],
                location=event_data['location']
            )
            db.session.add(event)
        
        db.session.commit()
        
        # Create Discount Codes
        discounts = [
            {
                'code': 'WELCOME10',
                'description': 'Hoş geldin indirim - %10',
                'discount_type': 'percentage',
                'discount_value': 1000,
                'min_amount': 10000,
                'max_uses': 100,
                'valid_until': datetime.now() + timedelta(days=30)
            },
            {
                'code': 'ARTIST20',
                'description': 'Sanatçı özel indirim - %20',
                'discount_type': 'percentage',
                'discount_value': 2000,
                'min_amount': 50000,
                'max_uses': 50,
                'valid_until': datetime.now() + timedelta(days=60)
            },
            {
                'code': 'WORKSHOP100',
                'description': 'Atölye indirim - 100 TL',
                'discount_type': 'fixed',
                'discount_value': 10000,
                'min_amount': 30000,
                'max_uses': 25,
                'valid_until': datetime.now() + timedelta(days=45)
            }
        ]
        
        for discount_data in discounts:
            discount = Discount(
                code=discount_data['code'],
                description=discount_data['description'],
                discount_type=discount_data['discount_type'],
                discount_value=discount_data['discount_value'],
                min_amount=discount_data['min_amount'],
                max_uses=discount_data['max_uses'],
                valid_until=discount_data['valid_until']
            )
            db.session.add(discount)
        
        db.session.commit()
        
        print("Örnek veriler başarıyla oluşturuldu!")
        print("\nKullanıcı Hesapları:")
        print("Admin: admin / admin123")
        print("Sanatçı 1: ahmet_sanatci / sanat123")
        print("Sanatçı 2: ayse_sanatci / sanat123")
        print("Koleksiyoncu 1: mehmet_koleksiyoncu / kole123")
        print("Koleksiyoncu 2: zeynep_koleksiyoncu / kole123")
        
        print("\nİndirim Kodları:")
        print("WELCOME10 - %10 indirim")
        print("ARTIST20 - %20 indirim")
        print("WORKSHOP100 - 100 TL indirim")

if __name__ == '__main__':
    create_sample_data()
