#!/usr/bin/env python3
"""
Hacker Warehouse Ordering Script for RedWand Flipper Kit
===========================================================
Checks stock, calculates shipping, and generates order summaries
for Hacker Warehouse (backup supplier).

Usage:
    python hacker-warehouse-order.py check        # Check Flipper Zero stock
    python hacker-warehouse-order.py summary      # Generate full order summary
    python hacker-warehouse-order.py order       # Generate order link/url

Requirements:
    pip install requests beautifulsoup4
"""

import argparse
import json
import logging
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

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
logger = logging.getLogger("hacker_warehouse_order")

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
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE,
            supplier TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT,
            quantity INTEGER DEFAULT 1,
            unit_price REAL,
            total_price REAL,
            shipping_cost REAL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            received_at TIMESTAMP
        )
    """)
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
    conn.commit()
    return conn


# ─────────────────────────────────────────────
# STOCK CHECKING
# ─────────────────────────────────────────────

def check_flipper_zero_stock() -> dict:
    """
    Check Hacker Warehouse stock for Flipper Zero.
    Uses their public website to scrape availability.
    """
    result = {
        "supplier": "hacker_warehouse",
        "product_sku": config.PRODUCTS["flipper_zero"]["sku"],
        "product_name": config.PRODUCTS["flipper_zero"]["name"],
        "price": config.PRODUCTS["flipper_zero"]["price"],
        "stock_status": config.STOCK_STATUS["UNKNOWN"],
        "quantity": None,
        "backorder": False,
        "alert": None,
        "checked_at": datetime.now().isoformat(),
    }
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = config.SUPPLIERS["hacker_warehouse"]["stock_check_url"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for common stock indicators
            page_text = soup.get_text().lower()
            
            # Check for out of stock indicators
            out_of_stock_indicators = [
                "out of stock",
                "sold out",
                "backordered",
                "notify me",
                "out of stock -",
            ]
            
            in_stock_indicators = [
                "add to cart",
                "in stock",
                "available",
            ]
            
            # Check for backorder notice
            if any(ind in page_text for ind in ["backordered", "backorder", "estimated"]):
                result["backorder"] = True
                result["stock_status"] = config.STOCK_STATUS["BACKORDERED"]
                result["alert"] = "Item is on backorder - no current ETA"
            elif any(ind in page_text for ind in out_of_stock_indicators):
                result["stock_status"] = config.STOCK_STATUS["OUT_OF_STOCK"]
                result["alert"] = "Item currently out of stock"
            elif any(ind in page_text for ind in in_stock_indicators):
                result["stock_status"] = config.STOCK_STATUS["IN_STOCK"]
            else:
                # Try to find price to confirm product page loaded
                price_elem = soup.find("span", class_=["price", "product-price", "sale-price"])
                if price_elem:
                    result["stock_status"] = config.STOCK_STATUS["IN_STOCK"]
                else:
                    result["alert"] = "Could not determine stock status"
        else:
            result["alert"] = f"HTTP {response.status_code}"
            logger.warning(f"Hacker Warehouse returned HTTP {response.status_code}")
        
    except ImportError:
        result["alert"] = "beautifulsoup4 not installed - run: pip install beautifulsoup4"
        logger.warning("beautifulsoup4 not available for stock check")
    except Exception as e:
        result["alert"] = str(e)
        logger.error(f"Error checking Hacker Warehouse stock: {e}")
    
    # Log to database
    try:
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO stock_checks 
               (supplier, store_id, product_sku, stock_status, quantity)
               VALUES (?, ?, ?, ?, ?)""",
            ("hacker_warehouse", None, result["product_sku"],
             result["stock_status"], result.get("quantity"))
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log stock check: {e}")
    
    return result


# ─────────────────────────────────────────────
# SHIPPING CALCULATION
# ─────────────────────────────────────────────

def calculate_shipping(item_count: int = 1, supplier: str = "hacker_warehouse") -> dict:
    """
    Calculate shipping costs for an order.
    
    Hacker Warehouse shipping (typical):
    - Base rate: $8.95
    - Per item: $1.50
    - Total = base + (items * per_item)
    """
    supplier_config = config.SUPPLIERS[supplier]
    
    base = supplier_config.get("shipping_base", 8.95)
    per_item = supplier_config.get("shipping_per_item", 1.50)
    
    # Calculate based on item count
    # Flipper Zero is the main item - typically ships alone in a small box
    shipping_cost = base + (per_item * item_count)
    
    # Flat rate options sometimes available
    flat_options = [
        {"name": "Standard", "cost": shipping_cost, "days": "5-7 business days"},
        {"name": "Priority", "cost": shipping_cost + 5.00, "days": "2-3 business days"},
        {"name": "Express", "cost": shipping_cost + 15.00, "days": "1-2 business days"},
    ]
    
    return {
        "supplier": supplier,
        "item_count": item_count,
        "options": flat_options,
        "default": flat_options[0],
        "calculated_at": datetime.now().isoformat(),
    }


