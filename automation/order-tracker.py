#!/usr/bin/env python3
"""
Order Tracker for RedWand Flipper Kit
=======================================
Tracks procurement orders across suppliers, updates status,
and calculates cost variance.

Usage:
    python order-tracker.py list              # List all orders
    python order-tracker.py show ORD-001      # Show order details
    python order-tracker.py status ORD-001    # Update order status
    python order-tracker.py received ORD-001  # Mark items received
    python order-tracker.py costs              # Cost variance report
    python order-tracker.py summary           # Procurement summary

Requirements:
    pip install tabulate
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime
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
logger = logging.getLogger("order_tracker")

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
            shipping_cost REAL DEFAULT 0,
            status TEXT DEFAULT 'pending',
            store_id TEXT,
            store_name TEXT,
            tracking_number TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            received_at TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
# ORDER OPERATIONS
# ─────────────────────────────────────────────

def get_order(order_number: str) -> Optional[dict]:
    """Get order details by order number."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM orders WHERE order_number = ?", (order_number,)
    ).fetchall()
    
    if not rows:
        return None
    
    order = dict(rows[0])
    order["items"] = [dict(row) for row in rows]
    return order


def get_all_orders(status: Optional[str] = None, 
                   supplier: Optional[str] = None) -> list:
    """Get all orders with optional filters."""
    conn = get_db_connection()
    
    query = "SELECT * FROM orders WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    if supplier:
        query += " AND supplier = ?"
        params.append(supplier)
    
    query += " ORDER BY created_at DESC"
    
    rows = conn.execute(query, params).fetchall()
    
    # Group by order number
    orders = {}
    for row in rows:
        order_num = row["order_number"]
        if order_num not in orders:
            orders[order_num] = {
                "order_number": order_num,
                "supplier": row["supplier"],
                "status": row["status"],
                "store_name": row["store_name"],
                "created_at": row["created_at"],
                "items": [],
            }
        orders[order_num]["items"].append(dict(row))
    
    return list(orders.values())


def create_order(order_number: str, supplier: str, items: list,
                 store_id: str = None, store_name: str = None,
                 shipping_cost: float = 0.0, notes: str = "") -> str:
    """Create a new order record."""
    conn = get_db_connection()
    
    for item in items:
        conn.execute(
            """INSERT INTO orders 
               (order_number, supplier, product_sku, product_name, quantity,
                unit_price, total_price, shipping_cost, status, store_id, store_name, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                order_number,
                supplier,
                item["sku"],
                item.get("name", ""),
                item.get("quantity", 1),
                item.get("price", 0),
                item.get("line_total", item.get("price", 0) * item.get("quantity", 1)),
                shipping_cost,
                config.ORDER_STATUS["PENDING"],
                store_id,
                store_name,
                notes,
            )
        )
    
    conn.commit()
    log_order_event(order_number, "created", {"supplier": supplier, "items": len(items)})
    logger.info(f"Created order: {order_number}")
    return order_number


def update_order_status(order_number: str, new_status: str, 
                        tracking_number: str = None, notes: str = None):
    """Update the status of an order."""
    conn = get_db_connection()
    
    update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
    params = [new_status]
    
    if tracking_number:
        update_fields.append("tracking_number = ?")
        params.append(tracking_number)
    
    if notes:
        update_fields.append("notes = ?")
        params.append(notes)
    
    params.append(order_number)
    
    conn.execute(
        f"UPDATE orders SET {', '.join(update_fields)} WHERE order_number = ?",
        params
    )
    conn.commit()
    
    log_order_event(order_number, "status_changed", {"new_status": new_status})
    logger.info(f"Order {order_number} status updated to: {new_status}")


def mark_order_received(order_number: str, notes: str = ""):
    """Mark an order as received."""
    conn = get_db_connection()
    
    conn.execute(
        """UPDATE orders 
           SET status = ?, received_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP,
               notes = COALESCE(notes || ' | ', '') || ?
           WHERE order_number = ?""",
        (config.ORDER_STATUS["DELIVERED"], notes, order_number)
    )
    conn.commit()
    
    log_order_event(order_number, "received", {"notes": notes})
    logger.info(f"Order {order_number} marked as received")


def log_order_event(order_number: str, event_type: str, event_data: dict = None):
    """Log an event for an order."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO order_events (order_number, event_type, event_data) VALUES (?, ?, ?)",
        (order_number, event_type, json.dumps(event_data) if event_data else None)
    )
    conn.commit()


