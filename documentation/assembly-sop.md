# Vesper AI Flipper Kit — Assembly SOP (For TD)

**Purpose:** Step-by-step guide for assembling and configuring each Vesper AI Flipper Kit before it ships to a customer.

**Time Estimate:** 20–30 minutes per kit
**Performed by:** TD or authorized assembler

---

## Pre-Assembly Checklist

Gather the following before starting:

- [ ] Flipper Zero device (or compatible unit)
- [ ] SanDisk (or equivalent) microSD card — **32GB or smaller, formatted FAT32**
- [ ] Moto G Play phone (or equivalent Android device — provisioned per kit)
- [ ] USB-A to USB-C cable (for Flipper charging/data)
- [ ] USB-A to micro-USB cable (for Moto G charging)
- [ ] Vesper APK installer file (latest build, provided by developer)
- [ ] FAT32 formatting tool (see Step 1)
- [ ] Customer API key (generated during customer onboarding) — **leave blank for customer to enter**
- [ ] Factory reset completed (per Step 7)
- [ ] Clean workspace with good lighting

---

## Step 1: Format the SD Card (FAT32)

**⚠️ Important:** The Flipper requires a FAT32-formatted SD card. exFAT and NTFS are not supported.

### On macOS:

1. Insert the microSD card into your computer (use an adapter if needed)
2. Open **Disk Utility** (press Cmd + Space, type "Disk Utility")
3. Select the SD card from the list on the left
4. Click **"Erase"** at the top
5. In the popup:
   - **Name:** `flipper` (lowercase, no spaces)
   - **Format:** **MS-DOS (FAT32)**
   - **Scheme:** Master Boot Record
6. Click **"Erase"** and wait for the process to complete
7. Close Disk Utility

### On Windows:

1. Insert the SD card
2. Press **Win + X** and open **Disk Management**
3. Find your SD card in the list
4. Right-click the partition and select **"Format"**
5. In the popup:
   - **File System:** **FAT32**
   - **Volume Label:** `flipper`
6. Check **"Quick Format"**
7. Click **OK**

### On Linux:

```bash
# Find the SD card device name
lsblk

# Unmount if mounted (replace sdX with your device)
umount /dev/sdX1

# Format as FAT32
sudo mkfs.fat -F 32 /dev/sdX1

# Label it
sudo dosfslabel /dev/sdX1 flipper
```

**Verification:** After formatting, confirm the card shows up as `flipper` with FAT32 format. If the card is larger than 32GB, the FAT32 option may not appear in Disk Utility on macOS — use a 32GB or smaller card.

---

## Step 2: Insert SD Card into Flipper

1. Locate the SD card slot on the **back** of the Flipper (near the bottom)
2. Push the card gently into the slot until it clicks into place
3. The card sits flush with the back panel — do not force it
4. Confirm the card is seated by trying to pull it out lightly (it should resist until you press to release)

> **Note:** Some Flipper units have the SD card pre-installed. Confirm it is seated before proceeding.

---

## Step 3: Sideload Vesper APK onto Moto G Play

The Moto G Play phone comes pre-loaded with the Vesper app. Use this step if you need to reinstall or update it.

### Enable Developer Mode on Moto G Play:

1. Open **Settings** on the Moto G Play
2. Scroll to **"About phone"** (at the bottom)
3. Find **"Build number"**
4. Tap **Build number** 7 times
5. You see a message: **"You are now a developer!"**
6. Go back to **Settings**
7. Tap **"System"** > **"Advanced"** > **"Developer options"**
8. Find **"USB debugging"** — toggle it **On**
9. Confirm the warning if prompted

### Transfer and Install the APK:

**Option A — Using ADB (recommended for speed):**
```bash
# Connect Moto G Play to your computer via USB
# Make sure ADB is installed

adb devices
# You should see your device listed

adb install vesper-app.apk
# Wait for "Success" message
```

**Option B — Direct file transfer:**
1. Connect Moto G Play to your computer via USB cable
2. On the phone, swipe down from the top and select **"USB for charging"**
3. Tap to change it to **"File Transfer"**
4. Copy the `vesper-app.apk` file to the phone's Downloads folder
5. On the phone, open **Files** or **Downloads**
6. Tap the APK file
7. If prompted, tap **"Install anyway"** (the phone may warn about unknown apps — this is normal for sideloaded apps)
8. Wait for installation to complete
9. Tap **"Open"** once done

**Verify installation:** Find the Vesper app icon in your app drawer. Tap it to confirm it opens.

---

## Step 4: Initial Power-On Test

Perform this test for every Flipper unit before it ships.