# ─────────────────────────────────────────────
# ORDER SUMMARY
# ─────────────────────────────────────────────

def generate_order_summary(quantity: int = 1, supplier: str = "hacker_warehouse") -> dict:
    """
    Generate a complete order summary for Hacker Warehouse.
    Includes stock check, shipping calculation, and total cost.
    """
    summary = {
        "generated_at": datetime.now().isoformat(),
        "supplier": config.SUPPLIERS[supplier]["name"],
        "supplier_website": config.SUPPLIERS[supplier]["website"],
        "order_url": config.SUPPLIERS[supplier]["order_url"],
        "items": [],
        "stock_check": None,
        "shipping": None,
        "subtotal": 0.0,
        "shipping_cost": 0.0,
        "tax_estimate": 0.0,
        "total_estimate": 0.0,
        "can_order": False,
        "warnings": [],
        "order_ready": False,
    }
    
    # Check stock
    logger.info("Checking Hacker Warehouse stock...")
    stock = check_flipper_zero_stock()
    summary["stock_check"] = stock
    
    if stock["stock_status"] == config.STOCK_STATUS["IN_STOCK"]:
        summary["can_order"] = True
    elif stock["stock_status"] == config.STOCK_STATUS["BACKORDERED"]:
        summary["can_order"] = False
        summary["warnings"].append(f"⚠️  {stock.get('alert', 'Item on backorder')}")
    else:
        summary["can_order"] = False
        if stock.get("alert"):
            summary["warnings"].append(f"⚠️  {stock['alert']}")
    
    # Add item
    product = config.PRODUCTS["flipper_zero"]
    item_total = product["price"] * quantity
    summary["items"].append({
        "name": product["name"],
        "sku": product["sku"],
        "price": product["price"],
        "quantity": quantity,
        "line_total": item_total,
    })
    summary["subtotal"] = item_total
    
    # Calculate shipping
    shipping = calculate_shipping(item_count=quantity, supplier=supplier)
    summary["shipping"] = shipping
    summary["shipping_cost"] = shipping["default"]["cost"]
    
    # Totals
    summary["tax_estimate"] = summary["subtotal"] * 0.0825
    summary["total_estimate"] = summary["subtotal"] + summary["shipping_cost"] + summary["tax_estimate"]
    
    summary["order_ready"] = summary["can_order"]
    
    return summary


def print_order_summary(summary: dict):
    """Pretty print an order summary."""
    print("\n" + "=" * 60)
    print("📦 HACKER WAREHOUSE - ORDER SUMMARY")
    print("=" * 60)
    print(f"Generated: {summary['generated_at']}")
    print(f"Supplier: {summary['supplier']}")
    print(f"Website: {summary['supplier_website']}")
    print()
    
    # Stock status
    stock = summary["stock_check"]
    status_icon = "✅" if stock["stock_status"] == config.STOCK_STATUS["IN_STOCK"] else "⚠️" if stock["stock_status"] == config.STOCK_STATUS["BACKORDERED"] else "❌"
    print(f"  {status_icon} Stock Status: {stock['stock_status']}")
    if stock.get("alert"):
        print(f"     {stock['alert']}")
    print()
    
    # Items
    print("  ITEMS:")
    for item in summary["items"]:
        print(f"    • {item['name']}")
        print(f"      SKU: {item['sku']}")
        print(f"      ${item['price']:.2f} x {item['quantity']} = ${item['line_total']:.2f}")
    print()
    
    # Shipping
    print("  SHIPPING OPTIONS:")
    for opt in summary["shipping"]["options"]:
        print(f"    • {opt['name']}: ${opt['cost']:.2f} ({opt['days']})")
    print()
    
    # Totals
    print("-" * 40)
    print(f"  Subtotal:        ${summary['subtotal']:.2f}")
    print(f"  Shipping:        ${summary['shipping_cost']:.2f}")
    print(f"  Tax (est. 8.25%): ${summary['tax_estimate']:.2f}")
    print(f"  TOTAL:           ${summary['total_estimate']:.2f}")
    print("=" * 60)
    
    if summary["order_ready"]:
        print("✅ READY TO ORDER")
        print(f"   Order URL: {summary['order_url']}")
    else:
        print("❌ CANNOT ORDER - CHECK STOCK")
        for warning in summary["warnings"]:
            print(f"   {warning}")
    
    print()


