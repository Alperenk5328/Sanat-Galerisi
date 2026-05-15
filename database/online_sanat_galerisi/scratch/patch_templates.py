import re
import os

base_path = r"c:\Users\ertug\OneDrive\Masaüstü\Sanat-Galerisi\database\online_sanat_galerisi\frontend\templates"
artwork_detail_path = os.path.join(base_path, "artwork_detail.html")
event_detail_path = os.path.join(base_path, "event_detail.html")
gallery_path = os.path.join(base_path, "gallery.html")
events_path = os.path.join(base_path, "events.html")
base_html_path = os.path.join(base_path, "base.html")

# 1. Patch artwork_detail.html
with open(artwork_detail_path, "r", encoding="utf-8") as f:
    aw_content = f.read()

compare_btn_aw = """
                        <a href="{{ url_for('add_to_comparison', item_type='artwork', item_id=artwork.id) }}" 
                           class="btn btn-outline-secondary mt-2">
                            <i class="fas fa-balance-scale"></i> Karşılaştır
                        </a>
"""
# insert compare btn inside btn-group
aw_content = aw_content.replace(
    """<i class="fas fa-shopping-cart"></i> Sepete Ekle
                        </a>""",
    """<i class="fas fa-shopping-cart"></i> Sepete Ekle
                        </a>""" + compare_btn_aw
)

# insert stats below <small class="text-muted">
stats_aw = """
                <hr>
                <div class="row text-center mb-3">
                    <div class="col"><i class="fas fa-eye"></i> {{ view_count }} Görüntülenme</div>
                    <div class="col"><i class="fas fa-heart text-danger"></i> {{ favorite_count }} Favori</div>
                    <div class="col"><i class="fas fa-star text-warning"></i> {{ "%.1f"|format(avg_rating) }}/5</div>
                </div>
"""
aw_content = aw_content.replace("""<div class="mt-3">
                    {% if current_user.is_authenticated %}""", stats_aw + """<div class="mt-3">
                    {% if current_user.is_authenticated %}""")

