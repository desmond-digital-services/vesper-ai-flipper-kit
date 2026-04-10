# RedWand Flipper Kit — Troubleshooting Guide

**What this guide covers:** Solving the most common issues customers run into.
**How to use it:** Find the issue that matches what you're seeing, then try the steps in order.

If a step doesn't work, move to the next one. If you've tried all steps for your issue and it's still not working, contact us at the end of this guide.

---

## Issue 1: Bluetooth Won't Pair

**What you see:** Your phone can't find the Flipper, or it says "Pairing failed" when you try to connect.

### Step 1 — Make sure Bluetooth is on and the Flipper is discoverable

**On the Flipper:**
1. Press the **OK/Select button** to open the main menu
2. Use the arrows to scroll to **Settings**
3. Press **OK/Select**
4. Scroll to **Bluetooth** and press **OK/Select**
5. Make sure it says **"On"** — if not, scroll to "On" and press **OK/Select**
6. Confirm the screen says **"Discoverable"** or shows a Bluetooth symbol

**On your phone:**
1. Go to **Settings > Bluetooth**
2. Confirm Bluetooth is turned **On**

### Step 2 — Restart the Flipper

1. Hold the **power button** on the Flipper for **3 seconds** until the screen goes dark
2. Wait 5 seconds
3. Press the power button once to turn it back on
4. Wait for the main menu to appear (about 5 seconds)
5. Go back to **Settings > Bluetooth** and make sure it's still **On** and **Discoverable**

### Step 3 — Restart your phone's Bluetooth

**On iPhone:**
1. Go to **Settings > Bluetooth**
2. Turn Bluetooth **Off**
3. Wait 10 seconds
4. Turn Bluetooth **On**

**On Android:**
1. Swipe down from the top of the screen
2. Tap the **Bluetooth icon** to turn it off
3. Wait 10 seconds
4. Tap it again to turn it back on

### Step 4 — Forget old Bluetooth connections

If your Flipper was previously paired to this phone, it might be trying to reconnect to the old pairing instead of establishing a fresh one.

**On your phone:**
1. Go to **Settings > Bluetooth**
2. Find **Flipper-XXXX** in the list
3. Tap the **(i)** icon or tap and hold it
4. Tap **Forget This Device** or **Unpair**
5. Now try pairing again from scratch (see Step 1 above)

### Step 5 — Contact support

If you've tried all four steps above and Bluetooth still won't pair, reach out:

📧 **Email:** help@redwand.io
Include: What phone model you're using, what you've tried, and any error messages you've seen.

---

## Issue 2: RedWand App Won't Connect to Flipper

**What you see:** The RedWand app opens but shows "No device connected" or can't find your Flipper, even though Bluetooth is paired.

### Step 1 — Confirm Bluetooth pairing is separate from app connection

