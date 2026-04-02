# CardForge — Digital Business Card App

A Flask web app to create, manage, and share digital business cards via NFC tags and QR codes.

---

## Setup

### 1. Install Python (3.10+)
Download from https://python.org if not already installed.

### 2. Install dependencies
Open a terminal in this folder and run:
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

Open your browser to: **http://localhost:5000**

---

## Features
- Create multiple business cards with photo, contact info, and social links
- Each card gets a unique shareable URL
- QR code auto-generated for every card
- Download vCard (.vcf) for saving to contacts
- Cards stored locally in `data/cards.json`

---

## Sharing via NFC (iPhone)

1. Create your card and copy the share link
2. Download **NFC Tools** (free) from the App Store
3. Open NFC Tools → Write → Add a Record → URL/URI
4. Paste your share link → Write → tap your iPhone to a blank NFC sticker
5. Anyone who taps the sticker will see your card in their browser instantly

**Tip:** NFC stickers are cheap — search "NFC215 sticker" on Amazon (~$10 for 20).

---

## Sharing via QR Code
Every card page shows a scannable QR code. Works with any phone camera — no app needed.

---

## Making It Public (Optional)
To share cards with people outside your local network, deploy to a free host:

- **Render.com** — free tier, easy Flask deploy
- **Railway.app** — free tier, simple setup
- **PythonAnywhere.com** — free tier, Python-focused

Once deployed, replace `localhost:5000` with your public URL.

---

## Project Structure
```
digital_business_card/
├── app.py               # Flask backend
├── requirements.txt     # Python packages
├── data/
│   └── cards.json       # Card data storage (auto-created)
├── static/
│   └── uploads/         # Uploaded photos (auto-created)
└── templates/
    ├── base.html        # Shared layout & styles
    ├── index.html       # Card dashboard
    ├── card_form.html   # Create / Edit form
    └── card_view.html   # Public card + share tools
```
