# Vesper AI Order Database Setup Guide

This guide explains how to set up and run the Vesper AI Order Management System locally.

## Prerequisites

- Python 3.8 or higher
- SQLite (included with Python)
- Web browser (Chrome/Firefox/Safari for admin dashboard)

## Project Structure

```
vesper-ai/
├── database/
│   ├── schema.sql          # Database schema
│   └── vesper_orders.db    # SQLite database (created on first run)
├── backend/
│   ├── order-manager.py    # Flask API server
│   ├── email-system.py     # Email automation
│   └── webhooks.py         # Stripe webhook handler
├── web/
│   ├── admin/
│   │   ├── index.html      # Admin dashboard
│   │   ├── admin.css       # Dashboard styles
│   │   └── js/
│   │       └── admin.js    # Dashboard logic
│   └── index.html          # Public storefront
└── docs/
    └── database-setup-guide.md
```

## Quick Start

### 1. Navigate to Project Directory

```bash
cd ~/clawd/projects/vesper-ai
```

### 2. Install Python Dependencies

```bash
pip install flask
```

Or if using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask
```

### 3. Initialize the Database

The database is automatically created on first run. To manually initialize:

```bash
cd backend
python3 -c "
import sqlite3
conn = sqlite3.connect('../database/vesper_orders.db')
with open('../database/schema.sql', 'r') as f:
    conn.executescript(f.read())
conn.close()
print('Database initialized!')
"
```

### 4. Start the Backend Server

```bash
cd ~/clawd/projects/vesper-ai/backend
python3 order-manager.py
```

You should see:
```
Database initialized successfully
Starting Vesper AI Order Manager on http://localhost:5050
```

### 5. Access the Admin Dashboard

Open your browser and go to:
```
file:///Users/scrimwiggins/clawd/projects/vesper-ai/web/admin/index.html
```

Or serve it locally:
```bash
cd ~/clawd/projects/vesper-ai/web
python3 -m http.server 8080
```
Then visit: `http://localhost:8080/admin/index.html`

## API Endpoints

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders` | List all orders (supports `?status=`, `?payment_status=`, `?search=`) |
| GET | `/api/orders/<id>` | Get single order with all details |
| POST | `/api/orders` | Create new order |
| PUT | `/api/orders/<id>` | Update order fields |
| PUT | `/api/orders/<id>/status` | Update order status |
| POST | `/api/orders/<id>/tracking` | Add tracking number |
| POST | `/api/orders/<id>/notes` | Add note to order |
| GET | `/api/orders/export` | Export all orders as CSV |

### Email Log

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/<id>/emails` | Get email log for order |
| POST | `/api/emails` | Log an email |

### Hardware Procurement

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/<id>/procurement` | Get procurement for order |
| POST | `/api/procurement` | Add procurement record |
| PUT | `/api/procurement/<id>` | Update procurement status |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/sales?period=day|week|month` | Sales by period |
| GET | `/api/reports/revenue` | Revenue metrics |
| GET | `/api/reports/build-times` | Build time analytics |
| GET | `/api/reports/shipping` | Shipping performance |
| GET | `/api/health` | Health check |

## Integration Points

### Stripe Webhook Integration

To connect Stripe webhooks, add this to your webhook handler:

```python
# In your Stripe webhook handler
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    # ... verify webhook signature ...
    
    if event['type'] == 'payment_intent.succeeded':
        payment = event['data']['object']
        
        # Call order-manager API
        import requests
        requests.post('http://localhost:5050/api/orders', json={
            'customer_email': payment['receipt_email'],
            'customer_name': payment['metadata'].get('name'),
            'shipping_address': payment['metadata'].get('address'),
            'stripe_payment_intent_id': payment['id'],
            'payment_status': 'paid',
            'order_status': 'pending'
        })
```

### Email System Integration

The email system logs sent emails to the `email_log` table. To integrate:

```python
# After sending an email, log it
requests.post('http://localhost:5050/api/emails', json={
    'order_id': 'VPR-2026-00001',
    'email_type': 'confirmation',
    'subject': 'Your Vesper AI Flipper Kit Order',
    'sent_date': datetime.utcnow().isoformat() + 'Z',
    'status': 'sent',
    'recipient_email': customer_email
})
```

### Hardware Procurement Integration

Track supplier orders by adding procurement records:

```python
requests.post('http://localhost:5050/api/procurement', json={
    'order_id': 'VPR-2026-00001',
    'supplier': 'Micro Center',
    'item': 'Flipper Zero',
    'cost': 169.99,
    'status': 'ordered'
})
```

## Database Schema

### Orders Table

| Field | Type | Description |
|-------|------|-------------|
| order_id | TEXT (PK) | Unique order ID (e.g., VPR-2026-00001) |
| customer_name | TEXT | Customer full name |
| customer_email | TEXT | Customer email |
| customer_phone | TEXT | Optional phone |
| shipping_address | TEXT (JSON) | {street, city, state, zip, country} |
| order_date | TEXT | ISO 8601 timestamp |
| order_total | REAL | Total amount (default 499.00) |
| payment_status | TEXT | pending/paid/failed |
| stripe_payment_intent_id | TEXT | Stripe payment ID |
| order_status | TEXT | pending/building/testing/shipped/delivered |
| build_start_date | TEXT | When build started |
| ship_date | TEXT | When shipped |
| tracking_number | TEXT | USPS tracking |
| carrier | TEXT | Shipping carrier (default USPS) |
| estimated_delivery_date | TEXT | Estimated delivery |
| actual_delivery_date | TEXT | Actual delivery |
| notes | TEXT | General notes |

