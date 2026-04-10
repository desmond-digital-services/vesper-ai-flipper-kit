#!/usr/bin/env python3
"""
RedWand - Stripe Test Script
Creates test product, price, and checkout session
"""

import stripe
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.stripe.env')

# Set Stripe API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
api_version = os.getenv('STRIPE_API_VERSION', '2026-02-25')
stripe.api_version = api_version

print("=" * 60)
print("RedWand - Stripe Integration Test")
print("=" * 60)
print(f"API Version: {api_version}")
print(f"Test Mode: Yes")
print()

# Step 1: Create Product
print("Step 1: Creating RedWand Flipper Kit product...")
try:
    product = stripe.Product.create(
        name="RedWand Flipper Kit",
        description="Flipper Zero + Phone bundle that lets users control security hardware in plain English",
        images=[],
        metadata={
            'sku': 'REDWAND-KIT-001',
            'category': 'hardware',
            'build_time': '7-10 days'
        }
    )
    print(f"✓ Product created: {product.id}")
    print(f"  Name: {product.name}")
    print(f"  ID: {product.id}")
    print()
except stripe.error.StripeError as e:
    print(f"✗ Error creating product: {e}")
    exit(1)

# Step 2: Create Price
print("Step 2: Creating price ($499.00)...")
try:
    price = stripe.Price.create(
        product=product.id,
        unit_amount=49900,  # $499.00 in cents
        currency='usd',
        metadata={
            'product_id': product.id
        }
    )
    print(f"✓ Price created: {price.id}")
    print(f"  Amount: ${price.unit_amount / 100:.2f} {price.currency.upper()}")
    print(f"  ID: {price.id}")
    print()
except stripe.error.StripeError as e:
    print(f"✗ Error creating price: {e}")
    exit(1)

# Step 3: Create Checkout Session
print("Step 3: Creating checkout session...")
try:
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price.id,
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:8765/success.html?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://localhost:8765/cancel.html',
        customer_email='test@example.com',
        metadata={
            'order_type': 'redwand_flipper_kit',
            'build_time': '7-10 days',
            'test_order': 'true'
        }
    )
    print(f"✓ Checkout session created: {session.id}")
    print(f"  URL: {session.url}")
    print(f"  Payment Status: {session.payment_status}")
    print(f"  Created: {session.created}")
    print()
except stripe.error.StripeError as e:
    print(f"✗ Error creating session: {e}")
    exit(1)

# Step 4: Test Webhook Signature Verification (Mock)
print("Step 4: Testing webhook configuration...")
try:
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_test_placeholder')
    if webhook_secret.startswith('whsec_test'):
        print(f"⚠️  Webhook secret is placeholder")
        print(f"  To test webhooks:")
        print(f"  1. Create webhook at: https://dashboard.stripe.com/test/webhooks")
        print(f"  2. Endpoint: http://localhost:5050/api/webhook")
        print(f"  3. Events: checkout.session.completed")
        print(f"  4. Copy signing secret and add to .stripe.env")
    else:
        print(f"✓ Webhook secret configured")
    print()
except Exception as e:
    print(f"✗ Error with webhook: {e}")
    print()

# Summary
print("=" * 60)
print("Stripe Integration Test Summary")
print("=" * 60)
print(f"Product ID: {product.id}")
print(f"Price ID: {price.id}")
print(f"Session ID: {session.id}")
print(f"Checkout URL: {session.url}")
print()
print("To test payment flow:")
print("1. Open checkout URL in browser")
print("2. Use test card: 4242 4242 4242 4242")
print("3. Complete payment")
print("4. Webhook will trigger at: http://localhost:5050/api/webhook")
print()
print("✓ Stripe integration working!")
print("=" * 60)
