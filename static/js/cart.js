// Cart Management Functions
function addToCart(productId, quantity = 1) {
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({product_id: productId, quantity: quantity})
    })
    .then(res => res.json())
    .then(data => {
        if (data && data.status === 'success') {
            alert('Added to cart!');
            updateCartUI(data.total_items);
        } else {
            alert('Could not add to cart: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error adding to cart');
    });
}

function removeFromCart(productId) {
    fetch(`/api/cart/remove/${productId}`, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(res => res.json())
    .then(data => {
        if (data && data.status === 'success') {
            alert('Removed from cart');
            updateCartUI(data.total_items);
        } else {
            alert('Error: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error removing from cart');
    });
}

function getCart() {
    return fetch('/api/cart')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                return data;
            } else {
                throw new Error(data.message);
            }
        })
        .catch(err => {
            console.error('Error fetching cart:', err);
            return {cart: {}, total_items: 0};
        });
}

function clearCart() {
    if (confirm('Are you sure you want to clear your cart?')) {
        fetch('/api/cart/clear', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Cart cleared');
                updateCartUI(0);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(err => {
            console.error(err);
            alert('Error clearing cart');
        });
    }
}

function updateCartUI(totalItems) {
    const cartIcon = document.querySelector('.nav-icons a:nth-child(3)');
    if (cartIcon) {
        if (totalItems > 0) {
            let badge = cartIcon.querySelector('.cart-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'cart-badge';
                cartIcon.appendChild(badge);
            }
            badge.textContent = totalItems;
            badge.style.position = 'absolute';
            badge.style.top = '-5px';
            badge.style.right = '-10px';
            badge.style.backgroundColor = '#e94560';
            badge.style.color = 'white';
            badge.style.borderRadius = '50%';
            badge.style.width = '20px';
            badge.style.height = '20px';
            badge.style.display = 'flex';
            badge.style.alignItems = 'center';
            badge.style.justifyContent = 'center';
            badge.style.fontSize = '0.75rem';
            badge.style.fontWeight = 'bold';
        } else {
            const badge = cartIcon.querySelector('.cart-badge');
            if (badge) badge.remove();
        }
    }
}

// Initialize cart UI on page load
document.addEventListener('DOMContentLoaded', () => {
    getCart().then(data => {
        updateCartUI(data.total_items);
    });
});
