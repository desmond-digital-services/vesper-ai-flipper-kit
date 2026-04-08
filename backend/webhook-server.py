#!/usr/bin/env python3
"""
Vesper AI - Webhook Handler for Stripe Events
"""

import stripe
import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment
load_dotenv('.stripe.env')

app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Use the webhook signing secret to verify events
endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

@app.route('/api/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    print("=" * 60)
    print("Webhook received!")
    print(f"Signature: {sig_header[:20]}..." if sig_header else "No signature")
    print(f"Payload length: {len(payload)} bytes")
    print()
    
    try:
        if endpoint_secret and endpoint_secret != 'whsec_test_placeholder':
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
            print(f"✓ Webhook signature verified")
            print(f"✓ Event type: {event['type']}")
        else:
            # For testing without webhook secret, parse directly
            event = json.loads(payload)
            print(f"⚠️  Webhook secret not configured, parsing directly")
            print(f"⚠️  Event type: {event['type']}")
    except ValueError as e:
        print(f"✗ Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"✗ Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    event_type = event['type']
    print(f"Processing event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        handle_checkout_session_completed(event['data']['object'])
    elif event_type == 'payment_intent.succeeded':
        handle_payment_succeeded(event['data']['object'])
    else:
        print(f"Unhandled event type: {event_type}")
    
    print("=" * 60)
    print()
    
    return jsonify({'status': 'success', 'event_type': event_type}), 200

def handle_checkout_session_completed(session):
    """Handle successful checkout session"""
    print()
    print("✓✓✓ CHECKOUT SESSION COMPLETED ✓✓✓")
    print()
    print(f"Session ID: {session['id']}")
    print(f"Customer Email: {session['customer_details']['email']}")
    print(f"Payment Status: {session['payment_status']}")
    print(f"Amount Total: ${session['amount_total'] / 100:.2f}")
    print(f"Currency: {session['currency'].upper()}")
    
    # Extract metadata
    metadata = session.get('metadata', {})
    print(f"Metadata: {metadata}")
    
    # Here you would:
    # 1. Create order in database
    # 2. Send confirmation email
    # 3. Start build process
    print()
    print("NEXT STEPS:")
    print("  1. Create order in SQLite database")
    print("  2. Send confirmation email")
    print("  3. Update admin dashboard")
    print()
    
def handle_payment_succeeded(payment_intent):
    """Handle successful payment"""
    print()
    print(f"✓ Payment succeeded: {payment_intent['id']}")
    print(f"  Amount: ${payment_intent['amount'] / 100:.2f}")
    print(f"  Status: {payment_intent['status']}")
    print()

if __name__ == '__main__':
    print("=" * 60)
    print("Vesper AI - Webhook Server")
    print("=" * 60)
    print(f"Listening on: http://localhost:5050/api/webhook")
    print(f"Stripe Secret: {'✓ Configured' if endpoint_secret else '⚠️  Not configured'}")
    print()
    
    # Run on different port to avoid conflict with order-manager
    app.run(host='0.0.0.0', port=5051, debug=True)
