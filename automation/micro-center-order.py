#!/usr/bin/env python3
"""
Micro Center Ordering Script for RedWand Flipper Kit
=======================================================
Checks stock, generates shopping lists, and automates Micro Center orders.

Usage:
    python micro-center-order.py check          # Check stock at stores
    python micro-center-order.py list            # Generate shopping list
    python micro-center-order.py reserve        # Attempt to reserve items
    python micro-center-order.py order          # Attempt online order
    python micro-center-order.py status          # Check order status

Requirements:
    pip install requests beautifulsoup4 selenium webdriver-manager
    (also needs Chrome/Chromium installed for browser automation)
"""

import argparse
import json
import logging
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path

# Add parent dir to path for shared config
sys.path.insert(0, str(Path(__file__).parent))
import config

# ─────────────────────────────────────────────
# LOGGING SETUP
# ─────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_PATH),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("micro_center_order")

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DB_PATH = Path(__file__).parent.parent / config.DB_PATH


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
            status TEXT DEFAULT 'pending',
            store_id TEXT,
            store_name TEXT,
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

def check_store_stock(product_sku: str, store_id: str) -> dict:
    """
    Check stock for a product at a specific Micro Center store.
    Uses Micro Center's public inventory API endpoint.
    
    Returns dict with stock status and quantity.
    """
    # Micro Center has a JSON API for store inventory
    base_url = f"https://www.microcenter.com/api/v1/stores/{store_id}/products/{product_sku}/inventory"
    
    try:
        import requests
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": config.STOCK_STATUS["IN_STOCK"] if data.get("inStock") else config.STOCK_STATUS["OUT_OF_STOCK"],
                "quantity": data.get("quantity", 0),
                "store_id": store_id,
                "product_sku": product_sku,
                "checked_at": datetime.now().isoformat(),
            }
        else:
            logger.warning(f"Stock check failed for {product_sku} at {store_id}: HTTP {response.status_code}")
            return {
                "status": config.STOCK_STATUS["UNKNOWN"],
                "quantity": None,
                "store_id": store_id,
                "product_sku": product_sku,
                "checked_at": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Error checking stock for {product_sku} at {store_id}: {e}")
        return {
            "status": config.STOCK_STATUS["UNKNOWN"],
            "quantity": None,
            "store_id": store_id,
            "product_sku": product_sku,
            "error": str(e),
            "checked_at": datetime.now().isoformat(),
        }


def check_all_stores(product_sku: str) -> dict:
    """Check stock at all configured Micro Center stores."""
    results = {}
    for store in config.SUPPLIERS["micro_center"]["store_locations"]:
        store_id = store["id"]
        results[store_id] = check_store_stock(product_sku, store_id)
        
        # Log to database
        conn = get_db_connection()
        conn.execute(
            """INSERT INTO stock_checks 
               (supplier, store_id, product_sku, stock_status, quantity)
               VALUES (?, ?, ?, ?, ?)""",
            ("micro_center", store_id, product_sku,
             results[store_id]["status"], results[store_id].get("quantity"))
        )
        conn.commit()
        
    return results


def find_available_store(product_sku: str) -> dict:
    """
    Find the nearest store with stock for a product.
    Returns store info and stock details.
    """
    results = check_all_stores(product_sku)
    
    for store in config.SUPPLIERS["micro_center"]["store_locations"]:
        store_result = results.get(store["id"], {})
        if store_result.get("status") == config.STOCK_STATUS["IN_STOCK"]:
            return {
                "store": store,
                "stock": store_result,
                "available": True,
            }
    
    # Check for low stock
    for store in config.SUPPLIERS["micro_center"]["store_locations"]:
        store_result = results.get(store["id"], {})
        if store_result.get("status") == config.STOCK_STATUS["LOW_STOCK"]:
            return {
                "store": store,
                "stock": store_result,
                "available": False,
                "low_stock": True,
            }
    
    return {"available": False, "results": results}


# ─────────────────────────────────────────────
# SHOPPING LIST GENERATION
# ─────────────────────────────────────────────

def generate_shopping_list(quantity: int = 1) -> dict:
    """
    Generate a formatted shopping list for Micro Center pickup.
    Checks stock for all kit components.
    """
    items = []
    unavailable = []
    total = 0.0
    
    product_map = {
        "flipper_zero": config.PRODUCTS["flipper_zero"]["sku"],
        "moto_g_play": config.PRODUCTS["moto_g_play_2026"]["sku"],
        "sd_card": config.PRODUCTS["sd_card_32gb"]["sku"],
    }
    
    for item_key, sku in product_map.items():
        product = [p for k, p in config.PRODUCTS.items() if k == item_key][0]
        store_result = find_available_store(sku)
        
        if store_result.get("available"):
            item_total = product["price"] * quantity
            total += item_total
            items.append({
                "name": product["name"],
                "sku": sku,
                "price": product["price"],
                "qty": quantity,
                "line_total": item_total,
                "store": store_result["store"]["name"],
                "store_address": store_result["store"]["address"],
                "in_stock": True,
            })
        else:
            unavailable.append({
                "name": product["name"],
                "sku": sku,
                "price": product["price"],
                "reason": "out_of_stock" if not store_result.get("low_stock") else "low_stock",
            })
    
    shopping_list = {
        "generated_at": datetime.now().isoformat(),
        "supplier": "Micro Center",
        "pickup_type": "in_store",
        "items": items,
        "unavailable": unavailable,
        "subtotal": total,
        "tax_estimate": total * 0.0825,  # Austin area tax rate
        "total_estimate": total * 1.0825,
        "ready_for_pickup": len(unavailable) == 0,
    }
    
    return shopping_list


def print_shopping_list(shopping_list: dict):
    """Pretty print a shopping list."""
    print("\n" + "=" * 60)
    print("🛒  MICRO CENTER - RedWand FLIPPER KIT SHOPPING LIST")
    print("=" * 60)
    print(f"Generated: {shopping_list['generated_at']}")
    print(f"Pickup Type: {shopping_list['pickup_type'].upper()}")
    print()
    
    for i, item in enumerate(shopping_list["items"], 1):
        print(f"  {i}. {item['name']}")
        print(f"     SKU: {item['sku']}")
        print(f"     Price: ${item['price']:.2f} x {item['qty']} = ${item['line_total']:.2f}")
        print(f"     Store: {item['store']}")
        print(f"     Address: {item['store_address']}")
        print()
    
    if shopping_list["unavailable"]:
        print("⚠️  UNAVAILABLE ITEMS:")
        for item in shopping_list["unavailable"]:
            print(f"  - {item['name']} ({item['sku']}) - {item['reason']}")
        print()
    
    print("-" * 40)
    print(f"  Subtotal:    ${shopping_list['subtotal']:.2f}")
    print(f"  Tax (8.25%): ${shopping_list['tax_estimate']:.2f}")
    print(f"  TOTAL:       ${shopping_list['total_estimate']:.2f}")
    print("=" * 60)
    
    if shopping_list["ready_for_pickup"]:
        print("✅ ALL ITEMS READY FOR PICKUP")
    else:
        print("❌ SOME ITEMS UNAVAILABLE - CANNOT PROCEED")
    
    print()


# ─────────────────────────────────────────────
# ORDER PLACEMENT
# ─────────────────────────────────────────────

def create_order_record(shopping_list: dict, store_id: str) -> str:
    """Create order records in the database for tracking."""
    conn = get_db_connection()
    order_number = f"MC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    for item in shopping_list.get("items", []):
        conn.execute(
            """INSERT INTO orders 
               (order_number, supplier, product_sku, product_name, quantity,
                unit_price, total_price, status, store_id, store_name)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                order_number,
                "micro_center",
                item["sku"],
                item["name"],
                item["qty"],
                item["price"],
                item["line_total"],
                config.ORDER_STATUS["PENDING"],
                store_id,
                item["store"],
            )
        )
    
    conn.commit()
    logger.info(f"Created order record: {order_number}")
    return order_number


def update_order_status(order_number: str, status: str, notes: str = ""):
    """Update the status of an order."""
    conn = get_db_connection()
    conn.execute(
        """UPDATE orders SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
           WHERE order_number = ?""",
        (status, notes, order_number)
    )
    conn.commit()
    logger.info(f"Order {order_number} status updated to: {status}")


# ─────────────────────────────────────────────
# BROWSER AUTOMATION (for online ordering)
# ─────────────────────────────────────────────

def order_online(headless: bool = True) -> dict:
    """
    Attempt to place an online order via browser automation.
    Requires Chrome/Chromium and webdriver-manager.
    
    NOTE: This is a template - Micro Center's site requires
    authentication and has anti-bot measures. Review carefully
    before use.
    """
    result = {
        "success": False,
        "order_number": None,
        "error": None,
    }
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Navigate to Micro Center
        logger.info("Opening Micro Center website...")
        driver.get("https://www.microcenter.com")
        
        # NOTE: Actual form filling would go here
        # Micro Center requires login for online orders
        # and has anti-bot detection. This is a template.
        
        result["error"] = "Online ordering requires manual login - see browser"
        logger.warning("Online order attempted - manual review required")
        
        driver.quit()
        
    except ImportError as e:
        result["error"] = f"Missing dependency: {e}. Run: pip install selenium webdriver-manager"
        logger.error(result["error"])
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Online order failed: {e}")
    
    return result


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def cmd_check(args):
    """Check stock at all stores."""
    print("\n🔍 Checking Micro Center stock...\n")
    
    product = args.product or "flipper_zero"
    sku = config.PRODUCTS[product]["sku"]
    
    print(f"Product: {config.PRODUCTS[product]['name']} ({sku})\n")
    
    for store in config.SUPPLIERS["micro_center"]["store_locations"]:
        result = check_store_stock(sku, store["id"])
        status_icon = "✅" if result["status"] == config.STOCK_STATUS["IN_STOCK"] else "⚠️" if result["status"] == config.STOCK_STATUS["LOW_STOCK"] else "❌"
        qty = result.get("quantity", "N/A")
        print(f"  {status_icon} {store['name']}: {result['status']} (qty: {qty})")
    
    print()


def cmd_list(args):
    """Generate and print shopping list."""
    print("\n📋 Generating Micro Center shopping list...\n")
    qty = args.quantity or 1
    shopping_list = generate_shopping_list(quantity=qty)
    print_shopping_list(shopping_list)
    
    if args.save:
        save_path = Path(args.save)
        save_path.write_text(json.dumps(shopping_list, indent=2))
        print(f"💾 Shopping list saved to: {save_path}")


def cmd_reserve(args):
    """Attempt to reserve items (placeholder - requires API access)."""
    print("\n📦 Attempting to reserve items...\n")
    print("⚠️  Reservation requires Micro Center partner API access.")
    print("    This feature is a placeholder for when API access is granted.")
    print()
    print("    Alternative: Present this shopping list at the store counter")
    print("    and ask an associate to pull items for you.")
    print()
    
    qty = args.quantity or 1
    shopping_list = generate_shopping_list(quantity=qty)
    
    if shopping_list["ready_for_pickup"]:
        order_number = create_order_record(shopping_list, store_id="preferred")
        update_order_status(order_number, config.ORDER_STATUS["CONFIRMED"], 
                          notes="Reservation pending - in-store pickup required")
        print(f"📝 Order record created: {order_number}")
        print_shopping_list(shopping_list)
    else:
        print("❌ Cannot reserve - some items unavailable")
    
    return shopping_list


def cmd_order(args):
    """Attempt online order via browser automation."""
    print("\n🌐 Attempting online order...\n")
    
    if not args.yes:
        print("⚠️  This will open a browser window. Use --yes to confirm.")
        print("    Press Ctrl+C to cancel.\n")
        input("Press Enter to continue...")
    
    result = order_online(headless=not args.visible)
    
    if result["success"]:
        print(f"✅ Order placed: {result['order_number']}")
    else:
        print(f"❌ Order failed: {result.get('error')}")
        print("\n💡 Try in-store pickup instead:")
        print("   python micro-center-order.py list")


def main():
    parser = argparse.ArgumentParser(
        description="Micro Center ordering automation for RedWand Flipper Kit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python micro-center-order.py check                      # Check Flipper Zero stock
  python micro-center-order.py check --product moto_g_play  # Check Moto G stock
  python micro-center-order.py list                       # Generate shopping list
  python micro-center-order.py list --quantity 3          # List for 3 kits
  python micro-center-order.py reserve                    # Create reservation record
  python micro-center-order.py order --yes                # Attempt online order
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check stock at stores")
    check_parser.add_argument("--product", "-p", 
                              choices=["flipper_zero", "moto_g_play", "sd_card"],
                              default="flipper_zero",
                              help="Product to check (default: flipper_zero)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="Generate shopping list")
    list_parser.add_argument("--quantity", "-q", type=int, default=1,
                            help="Number of kits (default: 1)")
    list_parser.add_argument("--save", "-s", help="Save shopping list to file")
    
    # Reserve command
    reserve_parser = subparsers.add_parser("reserve", help="Create reservation record")
    reserve_parser.add_argument("--quantity", "-q", type=int, default=1,
                                help="Number of kits (default: 1)")
    
    # Order command
    order_parser = subparsers.add_parser("order", help="Attempt online order")
    order_parser.add_argument("--yes", "-y", action="store_true",
                             help="Skip confirmation prompt")
    order_parser.add_argument("--visible", action="store_true",
                             help="Show browser window (don't run headless)")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show order status")
    status_parser.add_argument("--order", "-o", help="Order number (or shows recent)")
    
    args = parser.parse_args()
    
    # Initialize database
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database init failed: {e}")
    
    if args.command == "check":
        cmd_check(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "reserve":
        cmd_reserve(args)
    elif args.command == "order":
        cmd_order(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        parser.print_help()


def cmd_status(args):
    """Show order status from database."""
    conn = get_db_connection()
    
    if args.order:
        rows = conn.execute(
            "SELECT * FROM orders WHERE order_number = ?", (args.order,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 10"
        ).fetchall()
    
    if not rows:
        print("No orders found.")
        return
    
    print("\n📦 ORDER STATUS\n")
    current_order = None
    for row in rows:
        if row["order_number"] != current_order:
            current_order = row["order_number"]
            print(f"Order: {row['order_number']} | Supplier: {row['supplier']}")
            print(f"  Status: {row['status']} | Store: {row['store_name']}")
            print(f"  Created: {row['created_at']}")
            print()
        
        print(f"  - {row['product_name']} x{row['quantity']} @ ${row['unit_price']:.2f}")
    
    print()


if __name__ == "__main__":
    main()
