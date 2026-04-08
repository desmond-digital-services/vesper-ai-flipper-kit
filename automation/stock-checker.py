#!/usr/bin/env python3
"""
Supplier Stock Checker for Vesper AI Flipper Kit
================================================
Monitors stock levels across all suppliers and sends alerts.

Usage:
    python stock-checker.py check             # Check all suppliers
    python stock-checker.py check --supplier micro_center  # Single supplier
    python stock-checker.py monitor           # Continuous monitoring mode
    python stock-checker.py report             # Generate stock report

Scheduling (cron):
    # Check every day at 8am
    0 8 * * * cd /path/to/vesper-ai/automation && python stock-checker.py check --quiet

Requirements:
    pip install requests beautifulsoup4
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
import config

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_PATH),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("stock_checker")

DB_PATH = Path(__file__).parent.parent / config.DB_PATH

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT NOT NULL,
            store_id TEXT,
            product_sku TEXT NOT NULL,
            stock_status TEXT NOT NULL,
            quantity INTEGER,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT,
            alert_type TEXT NOT NULL,
            message TEXT,
            acknowledged BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged_at TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE,
            supplier TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT,
            quantity INTEGER DEFAULT 1,
            unit_price REAL,
            total_price REAL,
            status TEXT DEFAULT 'pending',
            store_id TEXT,
            store_name TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            received_at TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

def send_email_alert(subject: str, body: str, to_addrs: Optional[list] = None):
    """Send an email alert."""
    if not config.NOTIFICATIONS.get("email", {}).get("enabled"):
        logger.info("Email notifications disabled - would send:")
        logger.info(f"  Subject: {subject}")
        logger.info(f"  Body: {body[:200]}...")
        return
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        email_config = config.NOTIFICATIONS["email"]
        
        msg = MIMEMultipart()
        msg["From"] = email_config["from_addr"]
        msg["To"] = ", ".join(to_addrs or email_config["to_addrs"])
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(email_config["smtp_host"], email_config["smtp_port"]) as server:
            server.starttls()
            server.login(email_config["smtp_user"], email_config["smtp_password"])
            server.send_message(msg)
        
        logger.info(f"Email alert sent to {to_addrs or email_config['to_addrs']}")
        
    except Exception as e:
        logger.error(f"Failed to send email alert: {e}")


def send_sms_alert(message: str, to_numbers: Optional[list] = None):
    """Send an SMS alert via Twilio."""
    if not config.NOTIFICATIONS.get("sms", {}).get("enabled"):
        logger.info("SMS notifications disabled - would send:")
        logger.info(f"  Message: {message}")
        return
    
    try:
        from twilio.rest import Client
        
        sms_config = config.NOTIFICATIONS["sms"]
        client = Client(sms_config["twilio_sid"], sms_config["twilio_token"])
        
        numbers = to_numbers or sms_config["to_numbers"]
        
        for number in numbers:
            client.messages.create(
                body=message,
                from_=sms_config["from_number"],
                to=number
            )
        
        logger.info(f"SMS alert sent to {numbers}")
        
    except ImportError:
        logger.error("twilio not installed - run: pip install twilio")
    except Exception as e:
        logger.error(f"Failed to send SMS alert: {e}")


def send_telegram_alert(message: str, chat_ids: Optional[list] = None):
    """Send a Telegram alert."""
    if not config.NOTIFICATIONS.get("telegram", {}).get("enabled"):
        logger.info("Telegram notifications disabled - would send:")
        logger.info(f"  Message: {message}")
        return
    
    try:
        import requests
        
        telegram_config = config.NOTIFICATIONS["telegram"]
        token = telegram_config["bot_token"]
        chat_ids = chat_ids or telegram_config["chat_ids"]
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        for chat_id in chat_ids:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Telegram send failed: {response.text}")
        
        logger.info(f"Telegram alert sent to {len(chat_ids)} chats")
        
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


def send_stock_alert(supplier: str, product_name: str, sku: str, 
                     status: str, quantity: Optional[int] = None):
    """Send stock alert through all configured channels."""
    
    # Determine alert type
    if status == config.STOCK_STATUS["OUT_OF_STOCK"]:
        alert_type = "OUT_OF_STOCK"
        icon = "🔴"
        message = f"{icon} <b>OUT OF STOCK</b>\n\n{supplier.title()}: {product_name} ({sku})\nQuantity: {quantity if quantity else 'Unknown'}"
    elif status == config.STOCK_STATUS["LOW_STOCK"]:
        alert_type = "LOW_STOCK"
        icon = "🟡"
        message = f"{icon} <b>LOW STOCK</b>\n\n{supplier.title()}: {product_name} ({sku})\nQuantity: {quantity if quantity else 'Unknown'}"
    elif status == config.STOCK_STATUS["BACKORDERED"]:
        alert_type = "BACKORDERED"
        icon = "🟠"
        message = f"{icon} <b>BACKORDERED</b>\n\n{supplier.title()}: {product_name} ({sku})\nItem is on backorder"
    else:
        return  # No alert for IN_STOCK
    
    subject = f"[{icon}] Stock Alert: {product_name}"
    
    # Log to database
    try:
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO stock_alerts 
               (supplier, product_sku, product_name, alert_type, message)
               VALUES (?, ?, ?, ?, ?)""",
            (supplier, sku, product_name, alert_type, message)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log stock alert: {e}")
    
    # Send notifications
    send_email_alert(subject, message)
    send_sms_alert(f"Stock Alert: {product_name} at {supplier} - {status}")
    send_telegram_alert(message)


