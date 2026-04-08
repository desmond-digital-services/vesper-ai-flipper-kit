"""
Stripe Webhook Handler for Vesper AI Flipper Kit
Handles payment events: checkout.session.completed, payment_intent.succeeded, payment_intent.payment_failed
"""

import stripe
import json
import os
from flask import Flask, request, jsonify
from stripe_config import StripeConfig

app = Flask(__name__)
config = StripeConfig()
stripe.api_key = config.get_api_key()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            config.webhook_secret
        )
    except ValueError as e:
        print(f"Webhook signature verification failed: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        handle_checkout_completed(event['data']['object'])
    elif event['type'] == 'payment_intent.succeeded':
        handle_payment_succeeded(event['data']['object'])
    elif event['type'] == 'payment_intent.payment_failed':
        handle_payment_failed(event['data']['object'])
    else:
        print(f"Unhandled event type: {event['type']}")
    
    return jsonify({'status': 'success'}), 200

def handle_checkout_completed(session):
    """
    Handle checkout.session.completed event
    Create order record, send confirmation email
    """
    print(f"Checkout completed: {session.id}")
    print(f"Customer email: {session.get('customer_details', {}).get('email')}")
    print(f"Payment intent: {session.payment_intent}")
    print(f"Amount: ${session.amount_total / 100}")
    
    # TODO: Create order in database
    # TODO: Send order confirmation email
    # TODO: Update order status to 'paid'

def handle_payment_succeeded(payment_intent):
    """
    Handle payment_intent.succeeded event
    Redundant backup for checkout.session.completed
    """
    print(f"Payment succeeded: {payment_intent.id}")
    print(f"Amount: ${payment_intent.amount / 100}")
    print(f"Status: {payment_intent.status}")

def handle_payment_failed(payment_intent):
    """
    Handle payment_intent.payment_failed event
    Send payment failed email, log for retry
    """
    print(f"Payment failed: {payment_intent.id}")
    print(f"Error: {payment_intent.last_payment_error}")
    
    # TODO: Send payment failed email
    # TODO: Update order status to 'payment_failed'

if __name__ == '__main__':
    # Run webhook server
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
