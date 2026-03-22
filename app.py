from flask import Flask, request, jsonify, render_template, session
from flask_mysqldb import MySQL
from datetime import datetime
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)

# MySQL configuration (update with your credentials)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
app.config['MYSQL_DB'] = 'clothing_store'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --- API: Save Contact Form Data ---
@app.route('/api/contact', methods=['POST'])
def save_contact():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
        
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()
        
        if not name or not phone or not message:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contact_messages (name, phone, message) VALUES (%s, %s, %s)", (name, phone, message))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Get Products ---
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        cur.close()
        return jsonify(products)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Get Product Details ---
@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cur.fetchone()
        cur.close()
        
        if not product:
            return jsonify({'status': 'error', 'message': 'Product not found'}), 404
        
        return jsonify({'status': 'success', 'product': product}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Add to Cart (Session-based) ---
@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
        
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({'status': 'error', 'message': 'Product ID required'}), 400
        
        quantity = int(data.get('quantity', 1))
        if quantity <= 0:
            return jsonify({'status': 'error', 'message': 'Quantity must be positive'}), 400
        
        if 'cart' not in session:
            session['cart'] = {}
        
        session['cart'][str(product_id)] = session['cart'].get(str(product_id), 0) + quantity
        session.modified = True
        
        return jsonify({'status': 'success', 'cart': session['cart'], 'total_items': sum(session['cart'].values())}), 200
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Get Cart ---
@app.route('/api/cart', methods=['GET'])
def get_cart():
    try:
        cart = session.get('cart', {})
        total_items = sum(cart.values()) if cart else 0
        return jsonify({'status': 'success', 'cart': cart, 'total_items': total_items}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Clear Cart ---
@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    try:
        session.pop('cart', None)
        session.modified = True
        return jsonify({'status': 'success', 'message': 'Cart cleared'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Remove from Cart ---
@app.route('/api/cart/remove/<product_id>', methods=['DELETE', 'POST'])
def remove_from_cart(product_id):
    try:
        if 'cart' not in session:
            return jsonify({'status': 'error', 'message': 'Cart is empty'}), 400
        
        if str(product_id) in session['cart']:
            del session['cart'][str(product_id)]
            session.modified = True
            return jsonify({'status': 'success', 'cart': session['cart'], 'total_items': sum(session['cart'].values())}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Product not in cart'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Place Order ---
@app.route('/api/order', methods=['POST'])
def place_order():
    cur = None
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
        
        customer = data.get('customer')
        cart = data.get('cart') or session.get('cart', {})
        payment_method = data.get('payment_method', 'COD')
        
        # Validate customer data
        if not customer or not isinstance(customer, dict):
            return jsonify({'status': 'error', 'message': 'Customer data required'}), 400
        
        required_fields = ['full_name', 'phone_number', 'email', 'address', 'city', 'state', 'pincode']
        for field in required_fields:
            if field not in customer or not str(customer[field]).strip():
                return jsonify({'status': 'error', 'message': f'Missing or empty field: {field}'}), 400
        
        # Validate cart data
        if not cart:
            return jsonify({'status': 'error', 'message': 'Cart is empty'}), 400
        
        # Convert cart dict to list if needed (from {product_id: qty} to list format)
        cart_items = []
        if isinstance(cart, dict):
            for prod_id, qty in cart.items():
                cart_items.append({'product_id': int(prod_id), 'quantity': int(qty)})
        else:
            cart_items = cart
        
        cur = mysql.connection.cursor()
        
        # Save customer details
        cur.execute("""
            INSERT INTO customers (full_name, phone_number, email, address, city, state, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            customer['full_name'], customer['phone_number'], customer['email'],
            customer['address'], customer['city'], customer['state'], customer['pincode']
        ))
        customer_id = cur.lastrowid
        
        # Calculate total amount
        total_amount = 0
        order_items = []
        for item in cart_items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            if not product_id or quantity <= 0:
                mysql.connection.rollback()
                cur.close()
                return jsonify({'status': 'error', 'message': 'Invalid product or quantity'}), 400
            
            cur.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
            product = cur.fetchone()
            if product:
                price = float(product['price'])
                total_amount += price * quantity
                order_items.append((product_id, quantity, price))
            else:
                mysql.connection.rollback()
                cur.close()
                return jsonify({'status': 'error', 'message': f'Product {product_id} not found'}), 404
        
        # Save order
        cur.execute("""
            INSERT INTO orders (customer_id, total_amount, payment_method, order_status)
            VALUES (%s, %s, %s, %s)
        """, (customer_id, total_amount, payment_method, 'Pending'))
        order_id = cur.lastrowid
        
        # Save order items
        for product_id, quantity, price in order_items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
        
        mysql.connection.commit()
        cur.close()
        session.pop('cart', None)
        return jsonify({'status': 'success', 'order_id': order_id}), 201
    except (ValueError, TypeError):
        if cur:
            mysql.connection.rollback()
            cur.close()
        return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400
    except Exception as e:
        if cur:
            mysql.connection.rollback()
            cur.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- API: Save Customer Details (if needed separately) ---
@app.route('/api/customer', methods=['POST'])
def save_customer():
    cur = None
    try:
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON'}), 400
        
        required_fields = ['full_name', 'phone_number', 'email', 'address', 'city', 'state', 'pincode']
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                return jsonify({'status': 'error', 'message': f'Missing or empty field: {field}'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO customers (full_name, phone_number, email, address, city, state, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['full_name'], data['phone_number'], data['email'],
            data['address'], data['city'], data['state'], data['pincode']
        ))
        mysql.connection.commit()
        customer_id = cur.lastrowid
        cur.close()
        return jsonify({'status': 'success', 'customer_id': customer_id}), 201
    except Exception as e:
        if cur:
            mysql.connection.rollback()
            cur.close()
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Serve HTML pages (optional) ---
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)