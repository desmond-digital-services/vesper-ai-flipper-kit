# Vesper AI Email System - Setup Guide

## Overview

The Vesper AI Email Automation System provides automated customer notifications throughout the Flipper Kit order lifecycle:

| Email Type | Timing | Purpose |
|------------|--------|---------|
| Order Confirmation | Immediate | Confirm order, payment, timeline |
| Build Progress | Day 5 | Update on production status |
| Shipped | Day 8-10 | Tracking info, setup resources |
| Delivery Follow-up | Day 12-15 | Check-in, support, feedback |
| Payment Failed | As needed | Error details, retry options |

## Directory Structure

```
projects/vesper-ai/
├── email-templates/
│   ├── order-confirmation.html
│   ├── build-progress.html
│   ├── shipped.html
│   ├── followup.html
│   └── payment-failed.html
├── backend/
│   ├── email-system.py
│   └── orders.db (created automatically)
├── docs/
│   └── email-setup-guide.md
└── .env (your configuration)
```

## Installation

### 1. System Requirements

- Python 3.8+
- SQLite3 (included with Python)
- SMTP access (Gmail, SendGrid, Mailgun, etc.)

### 2. Install Dependencies

No external dependencies required - uses Python standard library only.

### 3. Configure Environment Variables

Create a `.env` file in `projects/vesper-ai/`:

```bash
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Email Addresses
FROM_EMAIL=noreply@vespere.ai
FROM_NAME=Vesper AI
REPLY_TO=help@vespere.ai

# Debug mode (set to 'true' for testing without sending)
EMAIL_DEBUG=false
```

### 4. Gmail SMTP Setup

If using Gmail:

1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/security
3. Create an App Password (select "Mail" and "Other")
4. Use the app password as `SMTP_PASSWORD`

### 5. Alternative SMTP Providers

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.com
SMTP_PASSWORD=your-mailgun-password
```

**Custom SMTP Server:**
```bash
SMTP_HOST=mail.yourserver.com
SMTP_PORT=465
SMTP_USER=your-username
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
```

## Usage

### Command-Line Interface

```bash
# Send order confirmation
python backend/email-system.py send-confirmation \
    ORD-12345 "John Smith" "john@example.com" "2026-04-08" 499.00

# Send build progress update
python backend/email-system.py send-build \
    ORD-12345 "John Smith" "john@example.com" "2026-04-08"

# Send shipped notification
python backend/email-system.py send-shipped \
    ORD-12345 "John Smith" "john@example.com" "94001234567890123456789" "2026-04-08"

# Send delivery follow-up
python backend/email-system.py send-followup \
    ORD-12345 "John Smith" "john@example.com"

# Send payment failed notification
python backend/email-system.py send-payment-failed \
    ORD-12345 "John Smith" "john@example.com" "Card declined - insufficient funds"

# Process all scheduled emails (for cron job)
python backend/email-system.py batch

# Send test email
python backend/email-system.py test
```

### Python API

```python
from backend.email_system import VesperEmailSystem

# Initialize
email_system = VesperEmailSystem()

# Send order confirmation
email_system.send_order_confirmation(
    order_id='ORD-12345',
    customer_name='John Smith',
    customer_email='john@example.com',
    order_date='2026-04-08',
    order_amount=499.00
)

# Send shipped notification
email_system.send_shipped(
    order_id='ORD-12345',
    customer_name='John Smith',
    customer_email='john@example.com',
    tracking_number='94001234567890123456789',
    order_date='2026-04-08'
)
```

### Cron Job Setup

Add to crontab for automated processing:

```bash
# Run batch every hour during business hours
0 9-17 * * * cd /path/to/projects/vesper-ai && python backend/email-system.py batch >> logs/email-cron.log 2>&1

