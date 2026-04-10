"""
Stripe Checkout Session Generator for RedWand Flipper Kit
Follows Stripe Best Practices - Uses Checkout Sessions API
"""

import stripe
import os
from stripe_config import StripeConfig, PRODUCT_CONFIG, SUCCESS_URL, CANCEL_URL

class CheckoutGenerator:
    """Generate Stripe checkout sessions"""
    
    def __init__(self):
        config = StripeConfig()
        config.validate()
        
        stripe.api_key = config.get_api_key()
        self.config = config
        
    def create_checkout_session(self, customer_email=None, customer_name=None):
        """
        Create a checkout session for RedWand Flipper Kit
        
        Args:
            customer_email: Customer email for the order
            customer_name: Customer name (optional)
            
        Returns:
            Stripe checkout session object
        """
        
        try:
            # Create or retrieve product/price
            # In production, you'd create these once and save IDs
            # For now, we'll create them inline
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': PRODUCT_CONFIG['currency'],
                        'product_data': {
                            'name': PRODUCT_CONFIG['name'],
                            'description': PRODUCT_CONFIG['description'],
                        },
                        'unit_amount': PRODUCT_CONFIG['price'],
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=SUCCESS_URL,
                cancel_url=CANCEL_URL,
                customer_email=customer_email,
                customer_creation={
                    'name': customer_name,
                } if customer_name else None,
                metadata={
                    'product': 'redwand-ai-flipper-kit',
                    'price': str(PRODUCT_CONFIG['price']),
                    'currency': PRODUCT_CONFIG['currency'],
                    'source': 'redwand-ai-website',
                },
                expires_at_hours=24,  # Session expires in 24 hours
            )
            
            return session
            
        except stripe.error.StripeError as e:
            print(f"Stripe Error: {e}")
            raise

if __name__ == '__main__':
    # Example usage
    checkout = CheckoutGenerator()
    
    session = checkout.create_checkout_session(
        customer_email='test@example.com',
        customer_name='Test Customer'
    )
    
    print(f"Checkout Session URL: {session.url}")
    print(f"Session ID: {session.id}")