# Replace the placeholder similar artworks with Comments section
comments_aw = """
<!-- Değerlendirme ve Yorumlar -->
<div class="row mt-5">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Yorumlar ve Değerlendirmeler</h3>
            <div>
                <form action="{{ url_for('artwork_detail', id=artwork.id) }}" method="GET" class="d-inline">
                    <select name="sort" class="form-select form-select-sm" onchange="this.form.submit()">
                        <option value="newest" {% if sort_by == 'newest' %}selected{% endif %}>En Yeni</option>
                        <option value="highest" {% if sort_by == 'highest' %}selected{% endif %}>En Yüksek Puan</option>
                        <option value="helpful" {% if sort_by == 'helpful' %}selected{% endif %}>En Faydalı</option>
                    </select>
                </form>
            </div>
        </div>
        
        {% if current_user.is_authenticated %}
            {% if has_bought %}
                <div class="card mb-4">
                    <div class="card-body">
                        <form action="{{ url_for('add_artwork_comment', artwork_id=artwork.id) }}" method="POST">
                            <div class="mb-3">
                                <label class="form-label">Değerlendirmeniz (1-5 Yıldız)</label>
                                <select class="form-select w-25" name="rating" required>
                                    <option value="5">⭐⭐⭐⭐⭐ (5) Mükemmel</option>
                                    <option value="4">⭐⭐⭐⭐ (4) Çok İyi</option>
                                    <option value="3">⭐⭐⭐ (3) Ortalama</option>
                                    <option value="2">⭐⭐ (2) Kötü</option>
                                    <option value="1">⭐ (1) Çok Kötü</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Yorumunuz</label>
                                <textarea class="form-control" name="comment" rows="3" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Yorum Gönder</button>
                        </form>
                    </div>
                </div>
            {% else %}
                <div class="alert alert-info">Bu esere yorum yapabilmek için önce satın almalısınız. Sadece doğrulanmış alıcılar yorum yapabilir.</div>
            {% endif %}
        {% else %}
            <div class="alert alert-warning"><a href="{{ url_for('login') }}">Giriş yaparak</a> yorum yapabilirsiniz.</div>
        {% endif %}

        <div class="comments-list">
            {% for comment in comments %}
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h6 class="mb-0">{{ comment.user.username }} 
                                {% if comment.user_id in [order.user_id for order in artwork.orders if order.status=='completed'] %}
                                    <span class="badge bg-success ms-1" style="font-size: 0.6em;">Doğrulanmış Alıcı <i class="fas fa-check-circle"></i></span>
                                {% endif %}
                            </h6>
                            <div class="text-warning small mb-2">
                                {% for i in range(comment.rating) %}<i class="fas fa-star"></i>{% endfor %}
                            </div>
                        </div>
                        <small class="text-muted">{{ comment.created_at.strftime('%d.%m.%Y') }}</small>
                    </div>
                    <p class="mb-2">{{ comment.comment }}</p>
                    
                    <div class="d-flex align-items-center">
                        {% if current_user.is_authenticated and current_user.id != comment.user_id %}
                        <a href="{{ url_for('vote_comment', comment_type='artwork', comment_id=comment.id, vote_type='helpful') }}" class="btn btn-sm btn-outline-success py-0 px-2 me-2">
                            <i class="fas fa-thumbs-up"></i> Faydalı ({{ comment.helpful_votes }})
                        </a>
                        {% else %}
                        <span class="text-muted small me-2"><i class="fas fa-thumbs-up"></i> {{ comment.helpful_votes }} kişi faydalı buldu</span>
                        {% endif %}
                    </div>
                    
                    {% if comment.admin_reply %}
                    <div class="mt-3 ms-4 p-3 bg-light rounded border-start border-primary border-3">
                        <strong class="text-primary">Sanatçı/Yönetici Yanıtı:</strong>
                        <p class="mb-0 mt-1">{{ comment.admin_reply }}</p>
                    </div>
                    {% elif current_user.is_authenticated and (current_user.user_type == 'admin' or current_user.id == artwork.artist_id) %}
                    <div class="mt-3">
                        <button class="btn btn-sm btn-link p-0" onclick="document.getElementById('reply-form-aw-{{comment.id}}').classList.toggle('d-none')">Yanıtla</button>
                        <form id="reply-form-aw-{{comment.id}}" class="d-none mt-2" action="{{ url_for('reply_comment', comment_type='artwork', comment_id=comment.id) }}" method="POST">
                            <div class="input-group input-group-sm">
                                <input type="text" class="form-control" name="reply" placeholder="Yanıtınızı yazın..." required>
                                <button class="btn btn-primary" type="submit">Gönder</button>
                            </div>
                        </form>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <p class="text-muted">Henüz yorum yapılmamış.</p>
            {% endfor %}
        </div>
    </div>
</div>
"""
aw_content = re.sub(r'<!-- Benzer Eserler -->.*', comments_aw + "{% endblock %}", aw_content, flags=re.DOTALL)

with open(artwork_detail_path, "w", encoding="utf-8") as f:
    f.write(aw_content)

# 2. Patch event_detail.html
with open(event_detail_path, "r", encoding="utf-8") as f:
    ev_content = f.read()

compare_btn_ev = """
                        <a href="{{ url_for('add_to_comparison', item_type='event', item_id=event.id) }}" 
                           class="btn btn-outline-secondary mt-2">
                            <i class="fas fa-balance-scale"></i> Karşılaştır
                        </a>
"""
# insert compare btn inside btn-group
ev_content = ev_content.replace(
    """<button type="submit" class="btn btn-primary">
                                        <i class="fas fa-ticket-alt"></i> Rezervasyon Yap
                                    </button>""",
    """<button type="submit" class="btn btn-primary">
                                        <i class="fas fa-ticket-alt"></i> Rezervasyon Yap
                                    </button>""" + compare_btn_ev
)

