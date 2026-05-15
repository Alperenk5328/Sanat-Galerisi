import re
import os

app_path = r"c:\Users\ertug\OneDrive\Masaüstü\Sanat-Galerisi\database\online_sanat_galerisi\backend\app.py"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update ArtworkComment
content = content.replace(
    "helpful_votes = db.Column(db.Integer, default=0)",
    "helpful_votes = db.Column(db.Integer, default=0)\n    admin_reply = db.Column(db.Text, nullable=True)"
)

# 2. Update artwork_detail sorting & order checking
old_artwork_detail = """@app.route('/artwork/<int:id>')
def artwork_detail(id):
    artwork = Artwork.query.get_or_404(id)
    
    # Track view
    if current_user.is_authenticated:
        view = ArtworkView(artwork_id=id, user_id=current_user.id)
    else:
        view = ArtworkView(artwork_id=id, ip_address=request.remote_addr)
    db.session.add(view)
    db.session.commit()
    
    return render_template('artwork_detail.html', artwork=artwork)"""

new_artwork_detail = """@app.route('/artwork/<int:id>')
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
    
    return render_template('artwork_detail.html', artwork=artwork, comments=comments, sort_by=sort_by, avg_rating=avg_rating, view_count=view_count, favorite_count=favorite_count, has_bought=has_bought)"""

content = content.replace(old_artwork_detail, new_artwork_detail)

# 3. Update event_detail sorting & stats
old_event_detail = """@app.route('/event/<int:id>')
def event_detail(id):
    event = Event.query.get_or_404(id)
    
    # Track view
    if current_user.is_authenticated:
        view = EventView(event_id=id, user_id=current_user.id)
    else:
        view = EventView(event_id=id, ip_address=request.remote_addr)
    db.session.add(view)
    db.session.commit()
    
    return render_template('event_detail.html', event=event)"""

new_event_detail = """@app.route('/event/<int:id>')
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
    
    return render_template('event_detail.html', event=event, comments=comments, sort_by=sort_by, avg_rating=avg_rating, view_count=view_count, occupancy_rate=occupancy_rate, has_attended=has_attended)"""

content = content.replace(old_event_detail, new_event_detail)

# 4. add_artwork_comment verification
old_add_artwork_comment = """@app.route('/add_artwork_comment/<int:artwork_id>', methods=['POST'])
@login_required
def add_artwork_comment(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    
    comment_text = request.form.get('comment')"""

new_add_artwork_comment = """@app.route('/add_artwork_comment/<int:artwork_id>', methods=['POST'])
@login_required
def add_artwork_comment(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    
    has_bought = Order.query.filter_by(user_id=current_user.id, artwork_id=artwork_id).first() is not None
    if not has_bought:
        flash('Bu esere yorum yapabilmek için önce satın almış olmalısınız!', 'error')
        return redirect(url_for('artwork_detail', id=artwork_id))
        
    comment_text = request.form.get('comment')"""

content = content.replace(old_add_artwork_comment, new_add_artwork_comment)

# 5. reply_comment saving to admin_reply
old_reply_comment = """    # Create a support response for admin replies (simplified approach)
    if current_user.user_type == 'admin':
        response = SupportResponse(
            ticket_id=0,  # Using 0 as placeholder for comment replies
            user_id=current_user.id,
            message=f"Yanıt: {reply_text}",
            is_admin_response=True
        )
        db.session.add(response)
        db.session.commit()
        flash('Yanıtınız başarıyla eklendi!', 'success')"""

new_reply_comment = """    if current_user.user_type == 'admin' or (comment_type == 'artwork' and current_user.id == comment.artwork.artist_id) or (comment_type == 'event' and current_user.id == comment.event.instructor_id):
        comment.admin_reply = reply_text
        db.session.commit()
        flash('Yanıtınız başarıyla eklendi!', 'success')
    else:
        flash('Bu yoruma yanıt verme yetkiniz yok!', 'error')"""

content = content.replace(old_reply_comment, new_reply_comment)

# 6. Add Statistics Route
stats_route = """
@app.route('/statistics')
@login_required
def statistics():
    if current_user.user_type != 'admin':
        flash('Yetkisiz erişim!', 'error')
        return redirect(url_for('index'))
        
    total_sales = db.session.query(db.func.sum(Order.total_price)).filter_by(status='completed').scalar() or 0
    total_reservations = db.session.query(db.func.sum(Reservation.total_price)).filter_by(status='confirmed').scalar() or 0
    
    top_artworks = db.session.query(Artwork, db.func.count(ArtworkView.id).label('views'))\\
        .outerjoin(ArtworkView)\\
        .group_by(Artwork.id)\\
        .order_by(db.desc('views')).limit(5).all()
        
    events_stats = db.session.query(Event, db.func.count(Reservation.id).label('reservations'))\\
        .outerjoin(Reservation)\\
        .group_by(Event.id)\\
        .order_by(db.desc('reservations')).limit(5).all()
        
    return render_template('statistics.html', 
                           total_sales=total_sales, 
                           total_reservations=total_reservations,
                           top_artworks=top_artworks,
                           events_stats=events_stats)
"""
if "/statistics" not in content:
    content += stats_route


with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