# ─────────────────────────────────────────────
# STOCK CHECKING
# ─────────────────────────────────────────────

def check_micro_center(product_sku: str, store_id: str) -> dict:
    """Check stock at a Micro Center store."""
    result = {
        "supplier": "micro_center",
        "store_id": store_id,
        "product_sku": product_sku,
        "stock_status": config.STOCK_STATUS["UNKNOWN"],
        "quantity": None,
        "checked_at": datetime.now().isoformat(),
    }
    
    try:
        import requests
        
        url = f"https://www.microcenter.com/api/v1/stores/{store_id}/products/{product_sku}/inventory"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            in_stock = data.get("inStock", False)
            qty = data.get("quantity", 0)
            
            if in_stock and qty >= 5:
                result["stock_status"] = config.STOCK_STATUS["IN_STOCK"]
            elif in_stock and qty > 0:
                result["stock_status"] = config.STOCK_STATUS["LOW_STOCK"]
            elif data.get("backordered"):
                result["stock_status"] = config.STOCK_STATUS["BACKORDERED"]
            else:
                result["stock_status"] = config.STOCK_STATUS["OUT_OF_STOCK"]
            
            result["quantity"] = qty
        else:
            logger.warning(f"Micro Center API returned {response.status_code}")
            
    except Exception as e:
        logger.error(f"Micro Center check failed: {e}")
    
    return result


def check_hacker_warehouse(product_sku: str) -> dict:
    """Check stock at Hacker Warehouse."""
    result = {
        "supplier": "hacker_warehouse",
        "store_id": None,
        "product_sku": product_sku,
        "stock_status": config.STOCK_STATUS["UNKNOWN"],
        "quantity": None,
        "checked_at": datetime.now().isoformat(),
    }
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = config.SUPPLIERS["hacker_warehouse"]["stock_check_url"]
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text().lower()
            
            if any(x in page_text for x in ["backordered", "backorder", "estimated"]):
                result["stock_status"] = config.STOCK_STATUS["BACKORDERED"]
            elif any(x in page_text for x in ["out of stock", "sold out", "notify me"]):
                result["stock_status"] = config.STOCK_STATUS["OUT_OF_STOCK"]
            elif any(x in page_text for x in ["add to cart", "in stock", "available"]):
                result["stock_status"] = config.STOCK_STATUS["IN_STOCK"]
                
    except Exception as e:
        logger.error(f"Hacker Warehouse check failed: {e}")
    
    return result