# insert stats
stats_ev = """
                <hr>
                <div class="row text-center mb-3">
                    <div class="col"><i class="fas fa-eye"></i> {{ view_count }} Görüntülenme</div>
                    <div class="col" title="Doluluk Oranı"><i class="fas fa-chart-pie"></i> %{{ "%.0f"|format(occupancy_rate) }} Dolu</div>
                    <div class="col"><i class="fas fa-star text-warning"></i> {{ "%.1f"|format(avg_rating) }}/5</div>
                </div>
"""
ev_content = ev_content.replace("""<div class="mt-3">
                    {% if current_user.is_authenticated %}""", stats_ev + """<div class="mt-3">
                    {% if current_user.is_authenticated %}""")

# Replace similar events with comments
comments_ev = """
<!-- Değerlendirme ve Yorumlar -->
<div class="row mt-5">
    <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Yorumlar ve Değerlendirmeler</h3>
            <div>
                <form action="{{ url_for('event_detail', id=event.id) }}" method="GET" class="d-inline">
                    <select name="sort" class="form-select form-select-sm" onchange="this.form.submit()">
                        <option value="newest" {% if sort_by == 'newest' %}selected{% endif %}>En Yeni</option>
                        <option value="highest" {% if sort_by == 'highest' %}selected{% endif %}>En Yüksek Puan</option>
                        <option value="helpful" {% if sort_by == 'helpful' %}selected{% endif %}>En Faydalı</option>
                    </select>
                </form>
            </div>
        </div>
        
        {% if current_user.is_authenticated %}
            {% if has_attended %}
                <div class="card mb-4">
                    <div class="card-body">
                        <form action="{{ url_for('add_event_comment', event_id=event.id) }}" method="POST">
                            <div class="mb-3">
                                <label class="form-label">Değerlendirmeniz (1-5 Yıldız)</label>
                                <select class="form-select w-25" name="rating" required>
                                    <option value="5">⭐⭐⭐⭐⭐ (5) Mükemmel</option>
                                    <option value="4">⭐⭐⭐⭐ (4) Çok İyi</option>
                                    <option value="3">⭐⭐⭐ (3) Ortalama</option>
                                    <option value="2">⭐⭐ (2) Kötü</option>
                                    <option value="1">⭐ (1) Çok Kötü</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Yorumunuz</label>
                                <textarea class="form-control" name="comment" rows="3" required></textarea>
                            </div>
                            <button type="submit" class="btn btn-primary">Yorum Gönder</button>
                        </form>
                    </div>
                </div>
            {% else %}
                <div class="alert alert-info">Bu etkinliğe yorum yapabilmek için önce katılmış (rezervasyon yapmış) olmalısınız.</div>
            {% endif %}
        {% else %}
            <div class="alert alert-warning"><a href="{{ url_for('login') }}">Giriş yaparak</a> yorum yapabilirsiniz.</div>
        {% endif %}

        <div class="comments-list">
            {% for comment in comments %}
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h6 class="mb-0">{{ comment.user.username }} 
                                <span class="badge bg-success ms-1" style="font-size: 0.6em;">Katılımcı <i class="fas fa-check-circle"></i></span>
                            </h6>
                            <div class="text-warning small mb-2">
                                {% for i in range(comment.rating) %}<i class="fas fa-star"></i>{% endfor %}
                            </div>
                        </div>
                        <small class="text-muted">{{ comment.created_at.strftime('%d.%m.%Y') }}</small>
                    </div>
                    <p class="mb-2">{{ comment.comment }}</p>
                    
                    <div class="d-flex align-items-center">
                        {% if current_user.is_authenticated and current_user.id != comment.user_id %}
                        <a href="{{ url_for('vote_comment', comment_type='event', comment_id=comment.id, vote_type='helpful') }}" class="btn btn-sm btn-outline-success py-0 px-2 me-2">
                            <i class="fas fa-thumbs-up"></i> Faydalı ({{ comment.helpful_votes }})
                        </a>
                        {% else %}
                        <span class="text-muted small me-2"><i class="fas fa-thumbs-up"></i> {{ comment.helpful_votes }} kişi faydalı buldu</span>
                        {% endif %}
                    </div>
                    
                    {% if comment.admin_reply %}
                    <div class="mt-3 ms-4 p-3 bg-light rounded border-start border-info border-3">
                        <strong class="text-info">Eğitmen/Yönetici Yanıtı:</strong>
                        <p class="mb-0 mt-1">{{ comment.admin_reply }}</p>
                    </div>
                    {% elif current_user.is_authenticated and (current_user.user_type == 'admin' or current_user.id == event.instructor_id) %}
                    <div class="mt-3">
                        <button class="btn btn-sm btn-link p-0" onclick="document.getElementById('reply-form-ev-{{comment.id}}').classList.toggle('d-none')">Yanıtla</button>
                        <form id="reply-form-ev-{{comment.id}}" class="d-none mt-2" action="{{ url_for('reply_comment', comment_type='event', comment_id=comment.id) }}" method="POST">
                            <div class="input-group input-group-sm">
                                <input type="text" class="form-control" name="reply" placeholder="Yanıtınızı yazın..." required>
                                <button class="btn btn-primary" type="submit">Gönder</button>
                            </div>
                        </form>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <p class="text-muted">Henüz yorum yapılmamış.</p>
            {% endfor %}
        </div>
    </div>
</div>
"""
# Assuming event_detail ends similarly. I will append or replace.
if "<!-- Benzer Etkinlikler -->" in ev_content:
    ev_content = re.sub(r'<!-- Benzer Etkinlikler -->.*', comments_ev + "{% endblock %}", ev_content, flags=re.DOTALL)
