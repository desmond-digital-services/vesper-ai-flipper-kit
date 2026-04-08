"""
Vesper AI Flipper Kit - Procurement Configuration
=================================================
Stores supplier credentials, store locations, and product info.
Copy this to config_secrets.py and fill in your actual values.
"""

# ─────────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────────
PRODUCTS = {
    "flipper_zero": {
        "name": "Flipper Zero",
        "sku": "FLIPPER-ZERO",
        "price": 199.00,
        "suppliers": ["micro_center", "hacker_warehouse", "lab401"],
    },
    "moto_g_play_2026": {
        "name": "Moto G Play 2026",
        "sku": "MOTO-G-PLAY-2026",
        "price": 130.00,
        "suppliers": ["micro_center"],
    },
    "sd_card_32gb": {
        "name": "32GB SD Card",
        "sku": "SD-32GB",
        "price": 8.00,
        "suppliers": ["micro_center"],
    },
}

# ─────────────────────────────────────────────
# SUPPLIERS
# ─────────────────────────────────────────────
SUPPLIERS = {
    "micro_center": {
        "name": "Micro Center",
        "preferred": True,
        "store_locations": [
            {
                "id": "austin",
                "name": "Austin",
                "address": "910 W 14th St, Austin, TX 78701",
                "phone": "(512) 459-4408",
            },
            {
                "id": "cedar_creek",
                "name": "Cedar Creek",
                "address": "16000 Hwy 290 E, Cedar Creek, TX 78612",
                "phone": "(512) 303-4408",
            },
        ],
        "website": "https://www.microcenter.com",
        "order_online_url": "https://www.microcenter.com/checkout",
        "stock_check_url": "https://www.microcenter.com/product",
    },
    "hacker_warehouse": {
        "name": "Hacker Warehouse",
        "preferred": False,
        "website": "https://hackerwarehouse.com",
        "order_url": "https://hackerwarehouse.com/product/flipper-zero",
        "stock_check_url": "https://hackerwarehouse.com/product/flipper-zero",
        "shipping_base": 8.95,
        "shipping_per_item": 1.50,
    },
    "lab401": {
        "name": "Lab401",
        "preferred": False,
        "website": "https://lab401.com",
        "order_url": "https://lab401.com/products/flipper-zero",
        "stock_check_url": "https://lab401.com/products/flipper-zero",
        "shipping_base": 15.00,  # EU shipping
        "shipping_per_item": 2.50,
    },
}

# ─────────────────────────────────────────────
# KIT CONFIGURATION
# ─────────────────────────────────────────────
KIT_CONFIG = {
    "flipper_zero_qty": 1,
    "moto_g_play_qty": 1,
    "sd_card_qty": 1,
    "estimated_total": (
        PRODUCTS["flipper_zero"]["price"]
        + PRODUCTS["moto_g_play_2026"]["price"]
        + PRODUCTS["sd_card_32gb"]["price"]
    ),
}

# ─────────────────────────────────────────────
# PREFERRED SUPPLIER ORDER
# ─────────────────────────────────────────────
PREFERRED_SUPPLIER_ORDER = ["micro_center", "hacker_warehouse", "lab401"]

# ─────────────────────────────────────────────
# NOTIFICATION SETTINGS
# ─────────────────────────────────────────────
NOTIFICATIONS = {
    "email": {
        "enabled": False,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "your-email@gmail.com",
        "smtp_password": "your-app-password",
        "from_addr": "vesper-procurement@example.com",
        "to_addrs": ["admin@vesper.ai"],
    },
    "sms": {
        "enabled": False,
        "provider": "twilio",
        "twilio_sid": "YOUR_TWILIO_SID",
        "twilio_token": "YOUR_TWILIO_TOKEN",
        "from_number": "+1234567890",
        "to_numbers": ["+1234567890"],
    },
    "telegram": {
        "enabled": False,
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_ids": [],
    },
}

# ─────────────────────────────────────────────
# DATABASE / LOGGING
# ─────────────────────────────────────────────
DB_PATH = "procurement.db"
LOG_PATH = "procurement.log"
LOG_LEVEL = "INFO"

# ─────────────────────────────────────────────
# ORDER STATUSES
# ─────────────────────────────────────────────
ORDER_STATUS = {
    "PENDING": "pending",
    "CONFIRMED": "confirmed",
    "READY_FOR_PICKUP": "ready_for_pickup",
    "SHIPPED": "shipped",
    "DELIVERED": "delivered",
    "CANCELLED": "cancelled",
    "BACKORDERED": "backordered",
}

STOCK_STATUS = {
    "IN_STOCK": "in_stock",
    "LOW_STOCK": "low_stock",
    "OUT_OF_STOCK": "out_of_stock",
    "BACKORDERED": "backordered",
    "UNKNOWN": "unknown",
}
