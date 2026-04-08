# Vesper AI Flipper Kit — Instruction Card Design Spec

**Document type:** Design specification for printed quick-start card
**Card size:** 3.5 inches × 2 inches (standard business card size, landscape orientation)
**Print orientation:** Double-sided (front and back)
**Material suggestion:** 14pt or 16pt matte cardstock, rounded corners
**Finish:** Optional soft-touch laminate for premium feel

---

## Card Overview

This card is the first physical thing a customer sees when they open the box. It needs to:
1. Communicate confidence and quality
2. Get the customer started in under 60 seconds
3. Direct them to help if they need it

The card is not the full manual — it's a cheat sheet with QR codes for everything else.

---

## Front Side (Side A) — "You're Ready to Go"

### Layout Zones

**Top zone — Logo and tagline (top 30% of card):**

- **Logo:** Vesper logo — centered, approximately 1 inch wide
- **Tagline below logo:** *"Your AI, in your hand."* in a clean sans-serif font
- **Product name below tagline:** "AI Flipper Kit" in a smaller, lighter weight

*Visual description:* A clean, minimal header area. Dark background (#0A0A0A or deep navy) with white or light text. Gives the card a premium feel.

---

**Middle zone — Quick Start Checklist (middle 45% of card):**

A numbered checklist, bold and scannable. Large font — customer should be able to read this without glasses if needed.

```
1.  Switch battery ON
2.  Connect via Bluetooth
3.  Open the Vesper app
4.  Add your API key
5.  Say "Read this card"
```

**Font:** Bold, sans-serif, 10–11pt minimum
**Spacing:** Each line should have breathing room — 1.5x line height
**Color:** Black or dark charcoal text on light/white background for contrast

---

**Bottom zone — QR Code + Label (bottom 25% of card):**

- **QR code (left):** Links to the setup video
  - Size: 0.75 inch × 0.75 inch
  - Surrounding border: 0.1 inch quiet zone (white space)
  - Below QR code: small label text — *"Watch Setup Video"*
- **QR code (right):** Links to the troubleshooting guide
  - Size: 0.75 inch × 0.75 inch
  - Surrounding border: 0.1 inch quiet zone
  - Below QR code: small label text — *"Need Help?"*

**QR code style:** High-contrast black on white. Do not use colored QR codes — reduce scan reliability.

---

### Front Side Color Palette

| Element | Color | Notes |
|---------|-------|-------|
| Background | White (#FFFFFF) | Clean, high-contrast base |
| Header area | Deep charcoal (#1A1A1A) | Premium feel, use for top band |
| Header text | White (#FFFFFF) | Logo and tagline |
| Checklist numbers | Brand accent (e.g., teal #00B5A6) | Draws eye to steps |
| Checklist text | Near-black (#2D2D2D) | Easy to read |
| QR code | Black (#000000) on white | Maximum scan reliability |

---

## Back Side (Side B) — "Support & Legal"

### Layout Zones

**Top zone — Support Information (top 50% of card):**

- **Email:** help@vespere.ai (large, bold, easy to read)
- **Website:** vespere.ai (below email)
- **Support hours:** "We reply within 24 hours" (small, below website)

**Visual:** Clean, centered. White background with dark text. Simple and trustworthy.

---

**Middle zone — QR Code to Full Documentation (center):**

- **Single QR code,** centered, 0.9 inch × 0.9 inch
- Label above QR: *"Full Guide & Troubleshooting"*
- Links to: the full online documentation or support page

---

**Bottom zone — Legal / Responsible Use reminder (bottom 25%):**

Small, subtle text. Does not need to be prominent — just present.

```
Use responsibly. Do not use to access systems,
networks, or data you don't have permission to use.
See vespere.ai/responsible-use for full policy.
```

**Font size:** 6–7pt. Use a light gray (#888888) so it's there but not alarming.

---

### Back Side Color Palette

| Element | Color | Notes |
|---------|-------|-------|
| Background | White (#FFFFFF) | Consistent with front |
| Support email | Dark charcoal (#1A1A1A) | Prominent, confident |
| Website | Medium gray (#555555) | Secondary to email |
| QR code label | Medium gray (#555555) | Clear but not dominant |
| QR code | Black (#000000) on white | Standard scan reliability |
| Legal text | Light gray (#888888) | Subtle, not alarming |

---

## Print Specifications

### File Requirements
- **Format:** PDF (print-ready) or high-resolution PNG at 600 DPI
- **Bleed:** 0.125 inch on all sides (add to card size — final trim is 3.5" × 2")
- **Safe zone:** Keep all critical text and QR codes at least 0.15 inch from the trim edge

### Recommended Specs
- **Paper:** 16pt matte cardstock
- **Finish:** Soft-touch laminate on both sides (improves durability, feels premium)
- **Corners:** Rounded (0.125 inch radius) — matches consumer electronics aesthetic
- **Quantity recommendation:** Print in batches of 500–1000 for cost efficiency

### Color Space
- Use **CMYK** for print production
- Convert any RGB elements to CMYK before sending to printer
- Run a test print on standard paper before full production run

---

## Visual Reference — Front Side (Side A)

```
┌─────────────────────────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │  ← Dark charcoal band
│                                                         │
│              [VESPER LOGO]                             │
│          "Your AI, in your hand."                      │
│              AI Flipper Kit                            │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│                   1.  Switch battery ON                 │
│                   2.  Connect via Bluetooth            │
│                   3.  Open the Vesper app              │
│                   4.  Add your API key                  │
│                   5.  Say "Read this card"              │
│                                                         │
│                                                         │
│   ┌──────────┐              ┌──────────┐              │
│   │ ▓▓▓▓▓▓▓▓ │              │ ▓▓▓▓▓▓▓▓ │              │
│   │ ▓▓▓▓▓▓▓▓ │  ← QR code   │ ▓▓▓▓▓▓▓▓ │  ← QR code  │
│   │ ▓▓▓▓▓▓▓▓ │              │ ▓▓▓▓▓▓▓▓ │              │
│   └──────────┘              └──────────┘              │
│  "Watch Setup    "Need Help?"                         │
│     Video"                                            │
└─────────────────────────────────────────────────────────┘
```

---

## Visual Reference — Back Side (Side B)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                                                         │
│                  help@vespere.ai                       │
│                   vespere.ai                           │
│            We reply within 24 hours.                   │
│                                                         │
│                                                         │
│                  ┌──────────────┐                     │
│                  │ ▓▓▓▓▓▓▓▓▓▓▓ │                     │
│                  │ ▓▓▓▓▓▓▓▓▓▓▓ │  ← QR code          │
│                  │ ▓▓▓▓▓▓▓▓▓▓▓ │                     │
│                  └──────────────┘                     │
│            "Full Guide & Troubleshooting"              │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│   Use responsibly. Do not use to access systems,       │
│   networks, or data you don't have permission to use. │
│   See vespere.ai/responsible-use for full policy.    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## QR Code Destinations

| QR Code | Destination URL | Notes |
|---------|-----------------|-------|
| Front — Setup Video | `https://vespere.ai/setup-video` | Host a video walkthrough here |
| Front — Need Help? | `https://vespere.ai/troubleshooting` | Link to troubleshooting page |
| Back — Full Guide | `https://vespere.ai/docs` | Link to all documentation |

> **URLs above are placeholders.** Confirm final URLs with your web team before sending to print.

---

## Accessibility Notes

- Minimum font size for any text: **7pt** (legal text can be 6pt)
- QR codes must be at least **0.75 inch** for reliable scanning on most phones
- Maintain high contrast ratios — black on white, or dark on light
- Do not rely on color alone to convey meaning — use text labels alongside QR codes

---

## Designer Checklist

Before sending to print, confirm:
- [ ] All four QR codes scan correctly (test with 3 different phones)
- [ ] All URLs are correct and live
- [ ] Colors are converted to CMYK
- [ ] Bleed is set to 0.125 inch
- [ ] Safe zone respected (0.15 inch from trim)
- [ ] Rounded corners applied (0.125 inch radius)
- [ ] Proofread all text — no typos
- [ ] Legal text on back is accurate and up to date

---

*Questions about the design spec? Reach out to help@vespere.ai*
