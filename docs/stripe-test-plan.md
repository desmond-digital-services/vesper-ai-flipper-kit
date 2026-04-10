# Stripe Testing Plan for RedWand Flipper Kit

## Testing Phases

### Phase 1: API Connection Test (Test Mode)

**Goal:** Verify Stripe API keys are valid and can create sessions

**Test Steps:**
1. Load configuration from `.env` file
2. Validate API keys with `stripe-config.py`
3. Create a test checkout session
4. Verify session URL is generated
5. Verify session ID is returned

**Expected Result:** Session created successfully, no errors

**Command:**
```bash
cd ~/clawd/projects/redwand-ai/backend
python3 stripe-config.py
python3 create-checkout.py
```

**Success Criteria:**
- ✅ Configuration validates without errors
- ✅ Test session created
- ✅ Session URL returned
- ✅ Session ID returned

---

### Phase 2: Webhook Test (Test Mode)

**Goal:** Verify webhook receives Stripe events

**Test Steps:**
1. Start webhook server locally:
   ```bash
   python3 webhooks.py
   ```
2. Use ngrok or similar to expose webhook URL to internet
3. Add webhook URL to Stripe Dashboard
4. Send test webhook event via Stripe CLI:
   ```bash
   stripe trigger checkout.session.completed \
     --add checkout_session:cs_test_123456
   ```
5. Verify webhook receives event
6. Verify webhook returns 200 status

**Expected Result:** Webhook receives and logs event

**Success Criteria:**
- ✅ Webhook server starts
- ✅ Event received in webhook logs
- ✅ 200 status returned to Stripe
- ✅ Event data logged correctly

**Note:** For local testing, use ngrok to expose webhook:
```bash
ngrok http 5000
```

---

### Phase 3: End-to-End Payment Test (Test Mode)

**Goal:** Complete full payment flow from start to finish

**Test Steps:**
1. Open checkout session URL from Phase 1
2. Enter test card details:
   - Card Number: 4242 4242 4242 4242
   - Expiry: 12/34 (any future date)
   - CVC: 123
3. Complete payment
4. Verify redirect to success URL
5. Verify webhook receives `checkout.session.completed` event
6. Verify order is created in database
7. Verify order status is set to 'paid'
8. Verify confirmation email is sent

**Expected Result:** Full payment flow completes without errors

**Success Criteria:**
- ✅ Checkout page loads
- ✅ Test card accepted
- ✅ Redirects to success page
- ✅ Webhook receives event
- ✅ Order created in database
- ✅ Confirmation email sent
- ✅ No errors in any logs

---

### Phase 4: Error Handling Test

**Goal:** Verify errors are handled gracefully

**Test Steps:**

**Test A: Declined Card**
1. Try checkout with declined test card: `4000 0000 0000 0002`
2. Verify error message is displayed
3. Verify webhook receives `payment_intent.payment_failed` event
4. Verify payment failed email is sent

**Test B: Invalid Card**
1. Try checkout with invalid test card: `4242 4242 4242 4243`
2. Verify error is displayed on checkout page
3. Verify webhook doesn't receive success event

**Test C: Expired Session**
1. Create a checkout session
2. Wait 24 hours for session to expire
3. Try to pay with expired session URL
4. Verify session expired error is displayed

**Success Criteria:**
- ✅ Declined cards show proper error
- ✅ Invalid cards show proper error
- ✅ Expired sessions show proper error
- ✅ Payment failed emails sent correctly
- ✅ No payments created for failed attempts

---

### Phase 5: Live Mode Test (Optional - After Launch)

**Goal:** Verify live mode works with real payment

**Test Steps:**
1. Switch `.env` to live keys
2. Create a small test product ($1.00) for live testing
3. Complete a real payment with small amount
4. Verify all flows work as in test mode
5. Refund test payment if needed

**Success Criteria:**
- ✅ Real payment processes
- ✅ Live webhooks receive events
- ✅ Orders created correctly
- ✅ Emails sent correctly

**Note:** Test with small amount first to minimize risk if issues occur.

---

## Test Execution Checklist

### Pre-Test Setup
- [ ] Stripe test keys obtained
- [ ] `.env` file created with test keys
- [ ] Webhook endpoint created in Stripe Dashboard
- [ ] Webhook secret obtained
- [ ] Local webhook server tested

### Phase 1: API Connection
- [ ] Configuration validates
- [ ] Test session created
- [ ] Session URL returned

### Phase 2: Webhook
- [ ] Webhook server started
- [ ] Webhook URL accessible
- [ ] Test event sent
- [ ] Event received
- [ ] 200 status returned

### Phase 3: End-to-End
- [ ] Checkout session opened
- [ ] Test card entered
- [ ] Payment completed
- [ ] Redirected to success
- [ ] Webhook received event
- [ ] Order created in database
- [ ] Confirmation email sent

### Phase 4: Error Handling
- [ ] Declined card tested
- [ ] Invalid card tested
- [ ] Expired session tested
- [ ] Errors handled gracefully

### Phase 5: Live Mode (Optional)
- [ ] Live keys obtained
- [ ] `.env` updated to live keys
- [ ] Small test payment made
- [ ] Refunded if needed

---

## Test Results Template

Use this template to document test results:

| Test | Date | Status | Notes |
|------|------|--------|-------|
| Phase 1: API Connection | | | |
| Phase 2: Webhook | | | |
| Phase 3: End-to-End | | | |
| Phase 4: Error Handling | | | |
| Phase 5: Live Mode | | | |

**Overall Status:** [PASSED / FAILED / IN PROGRESS]

---

## Common Test Issues

### Webhook Not Receiving Events
**Cause:** Webhook URL not accessible or secret mismatch

**Solution:**
1. Verify webhook URL is publicly accessible
2. Check ngrok is running (for local testing)
3. Verify webhook secret matches Stripe Dashboard exactly
4. Check firewall rules allow Stripe webhooks

### Invalid Test Card
**Cause:** Test card details entered incorrectly

**Solution:**
1. Use exact test card number: 4242 4242 4242 4242
2. Expiry can be any future date
3. CVC can be any 3 digits
4. No spaces in card number

### Session Creation Failing
**Cause:** API key invalid or missing

**Solution:**
1. Verify STRIPE_SECRET_KEY is correct
2. Verify key has correct prefix (sk_test_)
3. Check Stripe Dashboard for API key errors

---

## Go-Live Checklist

Before going live, ensure:

- [ ] All tests in Test Mode passed
- [ ] Live API keys obtained
- [ ] Live webhook endpoint configured
- [ ] Webhook secret updated for live mode
- [ ] Database schema ready for production
- [ ] Email system configured for production
- [ ] Landing page deployed to production URL
- [ ] Success and cancel pages deployed to production URL
- [ ] Error handling tested and working
- [ ] Support team briefed on live launch
- [ ] Monitoring/alerting configured

---

**Last Updated:** 2026-04-08
**Status:** Test plan ready for execution
