"""
Stripe Configuration for Vesper AI Flipper Kit
Follows Stripe Best Practices (API version 2026-02-25.clover)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StripeConfig:
    """Stripe API configuration for Vesper AI"""
    
    def __init__(self):
        self.secret_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        self.test_mode = os.getenv('STRIPE_TEST_MODE', 'true').lower() == 'true'
        
    def validate(self):
        """Validate that required keys are set"""
        errors = []
        
        if not self.secret_key:
            errors.append("STRIPE_SECRET_KEY is required")
        elif not self.secret_key.startswith('sk_test_') and not self.secret_key.startswith('sk_live_'):
            errors.append("STRIPE_SECRET_KEY must start with sk_test_ or sk_live_")
            
        if not self.publishable_key:
            errors.append("STRIPE_PUBLISHABLE_KEY is required")
        elif not self.publishable_key.startswith('pk_test_') and not self.publishable_key.startswith('pk_live_'):
            errors.append("STRIPE_PUBLISHABLE_KEY must start with pk_test_ or pk_live_")
            
        if not self.webhook_secret:
            errors.append("STRIPE_WEBHOOK_SECRET is required")
        elif not self.webhook_secret.startswith('whsec_'):
            errors.append("STRIPE_WEBHOOK_SECRET must start with whsec_")
            
        if errors:
            raise ValueError(f"Stripe configuration errors:\n" + "\n".join(errors))
            
        return True
    
    def get_api_key(self):
        """Get secret key for API calls"""
        return self.secret_key
    
    def get_publishable_key(self):
        """Get publishable key for frontend"""
        return self.publishable_key
    
    def is_test_mode(self):
        """Check if running in test mode"""
        return self.test_mode
    
    def get_endpoint(self):
        """Get Stripe API endpoint based on mode"""
        if self.test_mode:
            return "https://api.stripe.com"
        else:
            return "https://api.stripe.com"

# Product configuration
PRODUCT_CONFIG = {
    'name': 'Vesper AI Flipper Kit',
    'description': 'Talk to your hardware in plain English. Includes Flipper Zero, Moto G Play, and pre-installed Vesper app.',
    'price': 49900,  # $499 in cents
    'currency': 'usd',
}

# Success and cancel URLs
SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', 'https://vespere.ai/success')
CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', 'https://vespere.ai/cancel')
