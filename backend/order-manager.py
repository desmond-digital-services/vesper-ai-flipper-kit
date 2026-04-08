"""
Vesper AI Flipper Kit - Order Management System
Flask REST API with SQLite backend
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from functools import wraps

app = Flask(__name__)
app.config['DATABASE'] = '../database/vesper_orders.db'

# ============================================
# DATABASE HELPERS
# ============================================

def get_db():
    """Get database connection for current request context"""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Close database connection at end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with schema"""
    with app.app_context():
        db = get_db()
        with open('../database/schema.sql', 'r') as f:
            db.executescript(f.read())
        print("Database initialized successfully")

# ============================================
# DECORATORS
# ============================================

def json_required(f):
    """Ensure request has JSON content"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated

def sanitize_string(s, max_length=500):
    """Sanitize string input"""
    if s is None:
        return None
    s = str(s).strip()[:max_length]
    return s if s else None

# ============================================
# UTILITY FUNCTIONS
# ============================================

def generate_order_id():
    """Generate unique order ID: VPR-YYYY-NNNNN"""
    year = datetime.now().year
    db = get_db()
    cursor = db.execute(
        "SELECT COUNT(*) as count FROM orders WHERE order_id LIKE ?",
        (f'VPR-{year}-%',)
    )
    count = cursor.fetchone()['count'] + 1
    return f"VPR-{year}-{count:05d}"

def row_to_dict(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    result = dict(row)
    # Parse shipping_address JSON if present
    if 'shipping_address' in result and result['shipping_address']:
        try:
            result['shipping_address'] = json.loads(result['shipping_address'])
        except json.JSONDecodeError:
            pass
    return result

def rows_to_list(rows):
    """Convert list of sqlite3.Row to list of dicts"""
    return [row_to_dict(row) for row in rows]

# ============================================
# ORDER ENDPOINTS
# ============================================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """
    Get all orders with optional filtering
    Query params: status, payment_status, search, sort, limit, offset
    """
    db = get_db()
    
    # Build query
    query = "SELECT * FROM orders WHERE 1=1"
    params = []
    
    # Filter by order status
    status = request.args.get('status')
    if status:
        query += " AND order_status = ?"
        params.append(status)
    
    # Filter by payment status
    payment_status = request.args.get('payment_status')
    if payment_status:
        query += " AND payment_status = ?"
        params.append(payment_status)
    
    # Search by order_id or email
    search = request.args.get('search')
    if search:
        query += " AND (order_id LIKE ? OR customer_email LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    # Sort order (default: newest first)
    sort = request.args.get('sort', 'date_desc')
    if sort == 'date_asc':
        query += " ORDER BY order_date ASC"
    elif sort == 'date_desc':
        query += " ORDER BY order_date DESC"
    elif sort == 'status':
        query += " ORDER BY order_status"
    elif sort == 'total':
        query += " ORDER BY order_total DESC"
    else:
        query += " ORDER BY order_date DESC"
    
    # Pagination
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    query += f" LIMIT {limit} OFFSET {offset}"
    
    cursor = db.execute(query, params)
    orders = rows_to_list(cursor.fetchall())
    
    # Get total count for pagination
    count_query = "SELECT COUNT(*) as total FROM orders WHERE 1=1" + (
        f" AND order_status = '{status}'" if status else ""
    ) + (
        f" AND payment_status = '{payment_status}'" if payment_status else ""
    ) + (
        f" AND (order_id LIKE '%{search}%' OR customer_email LIKE '%{search}%')" if search else ""
    )
    total_cursor = db.execute(count_query)
    total = total_cursor.fetchone()['total']
    
    return jsonify({
        'orders': orders,
        'total': total,
        'limit': limit,
        'offset': offset
    })

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get single order by ID with all details"""
    db = get_db()
    
    cursor = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = row_to_dict(cursor.fetchone())
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Get email log
    email_cursor = db.execute(
        "SELECT * FROM email_log WHERE order_id = ? ORDER BY sent_date DESC",
        (order_id,)
    )
    order['emails'] = rows_to_list(email_cursor.fetchall())
    
    # Get hardware procurement
    proc_cursor = db.execute(
        "SELECT * FROM hardware_procurement WHERE order_id = ? ORDER BY order_date",
        (order_id,)
    )
    order['procurement'] = rows_to_list(proc_cursor.fetchall())
    
    # Get notes
    notes_cursor = db.execute(
        "SELECT * FROM order_notes WHERE order_id = ? ORDER BY created_at DESC",
        (order_id,)
    )
    order['notes_history'] = rows_to_list(notes_cursor.fetchall())
    
    return jsonify(order)

