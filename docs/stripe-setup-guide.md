# Stripe Setup Guide for RedWand Flipper Kit

## Step 1: Get Stripe API Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy the **Secret key** (starts with `sk_test_`)
3. Copy the **Publishable key** (starts with `pk_test_`)
4. Go to https://dashboard.stripe.com/webhooks and create a webhook
5. Copy the **Webhook signing secret** (starts with `whsec_`)

## Step 2: Create Product and Price

### Option A: Via Stripe Dashboard (Recommended for Launch)
1. Go to https://dashboard.stripe.com/products
2. Click "Add product"
3. Fill in product details:
   - **Name:** RedWand Flipper Kit
   - **Description:** Talk to your hardware in plain English. Includes Flipper Zero, Moto G Play, and pre-installed RedWand app.
   - **Pricing:** Single price, $499.00
   - **Currency:** USD
4. Click "Create product"
5. The price ID will be generated (starts with `price_`)

### Option B: Via API (For Automation)
```bash
# Create product
stripe products create \
  --name "RedWand Flipper Kit" \
  --description "Talk to your hardware in plain English" \
  --default-price-data '{"currency": "usd", "unit_amount": 49900}'
```

## Step 3: Set Up Webhook

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter webhook URL: `https://redwand.io/webhook`
   - For local testing, use: `https://your-tunnel-url.ngrok.io/webhook`
4. Select events to listen for:
   - ✅ checkout.session.completed
   - ✅ payment_intent.succeeded
   - ✅ payment_intent.payment_failed
5. Copy the webhook signing secret (starts with `whsec_`)

## Step 4: Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
STRIPE_SECRET_KEY=sk_test_1234567890abcdef
STRIPE_PUBLISHABLE_KEY=pk_test_1234567890abcdef
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef
STRIPE_SUCCESS_URL=https://redwand.io/success
STRIPE_CANCEL_URL=https://redwand.io/cancel
STRIPE_TEST_MODE=true
```

## Step 5: Test Payment Flow

### 1. Test Card for Testing
Use Stripe test card:
- **Card Number:** 4242 4242 4242 4242
- **Expiry:** Any future date
- **CVC:** Any 3 digits

### 2. Run Checkout Generator
```bash
cd ~/clawd/projects/redwand-ai/backend
python3 create-checkout.py
```

This will output:
- Checkout Session URL
- Session ID

### 3. Test Webhook Delivery
```bash
# Run webhook server
python3 webhooks.py
```

Use Stripe CLI to send test webhook:
```bash
stripe trigger checkout.session.completed \
  --add checkout_session:cs_test_123456
```

### 4. Verify Order Creation
Check that:
- Order record is created in database
- Order status is set to 'paid'
- Confirmation email is sent

## Step 6: Go Live

1. Go to https://dashboard.stripe.com/live/apikeys
2. Repeat Step 1 with live keys (starts with `sk_live_` and `pk_live_`)
3. Update `.env` file with live keys:
   ```bash
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_PUBLISHABLE_KEY=pk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_TEST_MODE=false
   ```
4. Test with a small real payment first

## API Version Note

This integration uses Stripe API version **2026-02-25.clover**

Always use the latest API version for new integrations.

## Best Practices Followed

✅ Uses Checkout Sessions API (recommended over PaymentIntents)
✅ Handles payment failures gracefully
✅ Sets up webhooks for event handling
✅ Includes customer metadata in checkout sessions
✅ Uses test mode before going live
✅ 24-hour session expiration
✅ Validates API keys on startup

## Troubleshooting

### Webhook Not Firing
- Check webhook URL is publicly accessible
- Verify webhook secret matches
- Check Stripe webhook event log in dashboard

### Payment Failing
- Check test card details
- Verify publishable key is correct
- Check Stripe dashboard for error logs

### Session Expired
- Sessions expire after 24 hours
- Customer needs to complete payment in 24 hours
- Send reminder email at 22 hours if needed

## Next Steps

After Stripe is set up:
1. Integrate checkout button into landing page
2. Connect webhook handler to order database
3. Connect to email system for notifications
4. Test full end-to-end flow
5. Go live with real payments
