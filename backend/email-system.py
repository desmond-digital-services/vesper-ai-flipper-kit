#!/usr/bin/env python3
"""
RedWand Email Automation System
Automated customer notification system for Flipper Kit orders

Supports:
- Order confirmation (immediate)
- Build progress (Day 5)
- Shipped notification (Day 8-10)
- Delivery follow-up (Day 12-15)
- Payment failed (as needed)

Author: RedWand
Version: 1.0.0
"""

import os
import smtplib
import sqlite3
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Email system configuration from environment variables"""
    
    # SMTP Settings
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    # Email Addresses
    FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@redwand.io')
    FROM_NAME = os.getenv('FROM_NAME', 'RedWand')
    REPLY_TO = os.getenv('REPLY_TO', 'help@redwand.io')
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    TEMPLATES_DIR = BASE_DIR / 'email-templates'
    DB_PATH = BASE_DIR / 'backend' / 'orders.db'
    
    # Email timing (days after order)
    BUILD_PROGRESS_DAY = 5
    SHIPPED_DAY_MIN = 8
    SHIPPED_DAY_MAX = 10
    FOLLOWUP_DAY_MIN = 12
    FOLLOWUP_DAY_MAX = 15
    
    # Debug mode
    DEBUG = os.getenv('EMAIL_DEBUG', 'false').lower() == 'true'


# ============================================================================
# DATABASE
# ============================================================================

class EmailDatabase:
    """SQLite database for email tracking"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                email_type TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                smtp_status TEXT,
                error_message TEXT,
                UNIQUE(order_id, email_type)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                order_date DATE NOT NULL,
                order_amount REAL NOT NULL,
                tracking_number TEXT,
                ship_date DATE,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_email(self, order_id: str, email_type: str, recipient_email: str,
                  smtp_status: str = 'sent', error_message: str = None) -> bool:
        """Log sent email, return False if already sent (duplicate prevention)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_log (order_id, email_type, recipient_email, smtp_status, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, email_type, recipient_email, smtp_status, error_message))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Duplicate - email already sent
            return False
    
    def was_sent(self, order_id: str, email_type: str) -> bool:
        """Check if email was already sent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM email_log 
            WHERE order_id = ? AND email_type = ?
        ''', (order_id, email_type))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def add_order(self, order_id: str, customer_name: str, customer_email: str,
                  order_date: str, order_amount: float):
        """Add or update order record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO orders 
            (order_id, customer_name, customer_email, order_date, order_amount, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (order_id, customer_name, customer_email, order_date, order_amount))
        conn.commit()
        conn.close()
    
    def get_pending_orders(self) -> List[Dict]:
        """Get orders that need emails based on timing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM orders')
        columns = [desc[0] for desc in cursor.description]
        orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        return orders
    
    def update_tracking(self, order_id: str, tracking_number: str, ship_date: str):
        """Update order with tracking info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE orders 
            SET tracking_number = ?, ship_date = ?, status = 'shipped'
            WHERE order_id = ?
        ''', (tracking_number, ship_date, order_id))
        conn.commit()
        conn.close()


# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

class EmailTemplate:
    """Email template renderer with variable substitution"""
    
    def __init__(self, template_path: Path):
        self.template_path = template_path
        with open(template_path, 'r', encoding='utf-8') as f:
            self.html = f.read()
    
    def render(self, **kwargs) -> str:
        """Substitute {{VARIABLE}} placeholders with values"""
        result = self.html
        for key, value in kwargs.items():
            placeholder = f'{{{{{key}}}}}'
            result = result.replace(placeholder, str(value))
        return result


class TemplateManager:
    """Manages all email templates"""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self._templates = {}
    
    def get(self, template_name: str) -> EmailTemplate:
        """Get template by name"""
        if template_name not in self._templates:
            template_path = self.templates_dir / f'{template_name}.html'
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
            self._templates[template_name] = EmailTemplate(template_path)
        return self._templates[template_name]


# ============================================================================
# EMAIL SENDER
# ============================================================================

