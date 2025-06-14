from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os
from datetime import datetime
from models import db, User, Incident, ChatMessage

app = Flask(__name__)
app.config['SECRET_KEY'] = '5ee52e4c1eb3af0dcd2f287972b0c17d0629fd45830f78f539810e5cb05963fd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crime_alert.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
db.init_app(app)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Create DB tables
with app.app_context():
    db.create_all()
    # Create admin if not exists
    if not User.query.filter_by(email='admin@admin.com').first():
        admin = User(name='Admin', email='admin@admin.com', password=generate_password_hash('admin123'), is_admin=True)
        db.session.add(admin)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Serve static uploads
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Home page (map)
@app.route('/')
@login_required
def home():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        hashed_pw = generate_password_hash(data['password'])
        user = User(name=data['name'], email=data['email'], password=hashed_pw, phone=data['phone'], address=data.get('address', ''))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if user and check_password_hash(user.password, data['password']):
            login_user(user)
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Incident report page
@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if request.method == 'POST':
        data = request.form
        file = request.files.get('media')
        filename = None
        if file and file.filename:
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        incident = Incident(
            type=data['type'],
            location=data['location'],
            lat=float(data['lat']),
            lng=float(data['lng']),
            description=data['description'],
            media=filename,
            time=datetime.now().strftime('%Y-%m-%d %H:%M'),
            user_id=current_user.id
        )
        db.session.add(incident)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('report.html')

# API: Get incidents
@app.route('/api/incidents')
def api_incidents():
    incidents = Incident.query.order_by(Incident.time.desc()).all()
    return jsonify([{
        'id': i.id,
        'type': i.type,
        'location': i.location,
        'lat': i.lat,
        'lng': i.lng,
        'description': i.description,
        'media': i.media,
        'time': i.time,
        'verified': i.verified
    } for i in incidents])

# API: Submit incident (AJAX)
@app.route('/api/report', methods=['POST'])
@login_required
def api_report():
    data = request.json
    incident = Incident(
        type=data['type'],
        location=data['location'],
        lat=data['lat'],
        lng=data['lng'],
        description=data['description'],
        time=datetime.now().strftime('%Y-%m-%d %H:%M'),
        user_id=current_user.id
    )
    db.session.add(incident)
    db.session.commit()
    return jsonify({'message': 'Incident reported'})

# Community chat
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        msg = ChatMessage(user=current_user.name, message=request.form['message'], time=datetime.now().strftime('%H:%M'))
        db.session.add(msg)
        db.session.commit()
    messages = ChatMessage.query.order_by(ChatMessage.time.desc()).limit(50).all()
    return render_template('chat.html', messages=messages[::-1])

# API: Get chat messages
@app.route('/api/chat')
def api_chat():
    messages = ChatMessage.query.order_by(ChatMessage.time.desc()).limit(50).all()
    return jsonify([{'user': m.user, 'message': m.message, 'time': m.time} for m in messages[::-1]])

# SOS page
@app.route('/sos', methods=['GET', 'POST'])
@login_required
def sos():
    if request.method == 'POST':
        # Here you would send SMS/email to emergency contacts
        return render_template('sos.html', sent=True)
    return render_template('sos.html')

# Admin panel
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    incidents = Incident.query.order_by(Incident.time.desc()).all()
    return render_template('admin.html', incidents=incidents)

# API: Verify incident
@app.route('/api/admin/verify', methods=['POST'])
@login_required
def api_admin_verify():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    incident = Incident.query.get(data['id'])
    incident.verified = data['verified']
    db.session.commit()
    return jsonify({'message': 'Incident updated'})

if __name__ == '__main__':
    import webbrowser
    import threading
    port = int(os.environ.get("PORT", 10000))
    url = f"http://127.0.0.1:{port}/login"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    app.run(host='0.0.0.0', port=port)