# Vesper AI Project - Deployment Policy

**IMPORTANT:** BUILD LOCAL ONLY — NO DEPLOYMENT WITHOUT APPROVAL

---

## Deployment Status

**Current Policy:** 🔒 BUILD LOCALLY ONLY
**Web Deployment:** ❌ PAUSED — WAITING FOR EXPLICIT APPROVAL
**Action:** Create all files locally, do NOT deploy to DreamHost or make public

---

## Local Build Status

### ✅ Complete (Local Files Created)
1. **Documentation** — All 6 files in `~/clawd/projects/vesper-ai/documentation/`
2. **Landing Page** — All 5 files in `~/clawd/projects/vesper-ai/web/`

### 🔄 In Progress (Building Locally)
3. **Stripe Integration** — Files will be created in `~/clawd/projects/vesper-ai/backend/`

### ⏳ Pending (Local Build)
4. **Email System** — Files in `~/clawd/projects/vesper-ai/email-templates/` and `backend/`
5. **Order Management** — Files in `~/clawd/projects/vesper-ai/backend/` and `web/admin/`
6. **Hardware Procurement** — Files in `~/clawd/projects/vesper-ai/automation/`

---

## Deployment Checklist (Do NOT Do Until Approved)

### ❌ BLOCKED (Awaiting Approval)
- [ ] Deploy to DreamHost
- [ ] Make landing page public
- [ ] Activate Stripe live mode
- [ ] Send any customer emails
- [ ] Accept real payments
- [ ] Launch to social media

### ✅ READY TO DO (Once Approved)
- [ ] Deploy web/ directory to DreamHost SFTP
- [ ] Activate Stripe live mode
- [ ] Test real payment flow
- [ ] Announce on Reddit/X/Twitter
- [ ] Accept first real order

---

## Local File Structure (What Exists Now)

```
~/clawd/projects/vesper-ai/
├── docs/
│   ├── business-plan.md ✅ LOCAL
│   ├── payment-models-final.md ✅ LOCAL
│   └── assembly-sop.md ⏳ FROM DOCS AGENT
├── web/
│   ├── index.html ✅ LOCAL
│   ├── css/
│   │   └── styles.css ✅ LOCAL
│   ├── js/
│   │   └── main.js ✅ LOCAL
│   ├── assets/
│   │   └── vesper-logo.svg ✅ LOCAL
│   └── checkout.html ⏳ FROM STRIPE AGENT
├── backend/
│   ├── stripe-config.py ⏳ FROM STRIPE AGENT
│   ├── create-checkout.py ⏳ FROM STRIPE AGENT
│   ├── webhooks.py ⏳ FROM STRIPE AGENT
│   ├── order-manager.py ⏳ FROM ORDER AGENT
│   └── email-system.py ⏳ FROM EMAIL AGENT
├── email-templates/
│   ├── order-confirmation.html ⏳ FROM EMAIL AGENT
│   ├── build-progress.html ⏳ FROM EMAIL AGENT
│   ├── shipped.html ⏳ FROM EMAIL AGENT
│   └── followup.html ⏳ FROM EMAIL AGENT
├── documentation/
│   ├── setup-guide.md ✅ LOCAL
│   ├── assembly-sop.md ✅ LOCAL
│   ├── instruction-card-design.md ✅ LOCAL
│   ├── troubleshooting.md ✅ LOCAL
│   ├── faq.md ✅ LOCAL
│   └── responsible-use.md ✅ LOCAL
├── automation/
│   ├── micro-center-order.py ⏳ FROM PROCUREMENT AGENT
│   ├── stock-checker.py ⏳ FROM PROCUREMENT AGENT
│   └── order-tracker.py ⏳ FROM PROCUREMENT AGENT
└── database/
    ├── schema.sql ⏳ FROM ORDER AGENT
    └── orders.db ⏳ FROM ORDER AGENT
```

Legend: ✅ LOCAL (done, on disk) | ⏳ PENDING (will create locally)

---

## Deployment Approval Required Before:

### 1. Web Deployment
- [ ] TD says: "Deploy to DreamHost"
- [ ] Transfer web/ directory via SFTP
- [ ] Set permissions (755 for directories, 644 for files)
- [ ] Test vesper-ai.com is live

### 2. Stripe Live Mode
- [ ] TD says: "Switch to live mode"
- [ ] Replace test API keys with live keys
- [ ] Update Stripe product with real price ID
- [ ] Test with real credit card (small amount first)

### 3. Public Announcement
- [ ] TD says: "Launch publicly"
- [ ] Post to Reddit r/flipperzero
- [ ] Post to X/Twitter
- [ ] Set up customer support email
- [ ] Accept first real payment

---

## Current Phase

**Phase:** LOCAL BUILD ONLY
**Sub-agent Actions:** Continue building all files locally
**Deployment:** PAUSED — AWAITING EXPLICIT APPROVAL
**Web Status:** NOT PUBLIC — Local files only

---

**Last Updated:** 2026-04-08 13:45 CDT
**Policy:** BUILD LOCAL, DEPLOY ON APPROVAL ONLY