Bluetooth pairing (done in your phone's Settings) is different from the RedWand app connection. Both need to work.

1. Go to **Settings > Bluetooth** on your phone
2. Confirm your Flipper shows as **"Connected"** or "Paired" — not just "Available"
3. If it shows as "Available" only, tap it to connect

### Step 2 — Force quit and reopen the RedWand app

1. **On iPhone:** Swipe up from the bottom of the screen (or double-press the home button), find the RedWand app card, and swipe it away. Reopen the app.
2. **On Android:** Tap the **square** button at the bottom of the screen, find the RedWand app card, and swipe it away. Reopen the app.

### Step 3 — Check that the RedWand app has Bluetooth permission

**On iPhone:**
1. Go to **Settings > RedWand** (scroll down to find it)
2. Confirm **Bluetooth** is turned on

**On Android:**
1. Go to **Settings > Apps > RedWand**
2. Tap **Permissions**
3. Confirm **Bluetooth** is allowed

### Step 4 — Restart your phone

If Step 3 doesn't resolve it, a full phone restart often clears up Bluetooth permission issues.

1. Power off your phone completely
2. Wait 10 seconds
3. Power it back on
4. Open the RedWand app and try again

### Step 5 — Contact support

📧 **Email:** help@redwand.io
Include: Your phone model, what you've tried, and any screenshots if possible.

---

## Issue 3: API Key Errors

**What you see:** You see a message like "Invalid API Key," "Connection Failed," or "API Error" when trying to use the AI features.

### Step 1 — Check that your OpenRouter account is active

1. Visit **openrouter.ai** on your phone or computer
2. Log in to your account
3. Check the top of the page — if there's a message about verifying your email or activating your account, do that first

### Step 2 — Verify you copied the full API key

API keys are long. It's easy to miss the first or last character.

1. Go to **openrouter.ai/keys** while logged in
2. Find your key and click to copy it
3. Paste it into a notes app or text field
4. Look at it — does it start with `sk-or-v1-`? Is it complete with no spaces at the start or end?
5. If it looks correct, try copying it again directly from openrouter.ai

### Step 3 — Make sure you're not mixing up keys

If you have multiple API keys (from different services), it's easy to paste the wrong one.

- Confirm the key you're pasting into RedWand starts with `sk-or-v1-`
- Other providers' keys often start differently (e.g., `sk-` for OpenAI, `AIx` for others)

### Step 4 — Check your OpenRouter credit balance

1. Log in to **openrouter.ai**
2. Click on your account or credit balance
3. If your credits are at zero or the account shows as inactive, the key won't work

Getting more credits is usually fast — add a small amount and try again.

### Step 5 — Contact support

📧 **Email:** help@redwand.io
Include: The exact error message you're seeing, whether the key works on openrouter.ai directly, and your phone type.

---

## Issue 4: Flipper Screen Is Unresponsive or Blank

**What you see:** The Flipper screen is dark, frozen, or doesn't respond when you press buttons.

### Step 1 — Check the battery level

1. Look at the battery icon in the top-right corner of the screen
2. If it shows as empty or has a red indicator, **charge the Flipper**
3. Plug the USB-C cable into the Flipper and a power source (computer, wall adapter, or power bank)
4. Let it charge for **at least 15 minutes** before trying to turn it on again

### Step 2 — Force restart the Flipper

1. Hold the **power button** for **10 seconds** continuously — the screen may flicker or go dark
2. Release the power button
3. Wait 5 seconds
4. Press the power button once to turn it back on
5. Wait for the main menu (about 5 seconds)

### Step 3 — Try a different charging cable or power source

If the battery is very low, some cables or power sources may not deliver enough charge.

1. Try a different USB-C cable if you have one
2. Try a wall adapter instead of a computer USB port
3. Make sure the cable is fully inserted into the Flipper

### Step 4 — Contact support

If the screen still doesn't turn on after charging for 30 minutes and trying a force restart:

📧 **Email:** help@redwand.io
Include: Whether the device got wet or was dropped, any error messages seen before it stopped working, and what you've already tried.

---

## Issue 5: Flipper Is Charging but Battery Doesn't Go Up

**What you see:** You plug the Flipper in to charge, but the battery percentage doesn't increase or stays at the same level.

### Step 1 — Check the charging cable and adapter

1. Try a different USB-C cable
2. Try a different power adapter (wall outlet vs. computer USB vs. power bank)
3. Make sure the cable is fully inserted — push it in until you feel it click

### Step 2 — Clean the charging port

Lint and dust can build up in the USB-C port and prevent good contact.

1. Look inside the USB-C port on the Flipper
2. If you see lint, gently blow into the port or use a dry, soft brush (like a clean toothbrush)
3. **Do not** use a metal object — this can damage the contacts

### Step 3 — Let it charge while off

If you're using the Flipper while charging, the battery may charge slowly or not at all.

1. Turn the Flipper off completely (hold power for 3 seconds)
2. Plug it in and let it charge for **at least 1 hour**
3. Check the battery level — it should have gone up noticeably

### Step 4 — Contact support

📧 **Email:** help@redwand.io

---

## Issue 6: Common Error Messages

Here are the error messages you might see and what they mean:

### "Device not found"

**What it means:** The RedWand app can't see your Flipper.
**Try this:**
1. Make sure Bluetooth is turned on in your phone settings
2. Make sure your Flipper is powered on
3. Try force quitting and reopening the RedWand app
4. Restart your phone

---

### "Invalid API Key"

**What it means:** The API key you entered isn't working.
**Try this:**
1. Double-check the key on openrouter.ai — make sure you copied the whole thing
2. Check that your OpenRouter account has credits
3. Try deleting the key and re-entering it in the RedWand app

---

### "Connection timed out"

**What it means:** The app is trying to reach the AI server but taking too long.
**Try this:**
1. Check your internet connection — make sure Wi-Fi or mobile data is on
2. Wait 30 seconds and try again
3. If on public Wi-Fi, try switching to mobile data or a different network

---

### "Bluetooth disconnected"

**What it means:** Your phone lost the Bluetooth connection to the Flipper.
**Try this:**
1. Move your phone closer to the Flipper
2. Turn Bluetooth off and back on
3. Restart the RedWand app
4. If other devices are connected to the same Flipper, disconnect them first

---

### "Card not detected" (shown on Flipper screen)

**What it means:** The SD card isn't being read by the Flipper.
**Try this:**
1. Turn off the Flipper
2. Remove the SD card (push it in until it clicks, then release — it will spring out slightly)
3. Reinsert the SD card firmly until it clicks
4. Turn the Flipper back on
5. If the problem persists, the SD card may need to be reformatted (see Assembly SOP)

---

## When to Contact Support

Contact us if:

- You've tried all the steps for your issue and it's still not working
- Your Flipper was damaged (dropped, wet, cracked screen)
- You see an error message not listed here
- The device gets unusually hot while charging or in use

**How to reach us:**

📧 **Email:** help@redwand.io
We reply within **24 hours** on business days.

**When you email us, please include:**
1. What product you have (RedWand Flipper Kit)
2. What phone or tablet you're using (model name)
3. What step you're on when the issue happens
4. What you've already tried
5. Any screenshots or photos that show the error

---

## Quick Reference — Common Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Screen is dark | Charge for 15 minutes, then restart |
| Bluetooth won't pair | Restart both devices, forget old pairings |
| App can't find Flipper | Force quit app, check Bluetooth is "Connected" not just "Paired" |
| API key error | Re-copy the full key from openrouter.ai, check credits |
| Charging slowly | Charge while the device is off |
| SD card not detected | Remove and reinsert the SD card |
| Connection timed out | Check internet, try again in 30 seconds |

---

*Stuck? We're here to help. Email help@redwand.io — we typically reply within one business day.*