class EmailSender:
    """Sends emails via SMTP"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def send(self, to_email: str, subject: str, html_content: str,
             plain_text: str = None) -> Tuple[bool, str]:
        """Send email, return (success, error_message)"""
        
        if self.config.DEBUG:
            self.logger.info(f"[DEBUG] Would send email to {to_email}: {subject}")
            return True, None
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.FROM_NAME} <{self.config.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Reply-To'] = self.config.REPLY_TO
            
            # Attach both HTML and plain text versions
            if plain_text:
                msg.attach(MIMEText(plain_text, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.config.SMTP_HOST, self.config.SMTP_PORT)
            if self.config.SMTP_USE_TLS:
                server.starttls()
            
            if self.config.SMTP_USER and self.config.SMTP_PASSWORD:
                server.login(self.config.SMTP_USER, self.config.SMTP_PASSWORD)
            
            server.sendmail(self.config.FROM_EMAIL, to_email, msg.as_string())
            server.quit()
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True, None
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg


# ============================================================================
# EMAIL SYSTEM
# ============================================================================

class RedWandEmailSystem:
    """Main email automation system"""
    
    # Email type definitions
    EMAIL_TYPES = {
        'order_confirmation': {
            'template': 'order-confirmation',
            'subject': 'Your RedWand Flipper Kit Order #{order_number} is Confirmed',
            'description': 'Sent immediately on order'
        },
        'build_progress': {
            'template': 'build-progress',
            'subject': 'Your RedWand Kit is Being Built',
            'description': 'Sent on Day 5 of production'
        },
        'shipped': {
            'template': 'shipped',
            'subject': 'Your RedWand Kit Has Shipped! 📦',
            'description': 'Sent when order ships (Day 8-10)'
        },
        'followup': {
            'template': 'followup',
            'subject': "How's Your RedWand Kit Working?",
            'description': 'Sent 2-4 days after delivery (Day 12-15)'
        },
        'payment_failed': {
            'template': 'payment-failed',
            'subject': 'Payment Failed for Order #{order_number}',
            'description': 'Sent when payment fails'
        }
    }
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.db = EmailDatabase(self.config.DB_PATH)
        self.templates = TemplateManager(self.config.TEMPLATES_DIR)
        self.sender = EmailSender(self.config)
        
        # Setup logging
        logging.basicConfig(
            level=logging.DEBUG if self.config.DEBUG else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_template(self, email_type: str) -> Dict:
        """Get email configuration"""
        return self.EMAIL_TYPES[email_type]
    
    def _format_date(self, date_str: str) -> str:
        """Format date for display"""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%B %d, %Y')
        except:
            return date_str
    
    def _calculate_delivery(self, order_date: str, days: int = 10) -> str:
        """Calculate estimated delivery date"""
        try:
            dt = datetime.strptime(order_date, '%Y-%m-%d')
            delivery = dt + timedelta(days=days)
            return delivery.strftime('%B %d, %Y')
        except:
            return f"{days} days from order"
    
    def send_order_confirmation(self, order_id: str, customer_name: str,
                                customer_email: str, order_date: str,
                                order_amount: float, **kwargs) -> Tuple[bool, str]:
        """Send order confirmation email"""
        
        if self.db.was_sent(order_id, 'order_confirmation'):
            return False, "Email already sent"
        
        email_config = self._load_template('order_confirmation')
        template = self.templates.get(email_config['template'])
        
        subject = email_config['subject'].format(order_number=order_id)
        
        html = template.render(
            ORDER_NUMBER=order_id,
            CUSTOMER_NAME=customer_name,
            CUSTOMER_EMAIL=customer_email,
            ORDER_DATE=self._format_date(order_date),
            ORDER_AMOUNT=f"{order_amount:.2f}",
            ESTIMATED_DELIVERY=self._calculate_delivery(order_date, 10)
        )
        
        success, error = self.sender.send(customer_email, subject, html)
        
        status = 'sent' if success else 'failed'
        self.db.log_email(order_id, 'order_confirmation', customer_email, status, error)
        
        # Also add to orders table
        self.db.add_order(order_id, customer_name, customer_email, order_date, order_amount)
        
        return success, error
    
    def send_build_progress(self, order_id: str, customer_name: str,
                            customer_email: str, order_date: str) -> Tuple[bool, str]:
        """Send build progress email (Day 5)"""
        
        if self.db.was_sent(order_id, 'build_progress'):
            return False, "Email already sent"
        
        email_config = self._load_template('build_progress')
        template = self.templates.get(email_config['template'])
        
        html = template.render(
            ORDER_NUMBER=order_id,
            CUSTOMER_NAME=customer_name
        )
        
        success, error = self.sender.send(customer_email, email_config['subject'], html)
        
        status = 'sent' if success else 'failed'
        self.db.log_email(order_id, 'build_progress', customer_email, status, error)
        
        return success, error
    
    def send_shipped(self, order_id: str, customer_name: str, customer_email: str,
                     tracking_number: str, order_date: str,
                     estimated_delivery: str = None) -> Tuple[bool, str]:
        """Send shipped notification email"""
        
        if self.db.was_sent(order_id, 'shipped'):
            return False, "Email already sent"
        
        email_config = self._load_template('shipped')
        template = self.templates.get(email_config['template'])
        
        delivery = estimated_delivery or self._calculate_delivery(order_date, 12)
        tracking_url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
        
        html = template.render(
            TRACKING_NUMBER=tracking_number,
            ESTIMATED_DELIVERY=delivery,
            TRACKING_URL=tracking_url,
            SETUP_VIDEO_URL='https://redwand.io/setup-video',
            GUIDE_URL='https://redwand.io/quick-start',
            APP_URL='https://redwand.io/app'
        )
        
        success, error = self.sender.send(customer_email, email_config['subject'], html)
        
        status = 'sent' if success else 'failed'
        self.db.log_email(order_id, 'shipped', customer_email, status, error)
        
        # Update tracking info
        if success:
            self.db.update_tracking(order_id, tracking_number, datetime.now().strftime('%Y-%m-%d'))
        
        return success, error
    
    def send_followup(self, order_id: str, customer_name: str,
                      customer_email: str) -> Tuple[bool, str]:
        """Send delivery follow-up email"""
        
        if self.db.was_sent(order_id, 'followup'):
            return False, "Email already sent"
        
        email_config = self._load_template('followup')
        template = self.templates.get(email_config['template'])
        
        html = template.render(
            ORDER_NUMBER=order_id,
            CUSTOMER_NAME=customer_name,
            REVIEW_URL='https://redwand.io/review'
        )
        
        success, error = self.sender.send(customer_email, email_config['subject'], html)
        
        status = 'sent' if success else 'failed'
        self.db.log_email(order_id, 'followup', customer_email, status, error)
        
        return success, error
    
    def send_payment_failed(self, order_id: str, customer_name: str,
                           customer_email: str, error_reason: str) -> Tuple[bool, str]:
        """Send payment failed notification"""
        
        if self.db.was_sent(order_id, 'payment_failed'):
            return False, "Email already sent"
        
        email_config = self._load_template('payment_failed')
        template = self.templates.get(email_config['template'])
        
        subject = email_config['subject'].format(order_number=order_id)
        
        html = template.render(
            ORDER_NUMBER=order_id,
            ERROR_REASON=error_reason,
            CUSTOMER_NAME=customer_name,
            CUSTOMER_EMAIL=customer_email,
            RETRY_PAYMENT_URL=f'https://redwand.io/payment-retry?order={order_id}'
        )
        
        success, error = self.sender.send(customer_email, subject, html)
        
        status = 'sent' if success else 'failed'
        self.db.log_email(order_id, 'payment_failed', customer_email, status, error)
        
        return success, error
    
    def process_batch(self) -> Dict[str, int]:
        """Process scheduled emails based on timing"""
        results = {'sent': 0, 'failed': 0, 'skipped': 0}
        
        orders = self.db.get_pending_orders()
        today = datetime.now()
        
        for order in orders:
            order_id = order['order_id']
            customer_name = order['customer_name']
            customer_email = order['customer_email']
            order_date = datetime.strptime(order['order_date'], '%Y-%m-%d')
            days_since_order = (today - order_date).days
            
            # Build progress (Day 5)
            if days_since_order >= 5 and not self.db.was_sent(order_id, 'build_progress'):
                success, _ = self.send_build_progress(order_id, customer_name, customer_email, order['order_date'])
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
            
            # Shipped (Day 8-10)
            elif 8 <= days_since_order <= 10 and order.get('tracking_number') and not self.db.was_sent(order_id, 'shipped'):
                success, _ = self.send_shipped(
                    order_id, customer_name, customer_email,
                    order['tracking_number'], order['order_date']
                )
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
            
            # Follow-up (Day 12-15)
            elif 12 <= days_since_order <= 15 and not self.db.was_sent(order_id, 'followup'):
                success, _ = self.send_followup(order_id, customer_name, customer_email)
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
            
            else:
                results['skipped'] += 1
        
        return results


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Command-line interface"""
    
    if len(sys.argv) < 2:
        print("RedWand Email System")
        print("Usage: python email-system.py <command> [options]")
        print("\nCommands:")
        print("  send-confirmation   <order_id> <name> <email> <date> <amount>")
        print("  send-build          <order_id> <name> <email> <date>")
        print("  send-shipped        <order_id> <name> <email> <tracking> <date>")
        print("  send-followup       <order_id> <name> <email>")
        print("  send-payment-failed <order_id> <name> <email> <reason>")
        print("  batch               Process all scheduled emails")
        print("  test                Send test email")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    email_system = RedWandEmailSystem()
    
    try:
        if command == 'send-confirmation':
            _, order_id, name, email, date, amount = sys.argv
            success, error = email_system.send_order_confirmation(
                order_id, name, email, date, float(amount)
            )
            print(f"Order confirmation: {'Sent' if success else error}")
        
        elif command == 'send-build':
            _, order_id, name, email, date = sys.argv
            success, error = email_system.send_build_progress(order_id, name, email, date)
            print(f"Build progress: {'Sent' if success else error}")
        
        elif command == 'send-shipped':
            _, order_id, name, email, tracking, date = sys.argv
            success, error = email_system.send_shipped(order_id, name, email, tracking, date)
            print(f"Shipped notification: {'Sent' if success else error}")
        
        elif command == 'send-followup':
            _, order_id, name, email = sys.argv
            success, error = email_system.send_followup(order_id, name, email)
            print(f"Follow-up: {'Sent' if success else error}")
        
        elif command == 'send-payment-failed':
            _, order_id, name, email, reason = sys.argv
            success, error = email_system.send_payment_failed(order_id, name, email, reason)
            print(f"Payment failed: {'Sent' if success else error}")
        
        elif command == 'batch':
            results = email_system.process_batch()
            print(f"Batch processed: {results['sent']} sent, {results['failed']} failed, {results['skipped']} skipped")
        
        elif command == 'test':
            success, error = email_system.sender.send(
                'test@redwand.io',
                'Test Email from RedWand',
                '<h1>Test</h1><p>If you received this, the email system is working!</p>'
            )
            print(f"Test email: {'Sent' if success else error}")
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()