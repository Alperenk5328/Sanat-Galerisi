// Main JavaScript file for Online Sanat Galerisi

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Image preview on upload
    var imageUpload = document.getElementById('image-upload');
    if (imageUpload) {
        imageUpload.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    var preview = document.getElementById('image-preview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Search functionality
    var searchInput = document.getElementById('search');
    var searchTimeout;
    
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            var query = e.target.value;
            
            if (query.length > 2) {
                searchTimeout = setTimeout(function() {
                    performSearch(query);
                }, 500);
            }
        });
    }

    // Add to favorites functionality
    var favoriteButtons = document.querySelectorAll('.btn-favorite');
    favoriteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleFavorite(this);
        });
    });

    // Lazy loading for images
    lazyLoadImages();

    // Smooth scroll for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Search function
function performSearch(query) {
    fetch('/api/search?q=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            updateSearchResults(data);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

// Update search results
function updateSearchResults(results) {
    var resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = '';
        
        if (results.length === 0) {
            resultsContainer.innerHTML = '<p class="text-muted">Sonuç bulunamadı.</p>';
            return;
        }
        
        results.forEach(function(result) {
            var resultElement = createSearchResultElement(result);
            resultsContainer.appendChild(resultElement);
        });
    }
}

// Create search result element
function createSearchResultElement(result) {
    var div = document.createElement('div');
    div.className = 'col-md-4 mb-3';
    
    div.innerHTML = `
        <div class="card">
            <img src="${result.image_url}" class="card-img-top" alt="${result.title}">
            <div class="card-body">
                <h6 class="card-title">${result.title}</h6>
                <p class="card-text">${result.description.substring(0, 100)}...</p>
                <a href="/artwork/${result.id}" class="btn btn-primary btn-sm">Detaylar</a>
            </div>
        </div>
    `;
    
    return div;
}

// Toggle favorite
function toggleFavorite(button) {
    var artworkId = button.dataset.artworkId;
    var isFavorited = button.classList.contains('favorited');
    
    fetch('/api/favorites/' + artworkId, {
        method: isFavorited ? 'DELETE' : 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.classList.toggle('favorited');
            button.innerHTML = isFavorited ? 
                '<i class="fas fa-heart"></i> Favorilere Ekle' : 
                '<i class="fas fa-heart text-danger"></i> Favorilerden Çıkar';
        }
    })
    .catch(error => {
        console.error('Favorite toggle error:', error);
    });
}

// Get CSRF token
function getCsrfToken() {
    var token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Lazy loading images
function lazyLoadImages() {
    var images = document.querySelectorAll('img[data-src]');
    
    var imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(function(img) {
        imageObserver.observe(img);
    });
}

// Form validation
function validateForm(formElement) {
    var inputs = formElement.querySelectorAll('input[required], textarea[required], select[required]');
    var isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Show loading spinner
function showLoadingSpinner(container) {
    var spinner = document.createElement('div');
    spinner.className = 'spinner';
    container.appendChild(spinner);
}

// Hide loading spinner
function hideLoadingSpinner(container) {
    var spinner = container.querySelector('.spinner');
    if (spinner) {
        spinner.remove();
    }
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(price);
}

// Format date
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString('tr-TR');
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.performSearch = performSearch;
window.toggleFavorite = toggleFavorite;
window.validateForm = validateForm;
window.showLoadingSpinner = showLoadingSpinner;
window.hideLoadingSpinner = hideLoadingSpinner;
window.formatPrice = formatPrice;
window.formatDate = formatDate;
window.debounce = debounce;