@app.route('/api/orders', methods=['POST'])
@json_required
def create_order():
    """Create new order (usually from Stripe webhook)"""
    data = request.json
    
    # Generate order ID
    order_id = generate_order_id()
    
    # Parse shipping address
    shipping_address = data.get('shipping_address', {})
    if isinstance(shipping_address, dict):
        shipping_address = json.dumps(shipping_address)
    
    db = get_db()
    try:
        db.execute('''
            INSERT INTO orders (
                order_id, customer_name, customer_email, customer_phone,
                shipping_address, order_date, order_total, payment_status,
                stripe_payment_intent_id, order_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id,
            sanitize_string(data.get('customer_name')),
            sanitize_string(data.get('customer_email')),
            sanitize_string(data.get('customer_phone')),
            shipping_address,
            data.get('order_date', datetime.utcnow().isoformat() + 'Z'),
            data.get('order_total', 499.00),
            data.get('payment_status', 'pending'),
            sanitize_string(data.get('stripe_payment_intent_id')),
            data.get('order_status', 'pending')
        ))
        db.commit()
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'order': row_to_dict(db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone())
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/<order_id>', methods=['PUT'])
@json_required
def update_order(order_id):
    """Update order details"""
    data = request.json
    db = get_db()
    
    # Check if order exists
    cursor = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'Order not found'}), 404
    
    # Build update query
    allowed_fields = [
        'customer_name', 'customer_email', 'customer_phone',
        'shipping_address', 'order_total', 'payment_status',
        'stripe_payment_intent_id', 'order_status', 'build_start_date',
        'ship_date', 'tracking_number', 'carrier', 'estimated_delivery_date',
        'actual_delivery_date', 'notes'
    ]
    
    updates = []
    params = []
    for field in allowed_fields:
        if field in data:
            value = data[field]
            if field == 'shipping_address' and isinstance(value, dict):
                value = json.dumps(value)
            updates.append(f"{field} = ?")
            params.append(value)
    
    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    params.append(order_id)
    query = f"UPDATE orders SET {', '.join(updates)} WHERE order_id = ?"
    
    try:
        db.execute(query, params)
        db.commit()
        
        return jsonify({
            'success': True,
            'order': row_to_dict(db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone())
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
@json_required
def update_order_status(order_id):
    """Update order status with validation"""
    data = request.json
    new_status = data.get('order_status')
    
    valid_statuses = ['pending', 'building', 'testing', 'shipped', 'delivered']
    if new_status not in valid_statuses:
        return jsonify({
            'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
        }), 400
    
    db = get_db()
    
    # Get current status for logging
    cursor = db.execute("SELECT order_status FROM orders WHERE order_id = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'error': 'Order not found'}), 404
    
    old_status = row['order_status']
    
    try:
        # Update status
        db.execute("UPDATE orders SET order_status = ? WHERE order_id = ?", (new_status, order_id))
        
        # Log status change in notes
        db.execute('''
            INSERT INTO order_notes (order_id, note, note_type)
            VALUES (?, ?, 'system')
        ''', (order_id, f'Status changed from {old_status} to {new_status}'))
        
        # Auto-set dates based on status
        if new_status == 'building' and not db.execute(
            "SELECT build_start_date FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()['build_start_date']:
            db.execute("UPDATE orders SET build_start_date = ? WHERE order_id = ?",
                      (datetime.utcnow().isoformat() + 'Z', order_id))
        
        if new_status == 'shipped' and not db.execute(
            "SELECT ship_date FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()['ship_date']:
            db.execute("UPDATE orders SET ship_date = ? WHERE order_id = ?",
                      (datetime.utcnow().isoformat() + 'Z', order_id))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'old_status': old_status,
            'new_status': new_status
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/<order_id>/tracking', methods=['POST'])
@json_required
def add_tracking(order_id):
    """Add tracking number to order"""
    data = request.json
    tracking_number = sanitize_string(data.get('tracking_number'))
    carrier = sanitize_string(data.get('carrier', 'USPS'))
    
    if not tracking_number:
        return jsonify({'error': 'Tracking number required'}), 400
    
    db = get_db()
    
    try:
        db.execute('''
            UPDATE orders 
            SET tracking_number = ?, carrier = ?, 
                ship_date = COALESCE(ship_date, ?),
                order_status = CASE WHEN order_status = 'testing' THEN 'shipped' ELSE order_status END
            WHERE order_id = ?
        ''', (tracking_number, carrier, datetime.utcnow().isoformat() + 'Z', order_id))
        
        db.execute('''
            INSERT INTO order_notes (order_id, note, note_type)
            VALUES (?, ?, 'system')
        ''', (order_id, f'Tracking added: {carrier} {tracking_number}'))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'tracking_number': tracking_number,
            'carrier': carrier
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/orders/<order_id>/notes', methods=['POST'])
@json_required
def add_note(order_id):
    """Add note to order"""
    data = request.json
    note = sanitize_string(data.get('note'), max_length=2000)
    
    if not note:
        return jsonify({'error': 'Note content required'}), 400
    
    db = get_db()
    
    try:
        db.execute('''
            INSERT INTO order_notes (order_id, note, note_type)
            VALUES (?, ?, ?)
        ''', (order_id, note, data.get('note_type', 'manual')))
        db.commit()
        
        return jsonify({
            'success': True,
            'note_id': db.execute("SELECT last_insert_rowid() as id").fetchone()['id']
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

# ============================================
# EMAIL LOG ENDPOINTS
# ============================================

@app.route('/api/orders/<order_id>/emails', methods=['GET'])
def get_order_emails(order_id):
    """Get email log for an order"""
    db = get_db()
    cursor = db.execute(
        "SELECT * FROM email_log WHERE order_id = ? ORDER BY sent_date DESC",
        (order_id,)
    )
    return jsonify(rows_to_list(cursor.fetchall()))

@app.route('/api/emails', methods=['POST'])
@json_required
def log_email():
    """Log an email that was sent"""
    data = request.json
    
    db = get_db()
    try:
        db.execute('''
            INSERT INTO email_log (order_id, email_type, subject, sent_date, status, error_message, recipient_email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('order_id'),
            data.get('email_type'),
            data.get('subject'),
            data.get('sent_date', datetime.utcnow().isoformat() + 'Z'),
            data.get('status', 'sent'),
            data.get('error_message'),
            data.get('recipient_email')
        ))
        db.commit()
        
        return jsonify({
            'success': True,
            'log_id': db.execute("SELECT last_insert_rowid() as id").fetchone()['id']
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

# ============================================
# HARDWARE PROCUREMENT ENDPOINTS
# ============================================

@app.route('/api/orders/<order_id>/procurement', methods=['GET'])
def get_order_procurement(order_id):
    """Get hardware procurement for an order"""
    db = get_db()
    cursor = db.execute(
        "SELECT * FROM hardware_procurement WHERE order_id = ? ORDER BY order_date",
        (order_id,)
    )
    return jsonify(rows_to_list(cursor.fetchall()))

@app.route('/api/procurement', methods=['POST'])
@json_required
def add_procurement():
    """Add hardware procurement record"""
    data = request.json
    
    db = get_db()
    try:
        db.execute('''
            INSERT INTO hardware_procurement (order_id, supplier, item, quantity, cost, order_date, tracking_number, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('order_id'),
            data.get('supplier'),
            data.get('item'),
            data.get('quantity', 1),
            data.get('cost', 0),
            data.get('order_date', datetime.utcnow().isoformat() + 'Z'),
            data.get('tracking_number'),
            data.get('status', 'ordered')
        ))
        db.commit()
        
        return jsonify({
            'success': True,
            'procurement_id': db.execute("SELECT last_insert_rowid() as id").fetchone()['id']
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/procurement/<int:procurement_id>', methods=['PUT'])
@json_required
def update_procurement(procurement_id):
    """Update procurement status"""
    data = request.json
    
    db = get_db()
    allowed_fields = ['supplier', 'item', 'quantity', 'cost', 'tracking_number', 'status', 'notes']
    updates = []
    params = []
    
    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            params.append(data[field])
    
    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    params.append(procurement_id)
    query = f"UPDATE hardware_procurement SET {', '.join(updates)} WHERE procurement_id = ?"
    
    try:
        db.execute(query, params)
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 400

# ============================================
# REPORT ENDPOINTS
# ============================================

@app.route('/api/reports/sales', methods=['GET'])
def sales_report():
    """Get sales report by period"""
    period = request.args.get('period', 'day')  # day, week, month
    
    db = get_db()
    
    if period == 'day':
        query = '''
            SELECT 
                DATE(order_date) as date,
                COUNT(*) as order_count,
                SUM(order_total) as revenue,
                SUM(CASE WHEN payment_status = 'paid' THEN order_total ELSE 0 END) as collected
            FROM orders
            WHERE order_date >= DATE('now', '-30 days')
            GROUP BY DATE(order_date)
            ORDER BY date DESC
        '''
    elif period == 'week':
        query = '''
            SELECT 
                strftime('%Y-W%W', order_date) as week,
                COUNT(*) as order_count,
                SUM(order_total) as revenue,
                SUM(CASE WHEN payment_status = 'paid' THEN order_total ELSE 0 END) as collected
            FROM orders
            WHERE order_date >= DATE('now', '-90 days')
            GROUP BY week
            ORDER BY week DESC
        '''
    else:  # month
        query = '''
            SELECT 
                strftime('%Y-%m', order_date) as month,
                COUNT(*) as order_count,
                SUM(order_total) as revenue,
                SUM(CASE WHEN payment_status = 'paid' THEN order_total ELSE 0 END) as collected
            FROM orders
            WHERE order_date >= DATE('now', '-365 days')
            GROUP BY month
            ORDER BY month DESC
        '''
    
    cursor = db.execute(query)
    return jsonify({
        'period': period,
        'data': rows_to_list(cursor.fetchall())
    })

@app.route('/api/reports/revenue', methods=['GET'])
def revenue_report():
    """Get revenue metrics"""
    db = get_db()
    
    # Total revenue
    total = db.execute("SELECT SUM(order_total) as total FROM orders").fetchone()['total'] or 0
    collected = db.execute(
        "SELECT SUM(order_total) as collected FROM orders WHERE payment_status = 'paid'"
    ).fetchone()['collected'] or 0
    pending = db.execute(
        "SELECT SUM(order_total) as pending FROM orders WHERE payment_status = 'pending'"
    ).fetchone()['pending'] or 0
    
    # Revenue by status
    by_status = db.execute('''
        SELECT order_status, COUNT(*) as count, SUM(order_total) as revenue
        FROM orders GROUP BY order_status
    ''').fetchall()
    
    # Monthly comparison
    this_month = db.execute('''
        SELECT SUM(order_total) as revenue FROM orders
        WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')
    ''').fetchone()['revenue'] or 0
    
    last_month = db.execute('''
        SELECT SUM(order_total) as revenue FROM orders
        WHERE strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now', '-1 month')
    ''').fetchone()['revenue'] or 0
    
    return jsonify({
        'total_revenue': total,
        'collected_revenue': collected,
        'pending_revenue': pending,
        'this_month': this_month,
        'last_month': last_month,
        'month_over_month_change': ((this_month - last_month) / last_month * 100) if last_month > 0 else 0,
        'by_status': rows_to_list(by_status)
    })

@app.route('/api/reports/build-times', methods=['GET'])
def build_time_report():
    """Get build time analytics"""
    db = get_db()
    
    # Average build time (pending -> building -> testing -> shipped)
    cursor = db.execute('''
        SELECT 
            AVG(julianday(ship_date) - julianday(build_start_date)) as avg_build_days
        FROM orders
        WHERE build_start_date IS NOT NULL AND ship_date IS NOT NULL
    ''')
    avg_build_days = cursor.fetchone()['avg_build_days']
    
    # Build time by month
    by_month = db.execute('''
        SELECT 
            strftime('%Y-%m', build_start_date) as month,
            COUNT(*) as orders,
            AVG(julianday(ship_date) - julianday(build_start_date)) as avg_days
        FROM orders
        WHERE build_start_date IS NOT NULL AND ship_date IS NOT NULL
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    ''').fetchall()
    
    # Status distribution
    status_dist = db.execute('''
        SELECT order_status, COUNT(*) as count
        FROM orders GROUP BY order_status
    ''').fetchall()
    
    return jsonify({
        'average_build_days': round(avg_build_days, 1) if avg_build_days else 0,
        'by_month': rows_to_list(by_month),
        'status_distribution': rows_to_list(status_dist)
    })

@app.route('/api/reports/shipping', methods=['GET'])
def shipping_report():
    """Get shipping/carrier performance"""
    db = get_db()
    
    cursor = db.execute('''
        SELECT 
            carrier,
            COUNT(*) as total_shipped,
            COUNT(CASE WHEN actual_delivery_date IS NOT NULL THEN 1 END) as delivered,
            AVG(CASE 
                WHEN actual_delivery_date IS NOT NULL 
                THEN julianday(actual_delivery_date) - julianday(ship_date)
                ELSE NULL
            END) as avg_delivery_days
        FROM orders
        WHERE tracking_number IS NOT NULL
        GROUP BY carrier
    ''')
    
    return jsonify(rows_to_list(cursor.fetchall()))

# ============================================
# EXPORT ENDPOINT
# ============================================

@app.route('/api/orders/export', methods=['GET'])
def export_orders():
    """Export orders as CSV"""
    db = get_db()
    
    cursor = db.execute('''
        SELECT 
            order_id,
            customer_name,
            customer_email,
            customer_phone,
            shipping_address,
            order_date,
            order_total,
            payment_status,
            order_status,
            build_start_date,
            ship_date,
            tracking_number,
            carrier,
            estimated_delivery_date,
            actual_delivery_date
        FROM orders
        ORDER BY order_date DESC
    ''')
    
    orders = cursor.fetchall()
    
    # Build CSV
    csv_lines = ['Order ID,Customer Name,Customer Email,Phone,Shipping Address,Order Date,Total,Payment Status,Order Status,Build Start,Ship Date,Tracking,Carrier,Est Delivery,Actual Delivery']
    
    for order in orders:
        row = [
            order['order_id'],
            order['customer_name'],
            order['customer_email'],
            order['customer_phone'] or '',
            (order['shipping_address'] or '').replace('"', '""'),
            order['order_date'],
            order['order_total'],
            order['payment_status'],
            order['order_status'],
            order['build_start_date'] or '',
            order['ship_date'] or '',
            order['tracking_number'] or '',
            order['carrier'] or '',
            order['estimated_delivery_date'] or '',
            order['actual_delivery_date'] or ''
        ]
        csv_lines.append(','.join(f'"{v}"' for v in row))
    
    return '\n'.join(csv_lines), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=vesper-orders-export.csv'
    }

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        db = get_db()
        cursor = db.execute("SELECT COUNT(*) as count FROM orders")
        order_count = cursor.fetchone()['count']
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'orders': order_count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    import os
    os.makedirs('database', exist_ok=True)
    init_db()
    print("Starting Vesper AI Order Manager on http://localhost:5050")
    app.run(host='0.0.0.0', port=5050, debug=True)