def get_order_events(order_number: str) -> list:
    """Get event history for an order."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM order_events WHERE order_number = ? ORDER BY created_at ASC",
        (order_number,)
    ).fetchall()
    return [dict(row) for row in rows]


# ─────────────────────────────────────────────
# COST TRACKING
# ─────────────────────────────────────────────

def calculate_actual_vs_estimated() -> dict:
    """
    Compare actual costs to estimated costs for all orders.
    """
    conn = get_db_connection()
    
    # Get all received orders
    rows = conn.execute(
        """SELECT supplier, product_sku, product_name, 
                  SUM(quantity) as total_qty,
                  SUM(total_price) as actual_cost,
                  SUM(shipping_cost) as actual_shipping
           FROM orders
           WHERE status = 'delivered'
           GROUP BY supplier, product_sku""",
    ).fetchall()
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "products": {},
        "totals": {
            "estimated_cost": 0.0,
            "actual_cost": 0.0,
            "variance": 0.0,
        }
    }
    
    for row in rows:
        sku = row["product_sku"]
        qty = row["total_qty"]
        
        # Find estimated price
        estimated_unit = 0.0
        for product_key, product in config.PRODUCTS.items():
            if product["sku"] == sku:
                estimated_unit = product["price"]
                break
        
        estimated_total = estimated_unit * qty
        actual_cost = row["actual_cost"] or 0.0
        variance = actual_cost - estimated_total
        
        report["products"][sku] = {
            "name": row["product_name"],
            "sku": sku,
            "supplier": row["supplier"],
            "quantity": qty,
            "estimated_unit_price": estimated_unit,
            "actual_unit_price": actual_cost / qty if qty > 0 else 0,
            "estimated_total": estimated_total,
            "actual_cost": actual_cost,
            "actual_shipping": row["actual_shipping"] or 0.0,
            "variance": variance,
        }
        
        report["totals"]["estimated_cost"] += estimated_total
        report["totals"]["actual_cost"] += actual_cost
        report["totals"]["variance"] += variance
    
    return report


# ─────────────────────────────────────────────
# FORMATTING
# ─────────────────────────────────────────────

def format_currency(amount: float) -> str:
    return f"${amount:.2f}"


def format_status(status: str) -> str:
    icons = {
        "pending": "⏳",
        "confirmed": "✅",
        "ready_for_pickup": "🏪",
        "shipped": "🚚",
        "delivered": "📦",
        "cancelled": "❌",
        "backordered": "🟠",
    }
    return f"{icons.get(status, '⚪')} {status.replace('_', ' ').title()}"


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def cmd_list(args):
    """List all orders."""
    orders = get_all_orders(status=args.status, supplier=args.supplier)
    
    if not orders:
        print("\n📦 No orders found.")
        return
    
    print(f"\n📦 Orders ({len(orders)} total)\n")
    print(f"{'Order #':<22} {'Supplier':<20} {'Status':<25} {'Items':<8} {'Created':<20}")
    print("-" * 100)
    
    for order in orders:
        print(f"{order['order_number']:<22} "
              f"{order['supplier'].replace('_', ' ').title():<20} "
              f"{format_status(order['status']):<25} "
              f"{len(order['items']):<8} "
              f"{order['created_at']:<20}")
    
    print()


def cmd_show(args):
    """Show detailed order information."""
    order = get_order(args.order_number)
    
    if not order:
        print(f"\n❌ Order {args.order_number} not found.")
        return
    
    events = get_order_events(args.order_number)
    
    print("\n" + "=" * 60)
    print(f"📦 ORDER: {order['order_number']}")
    print("=" * 60)
    print(f"  Supplier:    {order['items'][0]['supplier'].replace('_', ' ').title()}")
    print(f"  Status:     {format_status(order['status'])}")
    print(f"  Store:      {order['items'][0].get('store_name', 'N/A')}")
    print(f"  Created:    {order['items'][0]['created_at']}")
    print(f"  Updated:    {order['items'][0]['updated_at']}")
    
    if order['items'][0].get('tracking_number'):
        print(f"  Tracking:   {order['items'][0]['tracking_number']}")
    
    if order['items'][0].get('notes'):
        print(f"  Notes:      {order['items'][0]['notes']}")
    
    print("\n  ITEMS:")
    total = 0.0
    for item in order["items"]:
        line_total = item["total_price"] or 0.0
        total += line_total
        print(f"    • {item['product_name']}")
        print(f"      SKU: {item['product_sku']} | Qty: {item['quantity']} | "
              f"Unit: {format_currency(item['unit_price'])} | "
              f"Total: {format_currency(line_total)}")
    
    shipping = sum(i["shipping_cost"] or 0 for i in order["items"])
    print(f"\n  Subtotal:   {format_currency(total)}")
    print(f"  Shipping:   {format_currency(shipping)}")
    print(f"  TOTAL:      {format_currency(total + shipping)}")
    
    print("\n  HISTORY:")
    for event in events:
        data = json.loads(event["event_data"]) if event["event_data"] else {}
        print(f"    {event['created_at']} | {event['event_type']} | {data}")
    
    print("=" * 60)
    print()


def cmd_status(args):
    """Update order status."""
    order = get_order(args.order_number)
    
    if not order:
        print(f"\n❌ Order {args.order_number} not found.")
        return
    
    new_status = args.new_status
    if new_status not in config.ORDER_STATUS.values():
        print(f"\n❌ Invalid status. Valid statuses:")
        for s in config.ORDER_STATUS.values():
            print(f"   - {s}")
        return
    
    update_order_status(
        args.order_number,
        new_status,
        tracking_number=args.tracking,
        notes=args.notes
    )
    
    print(f"\n✅ Order {args.order_number} status updated to: {format_status(new_status)}")


def cmd_received(args):
    """Mark order as received."""
    order = get_order(args.order_number)
    
    if not order:
        print(f"\n❌ Order {args.order_number} not found.")
        return
    
    mark_order_received(args.order_number, notes=args.notes or "Manually marked received")
    
    print(f"\n✅ Order {args.order_number} marked as received!")
    
    # Show cost comparison
    cost_report = calculate_actual_vs_estimated()
    order_items = cost_report["products"]
    
    print("\n  COST COMPARISON:")
    for item in order["items"]:
        sku = item["product_sku"]
        if sku in order_items:
            est = order_items[sku]["estimated_total"]
            actual = order_items[sku]["actual_cost"]
            variance = actual - est
            print(f"    {item['product_name']}: Est {format_currency(est)} / "
                  f"Actual {format_currency(actual)} / "
                  f"Var {format_currency(variance)}")


def cmd_costs(args):
    """Generate cost variance report."""
    report = calculate_actual_vs_estimated()
    
    print("\n" + "=" * 70)
    print("💰 COST VARIANCE REPORT")
    print(f"Generated: {report['generated_at']}")
    print("=" * 70)
    
    if not report["products"]:
        print("\n  No delivered orders to report on.")
        print()
        return
    
    print(f"\n{'Product':<30} {'Est. Cost':<12} {'Actual':<12} {'Variance':<12}")
    print("-" * 70)
    
    for sku, data in report["products"].items():
        variance_str = format_currency(data["variance"])
        variance_prefix = "+" if data["variance"] >= 0 else ""
        print(f"{data['name']:<30} "
              f"{format_currency(data['estimated_total']):<12} "
              f"{format_currency(data['actual_cost']):<12} "
              f"{variance_prefix}{variance_str}")
    
    print("-" * 70)
    t = report["totals"]
    vp = "+" if t["variance"] >= 0 else ""
    print(f"{'TOTAL':<30} "
          f"{format_currency(t['estimated_cost']):<12} "
          f"{format_currency(t['actual_cost']):<12} "
          f"{vp}{format_currency(t['variance'])}")
    
    print("=" * 70)
    print()


def cmd_summary(args):
    """Show procurement summary."""
    conn = get_db_connection()
    
    # Order counts by status
    status_counts = conn.execute(
        """SELECT status, COUNT(*) as count, SUM(total_price) as cost
           FROM orders GROUP BY status"""
    ).fetchall()
    
    # Order counts by supplier
    supplier_counts = conn.execute(
        """SELECT supplier, COUNT(*) as count, SUM(total_price) as cost
           FROM orders GROUP BY supplier"""
    ).fetchall()
    
    # Recent activity
    recent_orders = conn.execute(
        """SELECT order_number, supplier, status, created_at
           FROM orders ORDER BY created_at DESC LIMIT 5"""
    ).fetchall()
    
    print("\n" + "=" * 60)
    print("📊 PROCUREMENT SUMMARY")
    print(f"Generated: {datetime.now().isoformat()}")
    print("=" * 60)
    
    print("\n  ORDERS BY STATUS:")
    for row in status_counts:
        print(f"    {format_status(row['status']):<25} {row['count']:>3} orders  "
              f"(total: {format_currency(row['cost'] or 0)})")
    
    print("\n  ORDERS BY SUPPLIER:")
    for row in supplier_counts:
        print(f"    {row['supplier'].replace('_', ' ').title():<25} {row['count']:>3} orders  "
              f"(total: {format_currency(row['cost'] or 0)})")
    
    print("\n  RECENT ORDERS:")
    for row in recent_orders:
        print(f"    {row['order_number']:<22} {row['supplier']:<20} "
              f"{format_status(row['status'])}")
    
    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Order tracker for RedWand Flipper Kit procurement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python order-tracker.py list                        # List all orders
  python order-tracker.py list --status pending       # Filter by status
  python order-tracker.py show MC-20241015-001         # Show order details
  python order-tracker.py status MC-001 shipped        # Update status
  python order-tracker.py status MC-001 --tracking TRACK123  # Add tracking
  python order-tracker.py received MC-001             # Mark as received
  python order-tracker.py costs                       # Cost variance report
  python order-tracker.py summary                     # Procurement summary
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    list_parser = subparsers.add_parser("list", help="List all orders")
    list_parser.add_argument("--status", "-s", 
                             choices=list(config.ORDER_STATUS.values()),
                             help="Filter by status")
    list_parser.add_argument("--supplier", 
                             choices=["micro_center", "hacker_warehouse", "lab401"],
                             help="Filter by supplier")
    
    show_parser = subparsers.add_parser("show", help="Show order details")
    show_parser.add_argument("order_number", help="Order number to show")
    
    status_parser = subparsers.add_parser("status", help="Update order status")
    status_parser.add_argument("order_number", help="Order number to update")
    status_parser.add_argument("new_status", 
                               choices=list(config.ORDER_STATUS.values()),
                               help="New status")
    status_parser.add_argument("--tracking", "-t", help="Tracking number")
    status_parser.add_argument("--notes", "-n", help="Notes")
    
    received_parser = subparsers.add_parser("received", help="Mark order received")
    received_parser.add_argument("order_number", help="Order number")
    received_parser.add_argument("--notes", "-n", help="Notes")
    
    subparsers.add_parser("costs", help="Cost variance report")
    subparsers.add_parser("summary", help="Procurement summary")
    
    args = parser.parse_args()
    
    try:
        init_db()
    except Exception as e:
        logger.error(f"Database init failed: {e}")
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "show":
        cmd_show(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "received":
        cmd_received(args)
    elif args.command == "costs":
        cmd_costs(args)
    elif args.command == "summary":
        cmd_summary(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