else:
    ev_content = ev_content.replace("{% endblock %}", comments_ev + "\n{% endblock %}")

with open(event_detail_path, "w", encoding="utf-8") as f:
    f.write(ev_content)

# 3. Add compare button to gallery.html
with open(gallery_path, "r", encoding="utf-8") as f:
    gal_content = f.read()

gal_btn = """
                                    <a href="{{ url_for('add_to_comparison', item_type='artwork', item_id=artwork.id) }}" class="btn btn-sm btn-outline-secondary" title="Karşılaştır"><i class="fas fa-balance-scale"></i></a>
"""
gal_content = gal_content.replace("""<a href="{{ url_for('artwork_detail', id=artwork.id) }}" class="btn btn-sm btn-outline-primary">Gör</a>""", """<a href="{{ url_for('artwork_detail', id=artwork.id) }}" class="btn btn-sm btn-outline-primary">Gör</a>""" + gal_btn)

with open(gallery_path, "w", encoding="utf-8") as f:
    f.write(gal_content)

# 4. Add compare button to events.html
with open(events_path, "r", encoding="utf-8") as f:
    eve_content = f.read()

eve_btn = """
                                    <a href="{{ url_for('add_to_comparison', item_type='event', item_id=event.id) }}" class="btn btn-sm btn-outline-secondary" title="Karşılaştır"><i class="fas fa-balance-scale"></i></a>
"""
eve_content = eve_content.replace("""<a href="{{ url_for('event_detail', id=event.id) }}" class="btn btn-sm btn-outline-primary">Detaylar</a>""", """<a href="{{ url_for('event_detail', id=event.id) }}" class="btn btn-sm btn-outline-primary">Detaylar</a>""" + eve_btn)

with open(events_path, "w", encoding="utf-8") as f:
    f.write(eve_content)

# 5. Base.html menu update
with open(base_html_path, "r", encoding="utf-8") as f:
    base_content = f.read()

support_menu = """
                                <li><a class="dropdown-item" href="{{ url_for('my_tickets') }}">Destek Talepleri</a></li>
"""
base_content = base_content.replace("""<li><a class="dropdown-item" href="{{ url_for('my_reservations') }}">Rezervasyonlar</a></li>""", """<li><a class="dropdown-item" href="{{ url_for('my_reservations') }}">Rezervasyonlar</a></li>""" + support_menu)

nav_compare = """
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('compare') }}">Karşılaştırma</a>
                    </li>
"""
base_content = base_content.replace("""<a class="nav-link" href="{{ url_for('events') }}">Etkinlikler</a>
                    </li>""", """<a class="nav-link" href="{{ url_for('events') }}">Etkinlikler</a>
                    </li>""" + nav_compare)

with open(base_html_path, "w", encoding="utf-8") as f:
    f.write(base_content)

print("Patch for templates applied.")
