from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///online_sanat_galerisi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images/artworks'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), default='collector')  # artist, collector, admin
    profile_image = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with artworks
    artworks = db.relationship('Artwork', backref='artist', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with artworks
    artworks = db.relationship('Artwork', backref='category', lazy=True)

class Artwork(db.Model):
    __tablename__ = 'artworks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    tags = db.Column(db.String(500))
    status = db.Column(db.String(20), default='active')  # active, sold, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with orders
    orders = db.relationship('Order', backref='artwork', lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=True)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Event/Workshop Models
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Integer, default=2)
    max_participants = db.Column(db.Integer, nullable=False)
    current_participants = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')  # active, cancelled, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = db.relationship('User', backref='instructed_events')
    category = db.relationship('Category', backref='events')
    reservations = db.relationship('Reservation', backref='event', lazy=True)
    comments = db.relationship('EventComment', backref='event', lazy=True)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    participant_count = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, cancelled, completed
    approved = db.Column(db.Boolean, default=False)
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='reservations')

# Favorites Model
class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='favorites')
    artwork = db.relationship('Artwork', backref='favorites')

# Comments and Ratings
class ArtworkComment(db.Model):
    __tablename__ = 'artwork_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)  # 1-5 stars
    helpful_votes = db.Column(db.Integer, default=0)
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='artwork_comments')
    artwork = db.relationship('Artwork', backref='comments')

class EventComment(db.Model):
    __tablename__ = 'event_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=0)  # 1-5 stars
    helpful_votes = db.Column(db.Integer, default=0)
    admin_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='event_comments')

# Shopping Cart
class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='cart_items')
    artwork = db.relationship('Artwork')
    event = db.relationship('Event')

# Discount/Coupon System
class Discount(db.Model):
    __tablename__ = 'discounts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), default='percentage')  # percentage, fixed
    discount_value = db.Column(db.Integer, nullable=False)
    min_amount = db.Column(db.Integer, default=0)
    max_uses = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    artwork = db.relationship('Artwork', backref='discounts')
    target_user = db.relationship('User', backref='targeted_discounts')

# Customer Support
class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='support_tickets')
    responses = db.relationship('SupportResponse', backref='ticket', lazy=True)

class SupportResponse(db.Model):
    __tablename__ = 'support_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # can be admin or customer
    message = db.Column(db.Text, nullable=False)
    is_admin_response = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='support_responses')

# Comparison System
class Comparison(db.Model):
    __tablename__ = 'comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comparison_type = db.Column(db.String(20), nullable=False)  # artwork, event
    item_ids = db.Column(db.Text, nullable=False)  # JSON array of item IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='comparisons')

# Statistics Tracking
class ArtworkView(db.Model):
    __tablename__ = 'artwork_views'
    
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45))
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

class EventView(db.Model):
    __tablename__ = 'event_views'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45))
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    artworks = Artwork.query.filter_by(status='active').order_by(Artwork.created_at.desc()).limit(12).all()
    categories = Category.query.all()
    return render_template('index.html', artworks=artworks, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Giriş başarılı!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'collector')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor!', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, user_type=user_type)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kayıt başarılı! Lütfen giriş yapın.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı!', 'info')
    return redirect(url_for('index'))