# ─────────────────────────────────────────────
# ORDER RECORD
# ─────────────────────────────────────────────

def create_order_record(summary: dict) -> str:
    """Create an order record in the database."""
    conn = get_db_connection()
    order_number = f"HW-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    for item in summary.get("items", []):
        conn.execute(
            """INSERT INTO orders 
               (order_number, supplier, product_sku, product_name, quantity,
                unit_price, total_price, shipping_cost, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                order_number,
                "hacker_warehouse",
                item["sku"],
                item["name"],
                item["quantity"],
                item["price"],
                item["line_total"],
                summary.get("shipping_cost", 0),
                config.ORDER_STATUS["PENDING"],
            )
        )
    
    conn.commit()
    logger.info(f"Created Hacker Warehouse order record: {order_number}")
    return order_number


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def cmd_check(args):
    """Check stock at Hacker Warehouse."""
    print("\n🔍 Checking Hacker Warehouse stock...\n")
    
    result = check_flipper_zero_stock()
    
    status_icon = "✅" if result["stock_status"] == config.STOCK_STATUS["IN_STOCK"] else "⚠️" if result["stock_status"] == config.STOCK_STATUS["BACKORDERED"] else "❌"
    
    print(f"  {status_icon} Status: {result['stock_status']}")
    print(f"     Product: {result['product_name']}")
    print(f"     SKU: {result['product_sku']}")
    print(f"     Price: ${result['price']:.2f}")
    
    if result.get("alert"):
        print(f"     Note: {result['alert']}")
    
    if result.get("backorder"):
        print(f"     ⚠️  BACKORDERED - No current ETA")
    
    print()


def cmd_summary(args):
    """Generate and print order summary."""
    print("\n📋 Generating Hacker Warehouse order summary...\n")
    
    qty = args.quantity or 1
    supplier = args.supplier or "hacker_warehouse"
    
    summary = generate_order_summary(quantity=qty, supplier=supplier)
    print_order_summary(summary)
    
    if args.save:
        save_path = Path(args.save)
        save_path.write_text(json.dumps(summary, indent=2))
        print(f"💾 Summary saved to: {save_path}")


def cmd_order(args):
    """Generate order (creates record, prints order link)."""
    print("\n🌐 Preparing Hacker Warehouse order...\n")
    
    qty = args.quantity or 1
    summary = generate_order_summary(quantity=qty)
    
    if summary["order_ready"]:
        order_number = create_order_record(summary)
        print(f"✅ Order ready! Record created: {order_number}")
        print(f"   Place order at: {summary['order_url']}")
        print()
        print_order_summary(summary)
    else:
        print("❌ Cannot create order - item not available")
        print(f"   Stock status: {summary['stock_check']['stock_status']}")
        if summary['stock_check'].get('alert'):
            print(f"   Note: {summary['stock_check']['alert']}")


def main():
    parser = argparse.ArgumentParser(
        description="Hacker Warehouse ordering automation for RedWand Flipper Kit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hacker-warehouse-order.py check         # Check Flipper Zero stock
  python hacker-warehouse-order.py summary       # Generate order summary
  python hacker-warehouse-order.py summary --quantity 3  # 3 kits
  python hacker-warehouse-order.py order        # Create order record
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    check_parser = subparsers.add_parser("check", help="Check Flipper Zero stock")
    
    summary_parser = subparsers.add_parser("summary", help="Generate order summary")
    summary_parser.add_argument("--quantity", "-q", type=int, default=1,
                                help="Number of kits (default: 1)")
    summary_parser.add_argument("--supplier", "-s", 
                               choices=["hacker_warehouse", "lab401"],
                               default="hacker_warehouse",
                               help="Supplier (default: hacker_warehouse)")
    summary_parser.add_argument("--save", help="Save summary to file")
    
    order_parser = subparsers.add_parser("order", help="Create order record")
    order_parser.add_argument("--quantity", "-q", type=int, default=1,
                              help="Number of kits (default: 1)")
    
    args = parser.parse_args()
    
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database init failed: {e}")
    
    if args.command == "check":
        cmd_check(args)
    elif args.command == "summary":
        cmd_summary(args)
    elif args.command == "order":
        cmd_order(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
