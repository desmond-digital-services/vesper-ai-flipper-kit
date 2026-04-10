# RedWand Flipper Kit Procurement Setup Guide

## Overview

This automation system manages procurement for the RedWand Flipper Kit components across multiple suppliers:
- **Flipper Zero** ($199) - Main device
- **Moto G Play 2026** ($130) - Companion phone
- **32GB SD Card** ($8) - Storage

## Project Structure

```
redwand-ai/
├── automation/
│   ├── config.py              # Configuration (products, suppliers, notifications)
│   ├── micro-center-order.py  # Micro Center ordering & stock checks
│   ├── hacker-warehouse-order.py  # Hacker Warehouse ordering
│   ├── stock-checker.py       # Multi-supplier stock monitoring
│   ├── order-tracker.py      # Order tracking & cost analysis
│   └── procurement.db        # SQLite database (created on first run)
├── email-templates/
│   └── supplier-inquiry.html  # Email templates for supplier communication
└── docs/
    └── procurement-setup-guide.md  # This file
```

## Prerequisites

```bash
# Install dependencies
pip install requests beautifulsoup4 selenium webdriver-manager tabulate

# For SMS alerts (optional)
pip install twilio
```

## Configuration

### 1. Set Up Config Secrets

Copy the example config and add your credentials:

```python
# automation/config.py - Update these sections:

# Email notifications
NOTIFICATIONS["email"]["enabled"] = True
NOTIFICATIONS["email"]["smtp_host"] = "smtp.gmail.com"
NOTIFICATIONS["email"]["smtp_port"] = 587
NOTIFICATIONS["email"]["smtp_user"] = "your-email@gmail.com"
NOTIFICATIONS["email"]["smtp_password"] = "your-app-password"  # Gmail App Password
NOTIFICATIONS["email"]["to_addrs"] = ["your-phone@ carrier.net"]  # Or admin email

# SMS notifications (Twilio)
NOTIFICATIONS["sms"]["enabled"] = True
NOTIFICATIONS["sms"]["twilio_sid"] = "AC..."
NOTIFICATIONS["sms"]["twilio_token"] = "..."
NOTIFICATIONS["sms"]["from_number"] = "+1..."
NOTIFICATIONS["sms"]["to_numbers"] = ["+1...", ]

# Telegram notifications
NOTIFICATIONS["telegram"]["enabled"] = True
NOTIFICATIONS["telegram"]["bot_token"] = "123456:ABC..."
NOTIFICATIONS["telegram"]["chat_ids"] = [12345678, ]
```

### 2. Gmail App Password Setup

1. Enable 2FA on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use that 16-character password in `smtp_password`

### 3. Twilio Setup (SMS)

1. Create a Twilio account at https://twilio.com
2. Get your Account SID and Auth Token from the console
3. Purchase a phone number
4. Add the number to `from_number`

### 4. Telegram Bot Setup

1. Message @BotFather on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token to `bot_token`
4. Start a chat with your bot, then get your chat ID:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
5. Add your numeric chat ID to `chat_ids`

## Usage

### Stock Checking

```bash
# Check all suppliers
python automation/stock-checker.py check

# Check specific supplier
python automation/stock-checker.py check --supplier micro_center

# Check all suppliers quietly (for cron)
python automation/stock-checker.py check --quiet

# Generate stock report
python automation/stock-checker.py report

# Save report to file
python automation/stock-checker.py report --save stock-report.json

# Find best available supplier for a product
python automation/stock-checker.py find flipper_zero

# Continuous monitoring (every hour)
python automation/stock-checker.py monitor --interval 3600
```

### Micro Center Orders

```bash
# Check stock at all stores
python automation/micro-center-order.py check

# Check specific product
python automation/micro-center-order.py check --product flipper_zero

# Generate shopping list for in-store pickup
python automation/micro-center-order.py list

# Generate for multiple kits
python automation/micro-center-order.py list --quantity 5

# Create reservation record
python automation/micro-center-order.py reserve

# Check order status
python automation/micro-center-order.py status
python automation/micro-center-order.py status --order MC-20241015-001
```

### Hacker Warehouse Orders

```bash
# Check stock
python automation/hacker-warehouse-order.py check

# Generate order summary
python automation/hacker-warehouse-order.py summary

# Create order record
python automation/hacker-warehouse-order.py order
```

### Order Tracking

```bash
# List all orders
python automation/order-tracker.py list

# Filter by status
python automation/order-tracker.py list --status pending
python automation/order-tracker.py list --status delivered

# Filter by supplier
python automation/order-tracker.py list --supplier micro_center

# Show order details
python automation/order-tracker.py show MC-20241015-001

# Update order status
python automation/order-tracker.py status MC-20241015-001 shipped
python automation/order-tracker.py status MC-20241015-001 shipped --tracking TRACK123

# Mark as received
python automation/order-tracker.py received MC-20241015-001

# Cost variance report
python automation/order-tracker.py costs

# Procurement summary
python automation/order-tracker.py summary
```