@app.route('/gallery')
def gallery():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Artwork.query.filter_by(status='active')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            db.or_(
                Artwork.title.contains(search),
                Artwork.description.contains(search),
                Artwork.tags.contains(search)
            )
        )
    
    artworks = query.order_by(Artwork.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    categories = Category.query.all()
    
    return render_template('gallery.html', artworks=artworks, categories=categories, 
                         selected_category=category_id, search=search)

@app.route('/artwork/<int:id>')
def artwork_detail(id):
    artwork = Artwork.query.get_or_404(id)
    
    # Track view
    if current_user.is_authenticated:
        view = ArtworkView(artwork_id=id, user_id=current_user.id)
    else:
        view = ArtworkView(artwork_id=id, ip_address=request.remote_addr)
    db.session.add(view)
    db.session.commit()
    
    # Sorting comments
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'highest':
        comments = ArtworkComment.query.filter_by(artwork_id=id).order_by(ArtworkComment.rating.desc(), ArtworkComment.created_at.desc()).all()
    elif sort_by == 'helpful':
        comments = ArtworkComment.query.filter_by(artwork_id=id).order_by(ArtworkComment.helpful_votes.desc(), ArtworkComment.created_at.desc()).all()
    else:
        comments = ArtworkComment.query.filter_by(artwork_id=id).order_by(ArtworkComment.created_at.desc()).all()
        
    avg_rating = sum(c.rating for c in comments) / len(comments) if comments else 0
    view_count = ArtworkView.query.filter_by(artwork_id=id).count()
    favorite_count = Favorite.query.filter_by(artwork_id=id).count()
    
    has_bought = False
    if current_user.is_authenticated:
        has_bought = Order.query.filter_by(user_id=current_user.id, artwork_id=id).first() is not None
    
    return render_template('artwork_detail.html', artwork=artwork, comments=comments, sort_by=sort_by, avg_rating=avg_rating, view_count=view_count, favorite_count=favorite_count, has_bought=has_bought)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username', current_user.username).strip()
        email = request.form.get('email', current_user.email).strip()
        bio = request.form.get('bio', current_user.bio or '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email:
            flash('Kullanıcı adı ve e-posta boş olamaz.', 'error')
            return redirect(url_for('profile'))

        if username != current_user.username and User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return redirect(url_for('profile'))

        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('Bu e-posta zaten kullanılıyor.', 'error')
            return redirect(url_for('profile'))

        if password:
            if password != confirm_password:
                flash('Şifreler eşleşmiyor.', 'error')
                return redirect(url_for('profile'))
            current_user.set_password(password)

        current_user.username = username
        current_user.email = email
        current_user.bio = bio
        db.session.commit()

        flash('Profiliniz güncellendi.', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)

@app.route('/add_artwork', methods=['GET', 'POST'])
@login_required
def add_artwork():
    if current_user.user_type != 'artist':
        flash('Sadece sanatçılar eser ekleyebilir.', 'error')
        return redirect(url_for('profile'))

    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price_input = request.form.get('price', '0')
        image_url = request.form.get('image_url')
        category_id = request.form.get('category_id')
        tags = request.form.get('tags')

        if not title or not description or not category_id:
            flash('Başlık, açıklama ve kategori gereklidir.', 'error')
            return render_template('add_artwork.html', categories=categories)

        try:
            price = int(float(price_input) * 100)
        except ValueError:
            flash('Geçerli bir fiyat girin.', 'error')
            return render_template('add_artwork.html', categories=categories)

        artwork = Artwork(
            title=title,
            description=description,
            price=price,
            image_url=image_url,
            artist_id=current_user.id,
            category_id=int(category_id),
            tags=tags,
            status='active'
        )
        db.session.add(artwork)
        db.session.commit()

        flash('Eser başarıyla eklendi!', 'success')
        return redirect(url_for('profile'))

    return render_template('add_artwork.html', categories=categories)

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.user_type != 'artist':
        flash('Sadece sanatçılar etkinlik ekleyebilir.', 'error')
        return redirect(url_for('profile'))

    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        category_id = request.form.get('category_id')
        event_date_str = request.form.get('event_date')
        duration_hours = request.form.get('duration_hours', '2')
        max_participants = request.form.get('max_participants', '1')
        location = request.form.get('location')

        if not title or not description or not category_id or not event_date_str or not location:
            flash('Başlık, açıklama, tarih, kategori ve lokasyon gereklidir.', 'error')
            return render_template('add_event.html', categories=categories)

        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
            duration_hours = int(duration_hours)
            max_participants = int(max_participants)
        except ValueError:
            flash('Geçerli bir tarih ve sayı değerleri girin.', 'error')
            return render_template('add_event.html', categories=categories)

        event = Event(
            title=title,
            description=description,
            image_url=image_url,
            instructor_id=current_user.id,
            category_id=int(category_id),
            event_date=event_date,
            duration_hours=duration_hours,
            max_participants=max_participants,
            location=location,
            price=0,
            status='active'
        )
        db.session.add(event)
        db.session.commit()

        flash('Etkinlik başarıyla oluşturuldu!', 'success')
        return redirect(url_for('profile'))

    return render_template('add_event.html', categories=categories)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username')
    email = request.form.get('email')
    bio = request.form.get('bio')
    
    # Validate inputs
    if not username or not email:
        flash('Kullanıcı adı ve e-posta zorunludur!', 'error')
        return redirect(url_for('profile'))
    
    # Check if username is taken by another user
    if username != current_user.username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Bu kullanıcı adı zaten kullanılıyor!', 'error')
            return redirect(url_for('profile'))
    
    # Check if email is taken by another user
    if email != current_user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Bu e-posta adresi zaten kullanılıyor!', 'error')
            return redirect(url_for('profile'))
    
    # Update user
    current_user.username = username
    current_user.email = email
    current_user.bio = bio
    current_user.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Profil başarıyla güncellendi!', 'success')
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_password or not new_password or not confirm_password:
        flash('Tüm şifre alanları zorunludur!', 'error')
        return redirect(url_for('profile'))
    
    if not current_user.check_password(current_password):
        flash('Mevcut şifreniz hatalı!', 'error')
        return redirect(url_for('profile'))
    
    if new_password != confirm_password:
        flash('Yeni şifreler eşleşmiyor!', 'error')
        return redirect(url_for('profile'))
    
    if len(new_password) < 6:
        flash('Şifre en az 6 karakter olmalıdır!', 'error')
        return redirect(url_for('profile'))
    
    current_user.set_password(new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Şifreniz başarıyla değiştirildi!', 'success')
    return redirect(url_for('profile'))

@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('Fotoğraf seçilmedi!', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['profile_picture']
    if file.filename == '':
        flash('Fotoğraf seçilmedi!', 'error')
        return redirect(url_for('profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add user ID to filename to make it unique
        filename = f"user_{current_user.id}_{filename}"
        
        # Create directory if it doesn't exist
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], '../static/images/profiles')
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        
        # Update user profile picture
        current_user.profile_image = filename
        current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Profil fotoğrafı başarıyla güncellendi!', 'success')
    else:
        flash('Geçersiz dosya formatı!', 'error')
    
    return redirect(url_for('profile'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from werkzeug.utils import secure_filename

@app.route('/events')
def events():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Event.query.filter_by(status='active')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            db.or_(
                Event.title.contains(search),
                Event.description.contains(search),
                Event.location.contains(search)
            )
        )
    
    events = query.order_by(Event.event_date.asc()).paginate(
        page=page, per_page=12, error_out=False
    )
    categories = Category.query.all()
    
    return render_template('events.html', events=events, categories=categories, 
                         selected_category=category_id, search=search)

@app.route('/event/<int:id>')
def event_detail(id):
    event = Event.query.get_or_404(id)
    
    # Track view
    if current_user.is_authenticated:
        view = EventView(event_id=id, user_id=current_user.id)
    else:
        view = EventView(event_id=id, ip_address=request.remote_addr)
    db.session.add(view)
    db.session.commit()
    
    # Sorting comments
    sort_by = request.args.get('sort', 'newest')
    if sort_by == 'highest':
        comments = EventComment.query.filter_by(event_id=id).order_by(EventComment.rating.desc(), EventComment.created_at.desc()).all()
    elif sort_by == 'helpful':
        comments = EventComment.query.filter_by(event_id=id).order_by(EventComment.helpful_votes.desc(), EventComment.created_at.desc()).all()
    else:
        comments = EventComment.query.filter_by(event_id=id).order_by(EventComment.created_at.desc()).all()
        
    avg_rating = sum(c.rating for c in comments) / len(comments) if comments else 0
    view_count = EventView.query.filter_by(event_id=id).count()
    occupancy_rate = (event.current_participants / event.max_participants) * 100 if event.max_participants > 0 else 0
    
    has_attended = False
    if current_user.is_authenticated:
        has_attended = Reservation.query.filter_by(user_id=current_user.id, event_id=id).first() is not None
    
    return render_template('event_detail.html', event=event, comments=comments, sort_by=sort_by, avg_rating=avg_rating, view_count=view_count, occupancy_rate=occupancy_rate, has_attended=has_attended)

@app.route('/favorites')
@login_required
def favorites():
    favorite_artworks = Favorite.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorite_artworks)

@app.route('/toggle_favorite/<int:artwork_id>')
@login_required
def toggle_favorite(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, artwork_id=artwork_id).first()
    
    if favorite:
        db.session.delete(favorite)
        flash('Eser favorilerden çıkarıldı.', 'info')
    else:
        favorite = Favorite(user_id=current_user.id, artwork_id=artwork_id)
        db.session.add(favorite)
        flash('Eser favorilere eklendi.', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('gallery'))

@app.route('/reserve_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def reserve_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        participant_count = int(request.form.get('participant_count', 1))
        
        if event.current_participants + participant_count > event.max_participants:
            flash('Yeterli kontenjan yok!', 'error')
            return redirect(url_for('event_detail', id=event_id))
        
        reservation = Reservation(
            user_id=current_user.id,
            event_id=event_id,
            participant_count=participant_count,
            total_price=0,
            approved=False
        )
        
        event.current_participants += participant_count
        
        db.session.add(reservation)
        db.session.commit()
        
        flash('Rezervasyon başarıyla oluşturuldu!', 'success')
        return redirect(url_for('my_reservations'))
    
    return render_template('reserve_event.html', event=event)

@app.route('/my_reservations')
@login_required
def my_reservations():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.reservation_date.desc()).all()
    return render_template('my_reservations.html', reservations=reservations)

@app.route('/update_reservation/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def update_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('Bu rezervasyonu güncelleme yetkiniz yok!', 'error')
        return redirect(url_for('my_reservations'))
    
    if request.method == 'POST':
        participant_count = int(request.form.get('participant_count', 1))
        
        if participant_count != reservation.participant_count:
            # Calculate participants difference
            diff = participant_count - reservation.participant_count
            
            if reservation.event.current_participants + diff > reservation.event.max_participants:
                flash('Yeterli kontenjan yok!', 'error')
                return redirect(url_for('update_reservation', reservation_id=reservation_id))
            
            reservation.event.current_participants += diff
            reservation.participant_count = participant_count
            reservation.total_price = 0
            
            db.session.commit()
            flash('Rezervasyon güncellendi!', 'success')
            return redirect(url_for('my_reservations'))
    
    return render_template('update_reservation.html', reservation=reservation)

@app.route('/cancel_reservation/<int:reservation_id>')
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.user_id != current_user.id:
        flash('Bu rezervasyonu iptal etme yetkiniz yok!', 'error')
        return redirect(url_for('my_reservations'))
    
    reservation.event.current_participants -= reservation.participant_count
    reservation.status = 'cancelled'
    
    db.session.commit()
    flash('Rezervasyon iptal edildi!', 'info')
    return redirect(url_for('my_reservations'))

@app.route('/approve_reservation/<int:reservation_id>')
@login_required
def approve_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    if reservation.event.instructor_id != current_user.id:
        flash('Bu rezervasyonu onaylama yetkiniz yok!', 'error')
        return redirect(url_for('profile'))
    
    reservation.approved = True
    db.session.commit()
    flash('Rezervasyon onaylandı!', 'success')
    return redirect(url_for('profile'))

@app.route('/approve_order/<int:order_id>')
@login_required
def approve_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.artwork.artist_id != current_user.id:
        flash('Bu siparişi onaylama yetkiniz yok!', 'error')
        return redirect(url_for('profile'))
    
    order.approved = True
    order.status = 'completed'
    db.session.commit()
    flash('Sipariş onaylandı!', 'success')
    return redirect(url_for('profile'))

@app.route('/cancel_order/<int:order_id>')
@login_required
def cancel_order(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Bu siparişi iptal etme yetkiniz yok!', 'error')
        return redirect(url_for('my_orders'))
    
    if order.status != 'pending':
        flash('Bu sipariş artık iptal edilemez.', 'warning')
        return redirect(url_for('my_orders'))
    
    order.status = 'cancelled'
    order.approved = False
    
    if order.artwork:
        order.artwork.status = 'active'
    
    db.session.commit()
    flash('Sipariş iptal edildi!', 'info')
    return redirect(url_for('my_orders'))

@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.artwork.price if item.artwork else item.event.price for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<item_type>/<int:item_id>')
@login_required
def add_to_cart(item_type, item_id):
    if item_type == 'artwork':
        item = Artwork.query.get_or_404(item_id)
        existing = Cart.query.filter_by(user_id=current_user.id, artwork_id=item_id).first()
    elif item_type == 'event':
        flash('Etkinlikler sepete eklenemez. Lütfen rezervasyon yapın.', 'warning')
        return redirect(url_for('reserve_event', event_id=item_id))
    else:
        flash('Geçersiz ürün tipi!', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if existing:
        flash('Bu ürün zaten sepetinizde!', 'info')
    else:
        cart_item = Cart(
            user_id=current_user.id,
            artwork_id=item_id if item_type == 'artwork' else None,
            event_id=None
        )
        db.session.add(cart_item)
        flash('Ürün sepete eklendi!', 'success')
    
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_cart/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    
    if cart_item.user_id != current_user.id:
        flash('Bu ürünü sepetten çıkarma yetkiniz yok!', 'error')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Ürün sepetten çıkarıldı!', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Sepetiniz boş!', 'error')
        return redirect(url_for('cart'))
    
    total = sum(item.artwork.price if item.artwork else item.event.price for item in cart_items)
    
    if request.method == 'POST':
        # Process payment (simulation)
        payment_method = request.form.get('payment_method')
        discount_code = request.form.get('discount_code')
        
        discount = None
        if discount_code:
            discount = Discount.query.filter_by(code=discount_code, is_active=True).first()
            if discount and discount.used_count < discount.max_uses:
                # Check target user
                if discount.target_user_id and discount.target_user_id != current_user.id:
                    flash('Bu indirim kodu size özel değil!', 'error')
                    return render_template('checkout.html', cart_items=cart_items, total=total)
                
                # Check artwork specific
                if discount.artwork_id and not any(item.artwork_id == discount.artwork_id for item in cart_items):
                    flash('Bu indirim kodu sepetinizdeki ürünler için geçerli değil!', 'error')
                    return render_template('checkout.html', cart_items=cart_items, total=total)
                
                discount.used_count += 1
            else:
                flash('Geçersiz veya süresi dolmuş indirim kodu!', 'error')
                return render_template('checkout.html', cart_items=cart_items, total=total)
        
        # Create orders
        for item in cart_items:
            item_price = item.artwork.price if item.artwork else item.event.price
            
            # Apply discount specific to this item if it matches, or to all if no artwork_id
            if discount:
                applies = False
                if discount.artwork_id:
                    if discount.artwork_id == item.artwork_id:
                        applies = True
                else:
                    applies = True # Global discount
                
                if applies:
                    if discount.discount_type == 'percentage':
                        # discount_value is integer like 10 for 10% or 1000 for 10%?
                        # Assume it's a direct percentage. e.g. 10 means 10%. 
                        # Wait, create_sample_data set 10% as 1000? Let's use it properly. If it's 10, then 10%.
                        # To be safe, if discount_value > 100, we treat it like fixed? No, we trust the DB type.
                        # We will just do (discount.discount_value / 100.0)
                        # Let's adjust to common percentage logic: discount_value is 10 for 10%.
                        discount_amount = int(item_price * (discount.discount_value / 100.0))
                        item_price = max(0, item_price - discount_amount)
                    else: # fixed
                        item_price = max(0, item_price - discount.discount_value)
            
            if item.artwork:
                order = Order(
                    user_id=current_user.id,
                    artwork_id=item.artwork_id,
                    total_price=item_price,
                    approved=False
                )
                item.artwork.status = 'sold'
            elif item.event:
                order = Order(
                    user_id=current_user.id,
                    artwork_id=None,
                    total_price=item_price,
                    approved=False
                )
                # Create reservation for event
                reservation = Reservation(
                    user_id=current_user.id,
                    event_id=item.event_id,
                    participant_count=1,
                    total_price=item_price,
                    approved=False
                )
                db.session.add(reservation)
            
            db.session.add(order)
        
        # Clear cart
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        flash('Ödeme başarıyla tamamlandı!', 'success')
        return redirect(url_for('my_orders'))
    
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/add_discount/<int:artwork_id>', methods=['GET', 'POST'])
@login_required
def add_discount(artwork_id):
    if current_user.user_type != 'artist':
        flash('Sadece sanatçılar kupon oluşturabilir.', 'error')
        return redirect(url_for('profile'))
        
    artwork = Artwork.query.get_or_404(artwork_id)
    if artwork.artist_id != current_user.id:
        flash('Sadece kendi eserleriniz için kupon oluşturabilirsiniz.', 'error')
        return redirect(url_for('profile'))
        
    if request.method == 'POST':
        code = request.form.get('code')
        discount_type = request.form.get('discount_type')
        discount_value = int(request.form.get('discount_value', 0))
        target_username = request.form.get('target_username')
        
        if not code or discount_value <= 0:
            flash('Kupon kodu ve indirim değeri zorunludur.', 'error')
            return render_template('add_discount.html', artwork=artwork)
            
        target_user_id = None
        if target_username:
            target_user = User.query.filter_by(username=target_username).first()
            if not target_user:
                flash(f'"{target_username}" adlı kullanıcı bulunamadı.', 'error')
                return render_template('add_discount.html', artwork=artwork)
            target_user_id = target_user.id
            
        discount = Discount(
            code=code,
            description=f"{artwork.title} için {'%' + str(discount_value) if discount_type == 'percentage' else str(discount_value) + ' TL'} indirim",
            discount_type=discount_type,
            discount_value=discount_value if discount_type == 'percentage' else discount_value * 100, # TL to cents
            max_uses=1, # Default single use
            artwork_id=artwork.id,
            target_user_id=target_user_id
        )
        db.session.add(discount)
        db.session.commit()
        
        flash('İndirim kuponu başarıyla oluşturuldu!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('add_discount.html', artwork=artwork)

@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)

# Comments and Ratings
@app.route('/add_artwork_comment/<int:artwork_id>', methods=['POST'])
@login_required
def add_artwork_comment(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    
    has_bought = Order.query.filter_by(user_id=current_user.id, artwork_id=artwork_id).first() is not None
    if not has_bought:
        flash('Bu esere yorum yapabilmek için önce satın almış olmalısınız!', 'error')
        return redirect(url_for('artwork_detail', id=artwork_id))
        
    comment_text = request.form.get('comment')
    rating = int(request.form.get('rating', 0))
    
    if not comment_text or rating < 1 or rating > 5:
        flash('Geçersiz yorum veya puan!', 'error')
        return redirect(url_for('artwork_detail', id=artwork_id))
    
    comment = ArtworkComment(
        user_id=current_user.id,
        artwork_id=artwork_id,
        comment=comment_text,
        rating=rating
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Yorumunuz başarıyla eklendi!', 'success')
    return redirect(url_for('artwork_detail', id=artwork_id))

@app.route('/add_event_comment/<int:event_id>', methods=['POST'])
@login_required
def add_event_comment(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Check if user attended the event
    reservation = Reservation.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not reservation:
        flash('Bu etkinlik hakkında yorum yapabilmek için katılmış olmalısınız!', 'error')
        return redirect(url_for('event_detail', id=event_id))
    
    comment_text = request.form.get('comment')
    rating = int(request.form.get('rating', 0))
    
    if not comment_text or rating < 1 or rating > 5:
        flash('Geçersiz yorum veya puan!', 'error')
        return redirect(url_for('event_detail', id=event_id))
    
    comment = EventComment(
        user_id=current_user.id,
        event_id=event_id,
        comment=comment_text,
        rating=rating
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Yorumunuz başarıyla eklendi!', 'success')
    return redirect(url_for('event_detail', id=event_id))

@app.route('/vote_comment/<comment_type>/<int:comment_id>/<vote_type>')
@login_required
def vote_comment(comment_type, comment_id, vote_type):
    if comment_type == 'artwork':
        comment = ArtworkComment.query.get_or_404(comment_id)
    elif comment_type == 'event':
        comment = EventComment.query.get_or_404(comment_id)
    else:
        flash('Geçersiz yorum tipi!', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if vote_type == 'helpful':
        comment.helpful_votes += 1
        db.session.commit()
        flash('Yorum faydalı olarak işaretlendi!', 'success')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/reply_comment/<comment_type>/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(comment_type, comment_id):
    if comment_type == 'artwork':
        comment = ArtworkComment.query.get_or_404(comment_id)
    elif comment_type == 'event':
        comment = EventComment.query.get_or_404(comment_id)
    else:
        flash('Geçersiz yorum tipi!', 'error')
        return redirect(request.referrer or url_for('index'))
    
    reply_text = request.form.get('reply')
    
    if not reply_text:
        flash('Yanıt boş olamaz!', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if current_user.user_type == 'admin' or (comment_type == 'artwork' and current_user.id == comment.artwork.artist_id) or (comment_type == 'event' and current_user.id == comment.event.instructor_id):
        comment.admin_reply = reply_text
        db.session.commit()
        flash('Yanıtınız başarıyla eklendi!', 'success')
    else:
        flash('Bu yoruma yanıt verme yetkiniz yok!', 'error')
    
    return redirect(request.referrer or url_for('index'))

# Customer Support
@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        priority = request.form.get('priority', 'medium')
        
        if not subject or not message:
            flash('Konu ve mesaj alanları zorunludur!', 'error')
            return render_template('support.html')
        
        ticket = SupportTicket(
            user_id=current_user.id,
            subject=subject,
            message=message,
            priority=priority
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash('Destek talebiniz başarıyla oluşturuldu!', 'success')
        return redirect(url_for('my_tickets'))
    
    return render_template('support.html')

@app.route('/my_tickets')
@login_required
def my_tickets():
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return render_template('my_tickets.html', tickets=tickets)

@app.route('/ticket/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    if ticket.user_id != current_user.id and current_user.user_type != 'admin':
        flash('Bu talebi görüntüleme yetkiniz yok!', 'error')
        return redirect(url_for('my_tickets'))
    
    return render_template('ticket_detail.html', ticket=ticket)

@app.route('/add_ticket_response/<int:ticket_id>', methods=['POST'])
@login_required
def add_ticket_response(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    if ticket.user_id != current_user.id and current_user.user_type != 'admin':
        flash('Bu talebe yanıt verme yetkiniz yok!', 'error')
        return redirect(url_for('my_tickets'))
    
    response_text = request.form.get('response')
    
    if not response_text:
        flash('Yanıt boş olamaz!', 'error')
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    response = SupportResponse(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=response_text,
        is_admin_response=(current_user.user_type == 'admin')
    )
    
    db.session.add(response)
    
    # Update ticket status
    if current_user.user_type == 'admin':
        ticket.status = 'in_progress'
    
    db.session.commit()
    
    flash('Yanıtınız başarıyla eklendi!', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))

# Comparison System
@app.route('/compare')
@login_required
def compare():
    comparison = Comparison.query.filter_by(user_id=current_user.id).first()
    
    if not comparison:
        flash('Karşılaştırma listeniz boş!', 'info')
        return redirect(url_for('gallery'))
    
    item_ids = json.loads(comparison.item_ids)
    
    if comparison.comparison_type == 'artwork':
        items = Artwork.query.filter(Artwork.id.in_(item_ids)).all()
    else:
        items = Event.query.filter(Event.id.in_(item_ids)).all()
    
    return render_template('compare.html', items=items, comparison_type=comparison.comparison_type)

@app.route('/add_to_comparison/<item_type>/<int:item_id>')
@login_required
def add_to_comparison(item_type, item_id):
    if item_type not in ['artwork', 'event']:
        flash('Geçersiz ürün tipi!', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Get or create comparison
    comparison = Comparison.query.filter_by(user_id=current_user.id, comparison_type=item_type).first()
    
    if not comparison:
        comparison = Comparison(
            user_id=current_user.id,
            comparison_type=item_type,
            item_ids=json.dumps([item_id])
        )
        db.session.add(comparison)
        flash('Ürün karşılaştırmaya eklendi!', 'success')
    else:
        item_ids = json.loads(comparison.item_ids)
        if item_id not in item_ids:
            item_ids.append(item_id)
            comparison.item_ids = json.dumps(item_ids)
            flash('Ürün karşılaştırmaya eklendi!', 'success')
        else:
            flash('Bu ürün zaten karşılaştırmada!', 'info')
    
    db.session.commit()
    return redirect(request.referrer or url_for('index'))

@app.route('/remove_from_comparison/<item_type>/<int:item_id>')
@login_required
def remove_from_comparison(item_type, item_id):
    comparison = Comparison.query.filter_by(user_id=current_user.id, comparison_type=item_type).first()
    
    if not comparison:
        flash('Karşılaştırma listeniz boş!', 'error')
        return redirect(url_for('compare'))
    
    item_ids = json.loads(comparison.item_ids)
    if item_id in item_ids:
        item_ids.remove(item_id)
        comparison.item_ids = json.dumps(item_ids)
        
        if not item_ids:
            db.session.delete(comparison)
            flash('Karşılaştırma temizlendi!', 'info')
        else:
            db.session.commit()
            flash('Ürün karşılaştırmadan çıkarıldı!', 'info')
    
    return redirect(url_for('compare'))

# Statistics
@app.route('/statistics')
@login_required
def statistics():
    if current_user.user_type != 'admin':
        flash('Bu sayfaya erişim izniniz yok!', 'error')
        return redirect(url_for('index'))
    
    # Artwork statistics
    total_artworks = Artwork.query.count()
    sold_artworks = Artwork.query.filter_by(status='sold').count()
    total_artwork_views = ArtworkView.query.count()
    
    # Event statistics
    total_events = Event.query.count()
    active_events = Event.query.filter_by(status='active').count()
    total_reservations = Reservation.query.count()
    
    # User statistics
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    
    # Favorite statistics
    total_favorites = Favorite.query.count()
    
    stats = {
        'artworks': {
            'total': total_artworks,
            'sold': sold_artworks,
            'views': total_artwork_views
        },
        'events': {
            'total': total_events,
            'active': active_events,
            'reservations': total_reservations
        },
        'users': {
            'total': total_users,
            'orders': total_orders,
            'revenue': total_revenue
        },
        'favorites': {
            'total': total_favorites
        }
    }
    
    return render_template('statistics.html', stats=stats)

@app.route('/admin')
@login_required
def admin():
    if current_user.user_type != 'admin':
        flash('Bu sayfaya erişim izniniz yok!', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    artworks = Artwork.query.all()
    orders = Order.query.all()
    events = Event.query.all()
    reservations = Reservation.query.all()
    tickets = SupportTicket.query.all()
    
    return render_template('admin.html', users=users, artworks=artworks, orders=orders, 
                         events=events, reservations=reservations, tickets=tickets)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
