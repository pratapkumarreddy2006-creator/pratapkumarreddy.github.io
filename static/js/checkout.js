// Order Placement Function
async function placeOrder(customer, cart, payment_method = 'COD') {
    try {
        // Get cart from session if not provided
        if (!cart || Object.keys(cart).length === 0) {
            const cartData = await getCart();
            cart = cartData.cart;
        }

        if (!cart || Object.keys(cart).length === 0) {
            alert('Your cart is empty. Please add items before placing an order.');
            return false;
        }

        const response = await fetch('/api/order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({customer, cart, payment_method})
        });

        const result = await response.json();
        if (result.status === 'success') {
            alert('Order placed successfully! Order ID: ' + result.order_id);
            clearCart();
            return true;
        } else {
            alert('Order failed: ' + (result.message || 'Unknown error'));
            return false;
        }
    } catch (error) {
        console.error('Error placing order:', error);
        alert('Network error placing order. Please try again.');
        return false;
    }
}

// Validate customer data before placing order
function validateCustomerData(customer) {
    const requiredFields = ['full_name', 'phone_number', 'email', 'address', 'city', 'state', 'pincode'];
    
    for (let field of requiredFields) {
        if (!customer[field] || customer[field].trim() === '') {
            alert(`Please fill in: ${field.replace(/_/g, ' ')}`);
            return false;
        }
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(customer.email)) {
        alert('Please enter a valid email address');
        return false;
    }
    
    // Validate phone format (basic check)
    if (!/^\d{10}$/.test(customer.phone_number.replace(/[-\s]/g, ''))) {
        alert('Please enter a valid 10-digit phone number');
        return false;
    }
    
    return true;
}
