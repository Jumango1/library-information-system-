# Public Access Setup

## Option 1: ngrok (Recommended)

### Step 1: Download ngrok

1. Open https://ngrok.com/download
2. Choose **Windows (64-bit)**
3. Download ZIP file

### Step 2: Extract

Extract `ngrok.exe` to project folder: `C:\Users\Penisan\library-information-system\`

### Step 3: Register (free)

- Open: https://dashboard.ngrok.com/signup
- Register via Google/GitHub
- Copy **authtoken** from: https://dashboard.ngrok.com/get-started/your-authtoken

### Step 4: Configure authtoken

Open command prompt in folder with `ngrok.exe`:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Step 5: Start tunnel

```bash
ngrok http 80
```

### Step 6: Get public URL

You will see:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:80
```

**This URL is publicly accessible.**

---

## Option 2: Cloudflare Tunnel

### Installation

```bash
# Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Run
cloudflared tunnel --url http://localhost:80
```

---

## Option 3: Local Network

If on same Wi-Fi network:

```bash
# Get your IP
ipconfig

# Find IPv4 address (e.g., 192.168.1.100)
# Access via: http://192.168.1.100
```

---

## Quick Command (after setup)

Just run in folder with ngrok.exe:
```bash
ngrok http 80
```

Get public URL for remote access.