def check_lab401(product_sku: str) -> dict:
    """Check stock at Lab401."""
    result = {
        "supplier": "lab401",
        "store_id": None,
        "product_sku": product_sku,
        "stock_status": config.STOCK_STATUS["UNKNOWN"],
        "quantity": None,
        "checked_at": datetime.now().isoformat(),
    }
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = config.SUPPLIERS["lab401"]["stock_check_url"]
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text().lower()
            
            if any(x in page_text for x in ["backordered", "pre-order", "preorder"]):
                result["stock_status"] = config.STOCK_STATUS["BACKORDERED"]
            elif any(x in page_text for x in ["out of stock", "sold out", "unavailable"]):
                result["stock_status"] = config.STOCK_STATUS["OUT_OF_STOCK"]
            elif any(x in page_text for x in ["add to cart", "in stock", "available", "buy"]):
                result["stock_status"] = config.STOCK_STATUS["IN_STOCK"]
                
    except Exception as e:
        logger.error(f"Lab401 check failed: {e}")
    
    return result


def check_all_suppliers(product_skus: Optional[dict] = None) -> dict:
    """
    Check stock across all configured suppliers.
    
    Args:
        product_skus: Dict mapping product keys to SKUs. 
                      Defaults to flipper_zero only (most critical).
    """
    if product_skus is None:
        product_skus = {"flipper_zero": config.PRODUCTS["flipper_zero"]["sku"]}
    
    results = {
        "checked_at": datetime.now().isoformat(),
        "suppliers": {},
    }
    
    for product_key, sku in product_skus.items():
        product = [p for k, p in config.PRODUCTS.items() if k == product_key][0]
        results["suppliers"][product_key] = {
            "product_name": product["name"],
            "sku": sku,
            "stores": {},
        }
        
        # Micro Center (check all stores)
        mc_stores = config.SUPPLIERS["micro_center"]["store_locations"]
        mc_results = []
        for store in mc_stores:
            r = check_micro_center(sku, store["id"])
            r["store_name"] = store["name"]
            mc_results.append(r)
            
            # Log to database
            log_stock_check(r)
            
            # Alert if needed
            if r["stock_status"] in [config.STOCK_STATUS["OUT_OF_STOCK"],
                                     config.STOCK_STATUS["LOW_STOCK"],
                                     config.STOCK_STATUS["BACKORDERED"]]:
                send_stock_alert("micro_center", product["name"], sku,
                               r["stock_status"], r.get("quantity"))
        
        results["suppliers"][product_key]["stores"]["micro_center"] = mc_results
        
        # Hacker Warehouse
        hw_result = check_hacker_warehouse(sku)
        hw_result["store_name"] = "Online"
        log_stock_check(hw_result)
        
        if hw_result["stock_status"] in [config.STOCK_STATUS["OUT_OF_STOCK"],
                                         config.STOCK_STATUS["BACKORDERED"]]:
            send_stock_alert("hacker_warehouse", product["name"], sku,
                           hw_result["stock_status"])
        
        results["suppliers"][product_key]["stores"]["hacker_warehouse"] = hw_result
        
        # Lab401
        lab_result = check_lab401(sku)
        lab_result["store_name"] = "Online (EU)"
        log_stock_check(lab_result)
        
        if lab_result["stock_status"] in [config.STOCK_STATUS["OUT_OF_STOCK"],
                                          config.STOCK_STATUS["BACKORDERED"]]:
            send_stock_alert("lab401", product["name"], sku,
                            lab_result["stock_status"])
        
        results["suppliers"][product_key]["stores"]["lab401"] = lab_result
    
    return results


