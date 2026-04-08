# Vesper AI - Comprehensive Local Testing Plan

**Date:** 2026-04-08
**Goal:** Verify all systems work locally before deployment

---

## Phase 1: Stripe Checkout Testing

### 1.1 Stripe Configuration
- [ ] Verify Stripe API keys in .env
- [ ] Confirm test mode is active
- [ ] Check Stripe CLI is installed and authenticated
- [ ] Verify webhook secret configuration

### 1.2 Checkout Flow Test
- [ ] Test checkout session creation
- [ ] Verify customer metadata passes through
- [ ] Test with test card: 4242 4242 4242 4242
- [ ] Test with decline card: 4000 0000 0000 0002
- [ ] Verify 24-hour session expiration
- [ ] Test payment intent creation and confirmation

### 1.3 Webhook Testing (Stripe CLI)
- [ ] Start Stripe CLI webhook forwarder
- [ ] Test `checkout.session.completed` event
- [ ] Verify webhook signature verification
- [ ] Test webhook retry logic
- [ ] Verify order creation in SQLite

---

## Phase 2: Order Management Testing

### 2.1 Database Operations
- [ ] Initialize SQLite database
- [ ] Test order creation via webhook
- [ ] Test order status updates
- [ ] Test order retrieval (single + list)
- [ ] Test order updates (status, shipping info)
- [ ] Test order deletion (if implemented)

### 2.2 Admin Dashboard
- [ ] Load admin dashboard in browser
- [ ] Test order list view
- [ ] Test order detail view
- [ ] Test status update buttons
- [ ] Test shipping info form
- [ ] Test CSV export functionality
- [ ] Test responsive design on mobile

### 2.3 API Endpoints
- [ ] Test GET /orders (list)
- [ ] Test GET /orders/{id} (detail)
- [ ] Test PUT /orders/{id} (update)
- [ ] Test DELETE /orders/{id} (delete)
- [ ] Test GET /reports/sales
- [ ] Test GET /reports/revenue
- [ ] Test GET /reports/build-times
- [ ] Test GET /reports/shipping
- [ ] Verify JSON response formats
- [ ] Test error handling

---

## Phase 3: Email System Testing

### 3.1 Email Templates
- [ ] Load order-confirmation.html in browser
- [ ] Load build-progress.html in browser
- [ ] Load shipped.html in browser
- [ ] Load followup.html in browser
- [ ] Load payment-failed.html in browser
- [ ] Verify all HTML renders correctly
- [ ] Verify variable substitution syntax

### 3.2 Email Delivery (Debug Mode)
- [ ] Test order confirmation email
- [ ] Test build progress email
- [ ] Test shipped notification email
- [ ] Test follow-up email
- [ ] Test payment failed email
- [ ] Verify SQLite logging of sent emails
- [ ] Test duplicate prevention logic

### 3.3 SMTP Configuration
- [ ] Verify SMTP server settings
- [ ] Test email sending to real address
- [ ] Verify email content (subject, body, HTML)
- [ ] Test email with attachments (if any)

---

## Phase 4: Procurement Automation Testing

### 4.1 Configuration
- [ ] Load automation/config.py
- [ ] Verify product definitions
- [ ] Verify supplier configurations
- [ ] Verify notification settings

### 4.2 Stock Checker
- [ ] Test Micro Center stock check
- [ ] Test Hacker Warehouse stock check
- [ ] Test Lab401 stock check (if accessible)
- [ ] Verify stock alerts trigger correctly
- [ ] Test multi-supplier monitoring

### 4.3 Order Tracker
- [ ] Test order creation in tracker
- [ ] Test order status updates
- [ ] Test cost variance calculation
- [ ] Test order history export

### 4.4 Supplier Email Templates
- [ ] Load supplier-inquiry.html
- [ ] Verify variable substitution
- [ ] Test email rendering in browser

---

## Phase 5: Landing Page Testing

### 5.1 Page Rendering
- [ ] Load index.html in browser
- [ ] Verify all 8 sections render correctly
- [ ] Test mobile responsive design
- [ ] Test tablet responsive design
- [ ] Verify CSS loads correctly
- [ ] Verify JavaScript loads correctly

### 5.2 Interactive Elements
- [ ] Test smooth scroll navigation
- [ ] Test FAQ accordion
- [ ] Test all anchor links
- [ ] Verify all images load
- [ ] Test external links

### 5.3 Stripe Integration (Frontend)
- [ ] Verify Stripe.js is loaded
- [ ] Test checkout button click
- [ ] Verify API key configuration
- [ ] Test redirect to checkout

---

## Phase 6: Documentation Testing

### 6.1 Customer Documentation
- [ ] Read setup-guide.md
- [ ] Read assembly-sop.md
- [ ] Read instruction-card-design.md
- [ ] Read troubleshooting.md
- [ ] Read faq.md
- [ ] Read responsible-use.md
- [ ] Verify all files render correctly
- [ ] Check for broken links or formatting issues

### 6.2 Technical Documentation
- [ ] Read all docs/*.md files
- [ ] Verify setup instructions are clear
- [ ] Check for missing steps or unclear language
- [ ] Verify code examples are correct

---

## Phase 7: End-to-End Integration Testing

### 7.1 Full Checkout Flow
- [ ] Simulate customer order through Stripe
- [ ] Verify webhook receives event
- [ ] Verify order created in database
- [ ] Verify confirmation email sent
- [ ] Verify order appears in admin dashboard
- [ ] Update order status
- [ ] Verify shipping email sent

### 7.2 Error Scenarios
- [ ] Test failed payment scenario
- [ ] Test webhook timeout handling
- [ ] Test database connection failure
- [ ] Test email sending failure
- [ ] Verify error logging and recovery

---

## Phase 8: Security Testing

### 8.1 API Security
- [ ] Verify CORS configuration
- [ ] Test API authentication (if implemented)
- [ ] Verify sensitive data is not exposed in logs
- [ ] Test input validation on all endpoints

### 8.2 Stripe Security
- [ ] Verify webhook signature verification
- [ ] Test replay attack prevention
- [ ] Verify API keys are not exposed in frontend
- [ ] Check for webhook secret leakage

---

## Phase 9: Performance Testing

### 9.1 Page Load Speed
- [ ] Test landing page load time
- [ ] Test admin dashboard load time
- [ ] Verify all assets are optimized
- [ ] Check for blocking resources

### 9.2 API Response Time
- [ ] Test API endpoint response times
- [ ] Verify database queries are optimized
- [ ] Test concurrent request handling

---

## Phase 10: Final Verification

### 10.1 Checklist Review
- [ ] All 100+ test items complete
- [ ] No critical bugs found
- [ ] All known issues documented
- [ ] Ready for deployment decision

### 10.2 Deployment Readiness
- [ ] Deployment documentation complete
- [ ] Environment variables documented
- [ ] Database schema documented
- [ ] Rollback procedure documented

---

## Testing Tools Used

- **Stripe CLI:** Webhook forwarding and testing
- **Python http.server:** Local web server
- **SQLite Browser:** Database inspection
- **Browser DevTools:** Frontend testing
- **curl:** API endpoint testing

---

## Known Issues to Track

*Document any issues found during testing here*

---

## Test Results Summary

*Fill in after testing complete*

- Tests Passed: ___/___
- Tests Failed: ___/___
- Critical Bugs: ___
- Non-Critical Bugs: ___
- Ready for Deployment: YES/NO

---

**Status:** IN PROGRESS
**Started:** 2026-04-08 17:15 CDT
**Estimated Completion:** 2026-04-08 18:00 CDT