## Scheduling with Cron

### Daily Stock Check (8 AM)

```bash
# Edit crontab
crontab -e

# Add this line:
0 8 * * * cd /path/to/redwand-ai/automation && python stock-checker.py check --quiet >> /path/to/redwand-ai/logs/cron.log 2>&1
```

### Weekly Full Report (Monday 9 AM)

```bash
0 9 * * 1 cd /path/to/redwand-ai/automation && python stock-checker.py report --save ../reports/stock-$(date +\%Y-\%m-\%d).json
```

## Email Templates

The `email-templates/supplier-inquiry.html` file contains 4 templates:

1. **Order Confirmation** - Sent after placing an order
2. **Shipping Inquiry** - Request tracking info
3. **Stock Availability Request** - Check if items are in stock
4. **Return/Exchange Request** - Process returns or exchanges

### Using Templates

Open the HTML file in a browser and add `?template=<name>` to view specific templates:

- `supplier-inquiry.html?template=order-confirmation`
- `supplier-inquiry.html?template=shipping-inquiry`
- `supplier-inquiry.html?template=stock-request`
- `supplier-inquiry.html?template=return-request`

Replace template variables (e.g., `{{order_number}}`, `{{order_date}}`) with actual values before sending.

## Database Schema

### Orders Table

| Column | Type | Description |
|--------|------|-------------|
| order_number | TEXT | Unique order identifier |
| supplier | TEXT | micro_center, hacker_warehouse, or lab401 |
| product_sku | TEXT | Product SKU |
| product_name | TEXT | Human-readable product name |
| quantity | INTEGER | Number of items |
| unit_price | REAL | Price per unit |
| total_price | REAL | quantity * unit_price |
| shipping_cost | REAL | Shipping cost |
| status | TEXT | Order status |
| store_id | TEXT | Store location ID |
| store_name | TEXT | Store name |
| tracking_number | TEXT | Shipping tracking |
| created_at | TIMESTAMP | Order creation time |
| updated_at | TIMESTAMP | Last update time |
| received_at | TIMESTAMP | When items were received |

### Stock Checks Table

| Column | Type | Description |
|--------|------|-------------|
| supplier | TEXT | Supplier name |
| store_id | TEXT | Store ID (for Micro Center) |
| product_sku | TEXT | Product SKU |
| stock_status | TEXT | in_stock, low_stock, out_of_stock, backordered |
| quantity | INTEGER | Available quantity |
| checked_at | TIMESTAMP | Check timestamp |

## API Reference

### check_all_suppliers(product_skus)

Check stock across all configured suppliers.

```python
from stock_checker import check_all_suppliers

results = check_all_suppliers({
    "flipper_zero": "FLIPPER-ZERO",
    "moto_g_play": "MOTO-G-PLAY-2026"
})
```

### find_best_supplier(product_key)

Find the best available supplier for a product.

```python
from stock_checker import find_best_supplier

result = find_best_supplier("flipper_zero")
# Returns: {"available": True, "supplier_name": "Micro Center", ...}
```

### create_order(order_number, supplier, items, ...)

Create a new order record.

```python
from order_tracker import create_order

create_order(
    order_number="MC-20241015-001",
    supplier="micro_center",
    items=[
        {"sku": "FLIPPER-ZERO", "name": "Flipper Zero", "price": 199.00, "quantity": 1}
    ],
    store_name="Austin"
)
```

### update_order_status(order_number, status, ...)

Update an order's status.

```python
from order_tracker import update_order_status

update_order_status(
    "MC-20241015-001",
    "shipped",
    tracking_number="1Z999AA10123456784"
)
```

## Troubleshooting

### "No module named 'requests'"

```bash
pip install requests beautifulsoup4 tabulate
```

### "beautifulsoup4 not installed" warning

This is informational. Stock checking will still work but with reduced accuracy.

### Micro Center API returns 403

Micro Center may rate-limit API access. Wait a few minutes and try again.

### Gmail authentication fails

1. Make sure you're using an App Password, not your regular password
2. Enable 2FA on your Google account first
3. Check that the SMTP settings are correct (port 587, TLS)

### Database locked errors

Only one process should write to the database at a time. If running multiple scripts, add file locking.

## Support

For issues or questions:
- Check the logs in `procurement.log`
- Review the database directly: `sqlite3 procurement.db ".schema"`
- Run with verbose logging: `python script.py --verbose` (if supported)