1. **Switch the battery ON** (slide the battery switch to the ON position)
2. **Power on the Flipper** — press and hold the power button for 2 seconds
3. **Confirm the following:**
   - [ ] Screen turns on and shows the main menu
   - [ ] Battery icon in the top-right shows a charge level (may be low — that's fine)
   - [ ] No error messages on screen
   - [ ] SD card is recognized — go to **Settings > Storage** and confirm it shows the SD card capacity
4. **Test basic navigation:**
   - Use the arrow pad to scroll through the menu
   - Press **OK/Select** on a menu item
   - Press **Back** to return
5. **Power off the Flipper** — hold the power button for 3 seconds until the screen goes dark

> **FAIL condition:** If the screen does not turn on, the SD card is not recognized, or error messages appear, do not ship the unit. Flag for repair or replacement.

---

## Step 5: BLE Pairing Verification

Confirm that the Flipper's Bluetooth Low Energy (BLE) connection is functioning.

1. Power on the Flipper
2. Go to **Settings > Bluetooth**
3. Confirm Bluetooth is **On** and set to **Discoverable**
4. On the Moto G Play (or your test phone):
   - Open **Settings > Bluetooth**
   - Confirm the Flipper appears in the device list (named something like `Flipper-XXXX`)
   - Tap to **Pair** and confirm pairing succeeds
5. In the Vesper app on the Moto G Play:
   - Open the app
   - Confirm the app detects the paired Flipper
   - Attempt to **Connect** from within the app
6. Confirm the connection stays stable for at least 30 seconds

**Verification checklist:**
- [ ] Flipper visible in phone's Bluetooth settings
- [ ] Pairing succeeds without error
- [ ] Vesper app connects to Flipper
- [ ] Connection does not drop during normal use

> **FAIL condition:** If the app cannot connect or the connection drops repeatedly, check battery level and try again. If the issue persists, do not ship the unit.

---

## Step 6: API Key Entry (Test Key — Not Customer's Key)

Use a test API key to verify the AI integration works end-to-end. **Do not enter the customer's key during assembly.**

1. In the Vesper app, go to **Settings** or **API Configuration**
2. Enter a test OpenRouter API key (provided internally for QA)
3. Tap **Save** or **Connect**
4. Confirm the app shows **"Connected"** or **"Ready"**
5. Send a test command in the app: **"Hello, testing"**
6. Confirm the Flipper responds or the app returns a response

**Verification checklist:**
- [ ] API key accepted (no "Invalid Key" error)
- [ ] AI responds to test command
- [ ] Response appears within a reasonable time (under 10 seconds)

> **Note:** The Moto G Play should be connected to Wi-Fi for this step. Confirm Wi-Fi is working before testing the API connection.

---

## Step 7: Factory Reset (For Customer Privacy)

**⚠️ Critical:** Perform this step immediately before packaging the kit. This ensures no test data, test accounts, or test Bluetooth pairings remain on the device.

### On the Flipper:

1. Go to **Settings**
2. Scroll to **"System"** or **"Reset"**
3. Select **"Factory Reset"** or **"Full Reset"**
4. Confirm the reset
5. Wait for the Flipper to restart

### On the Moto G Play:

1. Open **Settings > System > Reset options**
2. Tap **"Erase all data (factory reset)"**
3. Confirm
4. Wait for the phone to restart
5. On the setup screen, **do not complete the setup** — leave it at the welcome screen
6. **Do not sign in** to a Google account — leave the Google account prompt at the welcome screen

### Verify Factory Reset:

- **Flipper:** Confirms no paired devices, no saved data, returns to first-run state
- **Moto G Play:** Confirms no apps installed (except system apps), no Google account signed in, no personal data present

> **FAIL condition:** If any data, accounts, or pairings remain visible after reset, do not ship. Re-reset and recheck.

---

## Step 8: Quality Control Checklist

Complete this checklist before sealing and shipping the kit.

### Flipper Unit:
- [ ] Battery switched ON (ship with battery ON for customer convenience)
- [ ] SD card inserted and seated properly
- [ ] Screen turns on with no errors
- [ ] Navigation buttons all functional
- [ ] Bluetooth is ON and discoverable
- [ ] No visible cracks, scratches, or damage to screen or body
- [ ] USB-C port is clean and undamaged
- [ ] Factory reset confirmed — no test data remaining

### Moto G Play Phone:
- [ ] Factory reset confirmed — no Google account, no personal data
- [ ] Vesper APK installed and opens correctly
- [ ] USB debugging enabled (optional but helpful for customer support)
- [ ] Screen turns on with no errors
- [ ] No visible cracks or damage
- [ ] USB port is clean
- [ ] Charger cable included and functional

### Documentation:
- [ ] Quick-start instruction card included in box
- [ ] All accessories present (cables, etc.)
- [ ] Kit box is clean and undamaged

### Sealing:
- [ ] All components secured in box
- [ ] Box sealed properly
- [ ] Shipping label applied correctly

---

## Common Issues and Resolutions

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| SD card not recognized | Wrong format (not FAT32) | Re-format as FAT32 using Step 1 |
| SD card not recognized | Card too large (>32GB) | Use a 32GB or smaller card |
| Moto G won't accept APK | USB debugging off | Enable in Developer Options |
| Moto G won't accept APK | Security block | Enable "Install unknown apps" in settings |
| API test fails | No internet on Moto G | Connect to Wi-Fi |
| API test fails | Test key expired | Request new test key from developer |
| Factory reset fails | Battery critically low | Charge Flipper before resetting |
| Bluetooth not visible | Flipper in sleep mode | Wake Flipper, re-enable Bluetooth |

---

## Contact for Issues

If you encounter a problem you cannot resolve during assembly:

- **Internal support:** Check with the developer team
- **Hardware defects:** Flag unit, do not ship, contact supplier
- **APK issues:** Request a fresh APK build from developer

---

*Assembly should be completed with care. A properly assembled kit = a happy customer on the other end.*
