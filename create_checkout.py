#!/usr/bin/env python3
"""
Create Stripe checkout session for RedWand Flipper Kit
Uses the stripe-payments skill workflow
"""
import stripe
import json
import sys

# Load Stripe keys from environment
import os
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_YOUR_KEY_HERE")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "pk_test_YOUR_KEY_HERE")

stripe.api_key = STRIPE_SECRET_KEY

# Success/cancel URLs (production)
SUCCESS_URL = "https://desmond-digital.com/flip/success.html"
CANCEL_URL = "https://desmond-digital.com/flip/cancel.html"

print("=" * 60)
print("RedWand — Creating Stripe Checkout Session")
print("=" * 60)

try:
    # Step 1: Create product (check if exists first)
    print("\n[1/3] Creating product...")
    
    # List existing products to check
    products = stripe.Product.list(limit=10)
    redwand_product = None
    for p in products.data:
        if "redwand" in p.name.lower() or "flipper" in p.name.lower():
            redwand_product = p
            print(f"  Found existing product: {p.id} — {p.name}")
            break
    
    if not redwand_product:
        redwand_product = stripe.Product.create(
            name="RedWand Flipper Kit",
            description="Pre-assembled Flipper Zero + Moto G Play with RedWand app. No coding required. Talk to your hardware in plain English.",
            images=[],
        )
        print(f"  Created product: {redwand_product.id}")
    
    # Step 2: Create price ($499.00 = 49900 cents)
    print("\n[2/3] Creating price ($499)...")
    
    prices = stripe.Price.list(product=redwand_product.id, active=True, limit=5)
    price_499 = None
    for p in prices.data:
        if p.unit_amount == 49900:
            price_499 = p
            print(f"  Found existing price: {p.id} — ${p.unit_amount/100}")
            break
    
    if not price_499:
        price_499 = stripe.Price.create(
            product=redwand_product.id,
            unit_amount=49900,
            currency="usd",
        )
        print(f"  Created price: {price_499.id}")
    
    # Step 3: Create checkout session
    print("\n[3/3] Creating checkout session...")
    
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price": price_499.id,
            "quantity": 1,
        }],
        mode="payment",
        success_url=SUCCESS_URL,
        cancel_url=CANCEL_URL,
        metadata={
            "product": "RedWand Flipper Kit",
            "sku": "VFK-2026-001",
        },
    )
    
    print(f"\n{'=' * 60}")
    print("✅ CHECKOUT SESSION CREATED")
    print(f"{'=' * 60}")
    print(f"\nCheckout URL: {session.url}")
    print(f"Session ID: {session.id}")
    print(f"Price: ${price_499.unit_amount/100:.2f}")
    print(f"Product: {redwand_product.name}")
    print(f"Mode: {session.mode}")
    print(f"Success: {session.success_url}")
    print(f"Cancel: {session.cancel_url}")
    print(f"\nPublishable Key: {STRIPE_PUBLISHABLE_KEY}")
    
    # Output as JSON for easy parsing
    output = {
        "checkout_url": session.url,
        "session_id": session.id,
        "publishable_key": STRIPE_PUBLISHABLE_KEY,
        "price_id": price_499.id,
        "product_id": redwand_product.id,
    }
    
    print(f"\n--- JSON OUTPUT ---")
    print(json.dumps(output, indent=2))
    
except stripe.error.StripeError as e:
    print(f"\n❌ Stripe Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