### Email Log Table

| Field | Type | Description |
|-------|------|-------------|
| log_id | INTEGER (PK) | Auto-increment ID |
| order_id | TEXT (FK) | References orders.order_id |
| email_type | TEXT | confirmation/build/shipped/followup/payment_failed |
| subject | TEXT | Email subject line |
| sent_date | TEXT | ISO 8601 timestamp |
| status | TEXT | sent/failed |
| error_message | TEXT | Error details if failed |
| recipient_email | TEXT | To address |

### Hardware Procurement Table

| Field | Type | Description |
|-------|------|-------------|
| procurement_id | INTEGER (PK) | Auto-increment ID |
| order_id | TEXT (FK) | References orders.order_id |
| supplier | TEXT | Micro Center/Hacker Warehouse/Amazon |
| item | TEXT | Flipper Zero/Moto G Play/SD Card/etc |
| quantity | INTEGER | Number of items |
| cost | REAL | Cost in dollars |
| order_date | TEXT | When ordered from supplier |
| tracking_number | TEXT | Supplier tracking |
| status | TEXT | ordered/shipped/received/assembled |

## Testing

### Add Sample Data

Connect to the database and insert test orders:

```bash
sqlite3 ~/clawd/projects/vesper-ai/database/vesper_orders.db
```

```sql
INSERT INTO orders (order_id, customer_name, customer_email, customer_phone, shipping_address, order_date, order_total, payment_status, stripe_payment_intent_id, order_status, build_start_date, estimated_delivery_date)
VALUES 
('VPR-2026-00001', 'John Smith', 'john@example.com', '+1-555-123-4567', '{"street":"123 Main St","city":"Austin","state":"TX","zip":"78701","country":"US"}', datetime('now'), 499.00, 'paid', 'pi_test123', 'building', datetime('now'), datetime('now', '+5 days')),
('VPR-2026-00002', 'Jane Doe', 'jane@example.com', NULL, '{"street":"456 Oak Ave","city":"Dallas","state":"TX","zip":"75201","country":"US"}', datetime('now'), 499.00, 'paid', 'pi_test456', 'shipped', datetime('now', '-2 days'), datetime('now', '+3 days'), '9400111899223334445555');

INSERT INTO email_log (order_id, email_type, subject, sent_date, status, recipient_email)
VALUES 
('VPR-2026-00001', 'confirmation', 'Your Vesper AI Flipper Kit Order', datetime('now'), 'sent', 'john@example.com'),
('VPR-2026-00002', 'confirmation', 'Your Vesper AI Flipper Kit Order', datetime('now', '-2 days'), 'sent', 'jane@example.com'),
('VPR-2026-00002', 'shipped', 'Your Vesper AI Flipper Kit Has Shipped!', datetime('now'), 'sent', 'jane@example.com');

INSERT INTO hardware_procurement (order_id, supplier, item, cost, order_date, status)
VALUES 
('VPR-2026-00001', 'Micro Center', 'Flipper Zero', 169.99, datetime('now'), 'ordered'),
('VPR-2026-00002', 'Hacker Warehouse', 'Moto G Play', 129.99, datetime('now', '-3 days'), 'received');
```

### Test API Manually

```bash
# Health check
curl http://localhost:5050/api/health

# List orders
curl http://localhost:5050/api/orders

# Get single order
curl http://localhost:5050/api/orders/VPR-2026-00001

# Update status
curl -X PUT http://localhost:5050/api/orders/VPR-2026-00001/status \
  -H "Content-Type: application/json" \
  -d '{"order_status": "building"}'

# Get revenue report
curl http://localhost:5050/api/reports/revenue
```

## Troubleshooting

### "Connection refused" or Admin shows "Disconnected"

1. Make sure the backend server is running:
   ```bash
   ps aux | grep order-manager
   ```

2. Check if the port is in use:
   ```bash
   lsof -i :5050
   ```

3. Restart the server:
   ```bash
   cd ~/clawd/projects/vesper-ai/backend
   python3 order-manager.py
   ```

### Database locked errors

Close any other connections to the database (other terminals, SQLite browsers).

### CORS issues (if serving from different origin)

The admin dashboard uses `file://` protocol and the API runs on `localhost:5050`. For development, you may need to update the `API_BASE` in `admin.js` to point to your backend URL.

## Next Steps

1. **Stripe Setup**: Configure your Stripe webhook URL in the Stripe dashboard
2. **Email Integration**: Update `email-system.py` with your SMTP credentials
3. **Production Deployment**: For production, use gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5050 order-manager:app
   ```

## API Reference Summary

```
GET    /api/health
GET    /api/orders
GET    /api/orders/:id
POST   /api/orders
PUT    /api/orders/:id
PUT    /api/orders/:id/status
POST   /api/orders/:id/tracking
POST   /api/orders/:id/notes
GET    /api/orders/:id/emails
GET    /api/orders/:id/procurement
GET    /api/orders/export
POST   /api/emails
POST   /api/procurement
PUT    /api/procurement/:id
GET    /api/reports/sales
GET    /api/reports/revenue
GET    /api/reports/build-times
GET    /api/reports/shipping
```