# Or run daily at 9am
0 9 * * * cd /path/to/projects/vesper-ai && python backend/email-system.py batch >> logs/email-cron.log 2>&1
```

## Email Template Variables

All templates support these placeholders (use `{{VARIABLE_NAME}}`):

### Order Confirmation
- `{{ORDER_NUMBER}}` - Order ID (e.g., ORD-12345)
- `{{CUSTOMER_NAME}}` - Customer's full name
- `{{CUSTOMER_EMAIL}}` - Customer's email address
- `{{ORDER_DATE}}` - Formatted date (April 8, 2026)
- `{{ORDER_AMOUNT}}` - Order total (499.00)
- `{{ESTIMATED_DELIVERY}}` - Delivery estimate

### Build Progress
- `{{ORDER_NUMBER}}` - Order ID
- `{{CUSTOMER_NAME}}` - Customer's name

### Shipped
- `{{TRACKING_NUMBER}}` - USPS tracking number
- `{{ESTIMATED_DELIVERY}}` - Delivery date
- `{{TRACKING_URL}}` - Direct USPS tracking link
- `{{SETUP_VIDEO_URL}}` - Setup video URL
- `{{GUIDE_URL}}` - Quick start guide URL
- `{{APP_URL}}` - App download URL

### Follow-up
- `{{ORDER_NUMBER}}` - Order ID
- `{{CUSTOMER_NAME}}` - Customer's name
- `{{REVIEW_URL}}` - Review submission URL

### Payment Failed
- `{{ORDER_NUMBER}}` - Order ID
- `{{ERROR_REASON}}` - Payment error description
- `{{CUSTOMER_NAME}}` - Customer's name
- `{{CUSTOMER_EMAIL}}` - Customer's email
- `{{RETRY_PAYMENT_URL}}` - Payment retry link

## Database Schema

The system uses SQLite (`orders.db`) with these tables:

### orders
| Column | Type | Description |
|--------|------|-------------|
| order_id | TEXT PRIMARY KEY | Unique order identifier |
| customer_name | TEXT | Customer's full name |
| customer_email | TEXT | Customer's email |
| order_date | DATE | Order placement date |
| order_amount | REAL | Order total |
| tracking_number | TEXT | USPS tracking number |
| ship_date | DATE | Ship date |
| status | TEXT | pending/shipped/completed |

### email_log
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment ID |
| order_id | TEXT | Order reference |
| email_type | TEXT | Email type identifier |
| recipient_email | TEXT | Recipient email |
| sent_at | DATETIME | Send timestamp |
| smtp_status | TEXT | sent/failed |
| error_message | TEXT | Error details if failed |

## Integration Points

### From Your Order System

When a new order is placed:

```python
# In your order processing code
email_system = VesperEmailSystem()

# Send confirmation immediately
email_system.send_order_confirmation(
    order_id=order.id,
    customer_name=order.customer_name,
    customer_email=order.customer_email,
    order_date=order.date.strftime('%Y-%m-%d'),
    order_amount=order.total
)

# Schedule build progress (Day 5)
# Schedule shipped notification (Day 8-10)
# Schedule follow-up (Day 12-15)
```

### From Your Shipping System

When order ships:

```python
email_system.send_shipped(
    order_id=order.id,
    customer_name=order.customer_name,
    customer_email=order.customer_email,
    tracking_number=shipment.tracking_number,
    order_date=order.date.strftime('%Y-%m-%d'),
    estimated_delivery=shipment.delivery_date.strftime('%B %d, %Y')
)
```

### From Your Payment System

When payment fails:

```python
email_system.send_payment_failed(
    order_id=order.id,
    customer_name=order.customer_name,
    customer_email=order.customer_email,
    error_reason=payment.error_message
)
```

## Troubleshooting

### "SMTP authentication failed"
- Verify SMTP credentials
- For Gmail, ensure you're using an App Password, not your regular password

### "Connection timed out"
- Check firewall/network settings
- Verify SMTP host and port are correct
- Some hosts block port 587; try port 465

### "Template not found"
- Verify template files exist in `email-templates/` directory
- Check file extensions are `.html`

### "Email already sent" (unexpected)
- Check database for duplicate entries
- Verify UNIQUE constraint on (order_id, email_type) in email_log

### Debug Mode

Set `EMAIL_DEBUG=true` in `.env` to log emails without sending:

```bash
EMAIL_DEBUG=true
```

This will show what would be sent without actually delivering emails.

## Testing Checklist

- [ ] Order confirmation sends correctly
- [ ] Build progress template renders properly
- [ ] Shipped notification includes valid tracking links
- [ ] Follow-up email includes support resources
- [ ] Payment failed email shows error details
- [ ] All emails render on mobile devices
- [ ] Duplicate prevention works correctly
- [ ] SMTP connection succeeds
- [ ] Database logging works
- [ ] Cron job executes properly

## Support

For issues:
- Email: help@vespere.ai
- Documentation: https://vespere.ai/docs/email-system