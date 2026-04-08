# Vesper AI Flipper Kit — Landing Page Design Notes

## Overview

This document covers the design decisions, architecture, and integration points for the Vesper AI Flipper Kit landing page (`vesper-ai/web/`).

---

## Design System

### Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-bg` | `#1a1a1a` | Page background (deep charcoal) |
| `--color-bg-light` | `#222222` | Alternate section backgrounds |
| `--color-bg-card` | `#242424` | Card/component backgrounds |
| `--color-accent` | `#0066ff` | Primary action color (electric blue) |
| `--color-accent-hover` | `#0052cc` | Accent hover state |
| `--color-text` | `#f0f0f0` | Primary text |
| `--color-text-secondary` | `#a0a0a0` | Secondary/muted text |
| `--color-border` | `#2e2e2e` | Default borders |

### Typography

- **Font Family:** Inter (Google Fonts) with system fallback stack
- **Weights Used:** 400 (normal), 500 (medium), 600 (semibold), 700 (bold), 800 (extrabold)
- **Scale:** 0.75rem → 2.75rem (responsive via `clamp()`)
- **Letter-spacing:** Slightly negative (-0.02 to -0.03em) for headlines; improves legibility at large sizes

### Spacing

- Base unit: 8px grid
- Section padding: 80px top/bottom (desktop), 56px (mobile)
- Container max-width: 1120px
- Border radius: 8px (buttons/cards), 12px (cards), 16px (prominent elements)

### Motion

- **Transitions:** `150ms` (fast interactions), `250ms` (base)
- **Hover lift:** `translateY(-2px)` on cards with subtle shadow/glow
- **FAQ accordion:** max-height transition for smooth expand/collapse
- **Scroll shadow:** Header gets `box-shadow` after 100px scroll
- **No gratuitous animation:** Motion serves function, not decoration

---

## Layout & Structure

### Page Sections (in order)

1. **Header** — Sticky nav with logo, links, and CTA
2. **Hero** — Headline + subheadline + CTA + trust indicators + product visual placeholder
3. **Benefits** — 4-column grid of key value props
4. **What's Included** — 2-column grid of kit contents + bonus item + CTA
5. **Who It's For** — 3-column audience cards (Farmers, Factory Managers, Security)
6. **Setup Experience** — 4-step flow with connectors + video preview placeholder
7. **Social Proof** — Stats bar + 2 testimonial cards
8. **FAQ** — 6 questions in accordion format
9. **Checkout** — Two-column card (summary + purchase action)
10. **Footer** — Brand info + nav columns + disclaimer + copyright

### Grid Strategy

- Primary layout: CSS Grid with named columns
- Mobile-first breakpoints via media queries
- Sections alternate between `--color-bg` and `--color-bg-light` for visual rhythm

---

## Key Decisions

### Why NOT the "hacker" aesthetic

The target audience (farmers, factory managers, B2B buyers) expects legitimacy, not novelty. A terminal/Matrix aesthetic signals "hobby project" or "niche toy." The clean, dark professional look signals "serious tool."

### Why #0066ff over neon green

Electric blue reads as modern enterprise tech (Salesforce, IBM, Atlassian). Neon green reads as "I've been using Linux since 1998." We're targeting buyers who shop on Amazon and use Slack, not Reddit's netsec forums.

### Why Inter over Roboto/Montserrat

Inter is optimized for screens at every size. It has a genuine humanist sans feel at body sizes while remaining sharp and authoritative at display sizes. The tabular numerals are excellent for any numeric data.

### FAQ uses `hidden` attribute (not just CSS display:none)

Accessibility: `hidden` removes the element from the accessibility tree. Combined with `aria-expanded` on the button, screen readers correctly announce the expanded state.

### No JavaScript framework needed

The only dynamic behavior is the FAQ accordion. Vanilla JS is ~3KB vs. React at ~45KB. Every millisecond of load time matters for conversion — keep it lean.

---

## Stripe Integration Points

### Where to Replace

