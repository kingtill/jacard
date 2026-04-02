from flask import Flask, render_template, request, redirect, url_for, send_file, abort
import json
import os
import uuid
from datetime import datetime
import qrcode
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CARDS_FILE = os.path.join(DATA_DIR, 'cards.json')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'static', 'uploads'), exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_cards():
    if not os.path.exists(CARDS_FILE):
        os.makedirs('data', exist_ok=True)
        return {}
    with open(CARDS_FILE, 'r') as f:
        return json.load(f)


def save_cards(cards):
    os.makedirs('data', exist_ok=True)
    with open(CARDS_FILE, 'w') as f:
        json.dump(cards, f, indent=2)


def generate_qr_base64(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=3
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0a0a", back_color="#f0ece4")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    cards = load_cards()
    return render_template('index.html', cards=cards)


@app.route('/card/new', methods=['GET', 'POST'])
def new_card():
    if request.method == 'POST':
        cards = load_cards()
        card_id = str(uuid.uuid4())[:8]

        photo_path = None
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename and allowed_file(photo.filename):
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                ext = photo.filename.rsplit('.', 1)[1].lower()
                filename = f"{card_id}.{ext}"
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                photo_path = f"uploads/{filename}"

        card = {
            'id': card_id,
            'name': request.form.get('name', '').strip(),
            'title': request.form.get('title', '').strip(),
            'company': request.form.get('company', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip(),
            'website': request.form.get('website', '').strip(),
            'linkedin': request.form.get('linkedin', '').strip(),
            'twitter': request.form.get('twitter', '').strip(),
            'instagram': request.form.get('instagram', '').strip(),
            'photo': photo_path,
            'created': datetime.now().strftime('%B %d, %Y')
        }

        cards[card_id] = card
        save_cards(cards)
        return redirect(url_for('view_card', card_id=card_id))

    return render_template('card_form.html', card=None, action='new')


@app.route('/card/<card_id>')
def view_card(card_id):
    cards = load_cards()
    card = cards.get(card_id)
    if not card:
        abort(404)

    card_url = request.url_root.rstrip('/') + url_for('view_card', card_id=card_id)
    qr_code = generate_qr_base64(card_url)

    return render_template('card_view.html', card=card, qr_code=qr_code, card_url=card_url)


@app.route('/card/<card_id>/edit', methods=['GET', 'POST'])
def edit_card(card_id):
    cards = load_cards()
    card = cards.get(card_id)
    if not card:
        abort(404)

    if request.method == 'POST':
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename and allowed_file(photo.filename):
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                ext = photo.filename.rsplit('.', 1)[1].lower()
                filename = f"{card_id}.{ext}"
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                card['photo'] = f"uploads/{filename}"

        card.update({
            'name': request.form.get('name', '').strip(),
            'title': request.form.get('title', '').strip(),
            'company': request.form.get('company', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'email': request.form.get('email', '').strip(),
            'website': request.form.get('website', '').strip(),
            'linkedin': request.form.get('linkedin', '').strip(),
            'twitter': request.form.get('twitter', '').strip(),
            'instagram': request.form.get('instagram', '').strip(),
        })

        cards[card_id] = card
        save_cards(cards)
        return redirect(url_for('view_card', card_id=card_id))

    return render_template('card_form.html', card=card, action='edit')


@app.route('/card/<card_id>/delete', methods=['POST'])
def delete_card(card_id):
    cards = load_cards()
    if card_id in cards:
        # Remove photo file if exists
        card = cards[card_id]
        if card.get('photo'):
            photo_full = os.path.join('static', card['photo'])
            if os.path.exists(photo_full):
                os.remove(photo_full)
        del cards[card_id]
        save_cards(cards)
    return redirect(url_for('index'))


@app.route('/card/<card_id>/vcard')
def download_vcard(card_id):
    cards = load_cards()
    card = cards.get(card_id)
    if not card:
        abort(404)

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{card['name']}",
        f"TITLE:{card['title']}",
        f"ORG:{card['company']}",
    ]
    if card.get('phone'):
        lines.append(f"TEL;TYPE=CELL:{card['phone']}")
    if card.get('email'):
        lines.append(f"EMAIL:{card['email']}")
    if card.get('website'):
        lines.append(f"URL:{card['website']}")
    if card.get('linkedin'):
        lines.append(f"X-SOCIALPROFILE;type=linkedin:{card['linkedin']}")
    if card.get('twitter'):
        lines.append(f"X-SOCIALPROFILE;type=twitter:{card['twitter']}")
    if card.get('instagram'):
        lines.append(f"X-SOCIALPROFILE;type=instagram:{card['instagram']}")
    lines.append("END:VCARD")

    vcard_text = "\r\n".join(lines)
    buffer = io.BytesIO(vcard_text.encode('utf-8'))
    buffer.seek(0)

    safe_name = card['name'].replace(' ', '_') if card['name'] else 'card'
    return send_file(
        buffer,
        mimetype='text/vcard',
        as_attachment=True,
        download_name=f"{safe_name}.vcf"
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