def log_stock_check(result: dict):
    """Log a stock check to the database."""
    try:
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO stock_checks 
               (supplier, store_id, product_sku, stock_status, quantity)
               VALUES (?, ?, ?, ?, ?)""",
            (result["supplier"], result.get("store_id"), result["product_sku"],
             result["stock_status"], result.get("quantity"))
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log stock check: {e}")


# ─────────────────────────────────────────────
# REPORTING
# ─────────────────────────────────────────────

def generate_stock_report() -> dict:
    """Generate a comprehensive stock status report."""
    conn = get_db_connection()
    
    # Get latest check for each supplier/product
    report = {
        "generated_at": datetime.now().isoformat(),
        "products": {},
    }
    
    for product_key, product in config.PRODUCTS.items():
        sku = product["sku"]
        
        # Query latest checks per supplier
        rows = conn.execute(
            """SELECT supplier, store_id, stock_status, quantity, checked_at
               FROM stock_checks
               WHERE product_sku = ?
               AND id IN (
                   SELECT MAX(id) FROM stock_checks
                   WHERE product_sku = ?
                   GROUP BY supplier, store_id
               )
               ORDER BY checked_at DESC""",
            (sku, sku)
        ).fetchall()
        
        report["products"][product_key] = {
            "name": product["name"],
            "sku": sku,
            "suppliers": {},
        }
        
        for row in rows:
            report["products"][product_key]["suppliers"][row["supplier"]] = {
                "status": row["stock_status"],
                "quantity": row["quantity"],
                "store_id": row["store_id"],
                "last_checked": row["checked_at"],
            }
    
    return report


def print_stock_report(report: dict):
    """Pretty print a stock report."""
    print("\n" + "=" * 70)
    print("📊 VESPER AI FLIPPER KIT - STOCK STATUS REPORT")
    print(f"Generated: {report['generated_at']}")
    print("=" * 70)
    
    for product_key, product_data in report["products"].items():
        print(f"\n{product_data['name']} ({product_data['sku']})")
        print("-" * 50)
        
        for supplier, data in product_data["suppliers"].items():
            status = data["status"]
            qty = data.get("quantity") or "N/A"
            
            icon = "✅" if status == config.STOCK_STATUS["IN_STOCK"] else \
                   "🟡" if status == config.STOCK_STATUS["LOW_STOCK"] else \
                   "🟠" if status == config.STOCK_STATUS["BACKORDERED"] else \
                   "❌"
            
            location = data.get("store_id") or "Online"
            print(f"  {icon} {supplier.title():20} | {status:15} | qty: {qty} | {location}")
    
    print("\n" + "=" * 70)


# ─────────────────────────────────────────────
# FALLBACK ORDERING
# ─────────────────────────────────────────────

def find_best_supplier(product_key: str) -> dict:
    """
    Find the best available supplier for a product.
    Tries suppliers in preference order.
    """
    product = config.PRODUCTS.get(product_key)
    if not product:
        return {"available": False, "error": "Unknown product"}
    
    for supplier_id in config.PREFERRED_SUPPLIER_ORDER:
        if supplier_id not in product.get("suppliers", []):
            continue
        
        supplier_name = config.SUPPLIERS[supplier_id]["name"]
        
        if supplier_id == "micro_center":
            # Check all stores
            for store in config.SUPPLIERS["micro_center"]["store_locations"]:
                result = check_micro_center(product["sku"], store["id"])
                if result["stock_status"] == config.STOCK_STATUS["IN_STOCK"]:
                    return {
                        "available": True,
                        "supplier_id": supplier_id,
                        "supplier_name": supplier_name,
                        "store_id": store["id"],
                        "store_name": store["name"],
                        "stock_status": result["stock_status"],
                        "quantity": result.get("quantity"),
                        "price": product["price"],
                    }
        
        elif supplier_id == "hacker_warehouse":
            result = check_hacker_warehouse(product["sku"])
            if result["stock_status"] == config.STOCK_STATUS["IN_STOCK"]:
                return {
                    "available": True,
                    "supplier_id": supplier_id,
                    "supplier_name": supplier_name,
                    "url": config.SUPPLIERS[supplier_id]["order_url"],
                    "stock_status": result["stock_status"],
                    "price": product["price"],
                }
        
        elif supplier_id == "lab401":
            result = check_lab401(product["sku"])
            if result["stock_status"] == config.STOCK_STATUS["IN_STOCK"]:
                return {
                    "available": True,
                    "supplier_id": supplier_id,
                    "supplier_name": supplier_name,
                    "url": config.SUPPLIERS[supplier_id]["order_url"],
                    "stock_status": result["stock_status"],
                    "price": product["price"],
                }
    
    return {"available": False, "error": "No suppliers have this item in stock"}


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def cmd_check(args):
    """Check stock at all or specified suppliers."""
    print("\n🔍 Checking stock across all suppliers...\n")
    
    if args.supplier:
        print(f"Checking: {args.supplier}\n")
    
    # Build product SKUs to check
    if args.supplier == "micro_center":
        product_skus = {"flipper_zero": config.PRODUCTS["flipper_zero"]["sku"]}
    elif args.supplier == "hacker_warehouse":
        product_skus = {"flipper_zero": config.PRODUCTS["flipper_zero"]["sku"]}
    elif args.supplier == "lab401":
        product_skus = {"flipper_zero": config.PRODUCTS["flipper_zero"]["sku"]}
    else:
        product_skus = {k: v["sku"] for k, v in config.PRODUCTS.items()}
    
    results = check_all_suppliers(product_skus)
    
    if not args.quiet:
        print_stock_report(generate_stock_report())
    
    # Summary output
    alerts = []
    for product_key, supplier_data in results["suppliers"].items():
        for supplier, data in supplier_data["stores"].items():
            if isinstance(data, list):
                for store_data in data:
                    if store_data["stock_status"] != config.STOCK_STATUS["IN_STOCK"]:
                        alerts.append(f"{supplier}/{store_data.get('store_name', 'unknown')}: {store_data['stock_status']}")
            else:
                if data["stock_status"] != config.STOCK_STATUS["IN_STOCK"]:
                    alerts.append(f"{supplier}: {data['stock_status']}")
    
    if alerts:
        print(f"\n⚠️  {len(alerts)} stock issue(s) found - alerts sent")
    else:
        print("\n✅ All items in stock")
    
    return results


def cmd_monitor(args):
    """Continuous monitoring mode."""
    print("\n📡 Starting continuous stock monitoring...")
    print(f"   Check interval: {args.interval} seconds")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        while True:
            cmd_check(type("Args", (), {"supplier": None, "quiet": True})())
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def cmd_report(args):
    """Generate and display a stock report."""
    print("\n📋 Generating stock report...\n")
    
    report = generate_stock_report()
    print_stock_report(report)
    
    if args.save:
        save_path = Path(args.save)
        save_path.write_text(json.dumps(report, indent=2))
        print(f"\n💾 Report saved to: {save_path}")


def cmd_find_supplier(args):
    """Find best available supplier for a product."""
    print(f"\n🔎 Finding best supplier for {args.product}...\n")
    
    result = find_best_supplier(args.product)
    
    if result["available"]:
        print(f"✅ Best supplier: {result['supplier_name']}")
        print(f"   Price: ${result['price']:.2f}")
        print(f"   Stock: {result['stock_status']}")
        if result.get("store_name"):
            print(f"   Location: {result['store_name']}")
        if result.get("url"):
            print(f"   Order: {result['url']}")
    else:
        print(f"❌ {result.get('error', 'No available supplier')}")


def main():
    parser = argparse.ArgumentParser(
        description="Stock checker for Vesper AI Flipper Kit suppliers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stock-checker.py check              # Check all suppliers
  python stock-checker.py check --supplier micro_center  # Micro Center only
  python stock-checker.py check --quiet      # Minimal output (good for cron)
  python stock-checker.py monitor            # Continuous monitoring
  python stock-checker.py monitor --interval 3600  # Check every hour
  python stock-checker.py report             # Generate full report
  python stock-checker.py report --save report.json  # Save report
  python stock-checker.py find flipper_zero  # Find best supplier
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    check_parser = subparsers.add_parser("check", help="Check stock at suppliers")
    check_parser.add_argument("--supplier", "-s",
                             choices=["micro_center", "hacker_warehouse", "lab401"],
                             help="Specific supplier to check")
    check_parser.add_argument("--quiet", "-q", action="store_true",
                             help="Minimal output")
    
    monitor_parser = subparsers.add_parser("monitor", help="Continuous monitoring")
    monitor_parser.add_argument("--interval", "-i", type=int, default=3600,
                               help="Check interval in seconds (default: 3600)")
    
    report_parser = subparsers.add_parser("report", help="Generate stock report")
    report_parser.add_argument("--save", "-s", help="Save report to file")
    
    find_parser = subparsers.add_parser("find", help="Find best available supplier")
    find_parser.add_argument("product", choices=list(config.PRODUCTS.keys()),
                             help="Product to find supplier for")
    
    args = parser.parse_args()
    
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database init failed: {e}")
    
    if args.command == "check":
        cmd_check(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "find":
        cmd_find_supplier(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