Search the codebase for `STRIPE_INTEGRATION_POINT` comments. Current integration is a **placeholder link** (`href="#checkout"`).

### Required Changes

1. **Load Stripe.js** (already in `index.html`):
   ```html
   <script src="https://js.stripe.com/v3/"></script>
   ```

2. **Initialize Stripe** in `js/main.js`:
   ```javascript
   const stripe = Stripe('pk_live_YOUR_PUBLISHABLE_KEY');
   ```

3. **Redirect to Checkout** function (commented out in `main.js`):
   ```javascript
   stripe.redirectToCheckout({
       lineItems: [{ price: 'price_YOUR_STRIPE_PRICE_ID', quantity: 1 }],
       mode: 'payment',
       successUrl: window.location.origin + '/success',
       cancelUrl: window.location.origin + '/cancel',
   });
   ```

4. **Wire up buttons** — There are 4 CTA buttons:
   - `#nav-checkout-btn` (header nav)
   - `#hero-checkout-btn` (hero section)
   - `#stripe-checkout-btn` (checkout section — primary)
   - `.btn-primary` in `#whats-included` section

5. **For embedded checkout** (optional): Use Stripe's Payment Element or Checkout Session with `window.location.replace()`.

### Build-to-order note

The kit has a 7–10 day build time. If using Stripe:
- Set `payment_intent_data.capture_method = 'manual'` to authorize then capture after build ships
- Or use Stripe's `payment_intent_data.metadata` to track build status
- Consider webhooks to update order status

---

## Placeholders to Replace Before Launch

| Element | Location | Notes |
|---------|----------|-------|
| Product photo | Hero `.product-placeholder` | Replace with real Flipper Zero + Moto G shot |
| Testimonial quotes | `.testimonial-card` | Replace with real customer quotes |
| Testimonial names | `.testimonial-name` | Replace with real attribution |
| Video URL | `.video-qr-placeholder` | Replace with actual setup video URL |
| QR code | `.video-qr-placeholder svg` | Generate real QR code pointing to video |
| Social proof numbers | `.proof-number` | Update with real metrics |
| Privacy Policy URL | Footer legal links | Replace `#` with real URL |
| Terms of Service URL | Footer legal links | Replace `#` with real URL |
| Return Policy URL | Footer legal links | Replace `#` with real URL |

---

## File Structure

```
vesper-ai/
├── web/
│   ├── index.html          # Main landing page (all sections)
│   ├── css/
│   │   └── styles.css      # All styles (~500 lines, responsive)
│   ├── js/
│   │   └── main.js         # FAQ accordion + smooth scroll (~100 lines)
│   └── assets/
│       └── vesper-logo.svg  # SVG logo with V letterform + "vesper AI"
├── docs/
│   └── design-notes.md      # This document
└── PROJECT_PLAN.md         # Product/project plan (from TD)
```

---

## Performance Targets

| Metric | Target | Implementation |
|--------|--------|----------------|
| First Contentful Paint | < 1.2s | Minimal JS, CSS in `<head>`, no blocking resources |
| Largest Contentful Paint | < 2.0s | Hero image is SVG placeholder (fast) |
| Total Blocking Time | < 100ms | No heavy JS; FAQ accordion is ~3KB |
| Cumulative Layout Shift | < 0.05 | Explicit dimensions on images, reserved space |
| Total page weight | < 150KB | Inline SVGs, no external images |

---

## Accessibility

- All interactive elements have `:focus-visible` styles
- FAQ buttons use `aria-expanded` + `aria-controls` correctly
- Color contrast: All text meets WCAG AA (4.5:1 for body, 3:1 for large text)
- Semantic HTML: `<header>`, `<main>`, `<section>`, `<nav>`, `<footer>`, `<button>`
- No `outline: none` without replacement focus styles

---

## Browser Support

- Chrome/Edge 90+
- Firefox 90+
- Safari 14+
- Mobile Safari / Chrome on iOS/Android

No IE11. No legacy browsers.
