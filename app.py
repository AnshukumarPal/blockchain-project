from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import datetime
import os
import time
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_change_in_production'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Use absolute path for SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "study_chain.db")}'

# Configure SQLAlchemy engine options
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

# Blockchain Configuration
DIFFICULTY = 3  # Number of leading zeros required in hash
MAX_NONCE = 1000000  # Maximum nonce to try

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Increased length for hash
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    sessions = db.relationship('StudySession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class StudySession(db.Model):
    __tablename__ = 'study_session'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    subject = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    status = db.Column(db.String(20), nullable=False, default='pending')
    
    # Blockchain fields
    block_number = db.Column(db.Integer, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    hash = db.Column(db.String(64), nullable=False, index=True)
    prev_hash = db.Column(db.String(64), nullable=False)
    nonce = db.Column(db.Integer, default=0, nullable=False)
    difficulty = db.Column(db.Integer, default=DIFFICULTY, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'block_number': self.block_number,
            'user_id': self.user_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'subject': self.subject,
            'duration': self.duration,
            'status': self.status,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'hash': self.hash,
            'prev_hash': self.prev_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty
        }
    
    def __repr__(self):
        return f'<Block #{self.block_number} - {self.subject}>'

def calculate_hash(block_number, timestamp, prev_hash, data, nonce, difficulty):
    """Calculate SHA-256 hash for a block"""
    block_data = f"{block_number}{timestamp}{prev_hash}{data}{nonce}{difficulty}"
    return hashlib.sha256(block_data.encode()).hexdigest()

def mine_block(block_number, timestamp, prev_hash, data, difficulty):
    """Proof of Work mining - find a hash with required difficulty"""
    nonce = 0
    target = '0' * difficulty
    
    while nonce < MAX_NONCE:
        hash_result = calculate_hash(block_number, timestamp, prev_hash, data, nonce, difficulty)
        if hash_result.startswith(target):
            return hash_result, nonce
        nonce += 1
    
    # If max nonce reached, return with current hash
    return calculate_hash(block_number, timestamp, prev_hash, data, nonce, difficulty), nonce

def verify_chain(user_id):
    """Verify the integrity of the blockchain for a user"""
    sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.block_number).all()
    
    if not sessions:
        return True, "No blocks to verify"
    
    for i, session in enumerate(sessions):
        # Verify hash
        data = f"{session.date}{session.subject}{session.duration}{session.status}"
        calculated_hash = calculate_hash(
            session.block_number,
            session.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            session.prev_hash,
            data,
            session.nonce,
            session.difficulty
        )
        
        if calculated_hash != session.hash:
            return False, f"Block {session.block_number} has invalid hash"
        
        # Verify chain linkage
        if i > 0:
            if session.prev_hash != sessions[i-1].hash:
                return False, f"Block {session.block_number} has broken chain link"
        
        # Verify proof of work
        if not session.hash.startswith('0' * session.difficulty):
            return False, f"Block {session.block_number} doesn't meet difficulty requirement"
    
    return True, "Blockchain is valid"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username'].strip()
            age = int(request.form['age'])
            password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            # Validation
            if not username or len(username) < 3:
                flash('Username must be at least 3 characters long', 'error')
                return redirect(url_for('register'))
            
            if age < 1 or age > 150:
                flash('Please enter a valid age', 'error')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('register'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'error')
                return redirect(url_for('register'))
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, age=age, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except ValueError:
            flash('Please enter a valid age', 'error')
            return redirect(url_for('register'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        try:
            username = request.form['username'].strip()
            user = User.query.filter_by(username=username).first()
            
            if not user:
                flash('User not found', 'error')
                return redirect(url_for('forget_password'))
            
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return redirect(url_for('forget_password'))
            
            if new_password != confirm_password:
                flash('Passwords do not match', 'error')
                return redirect(url_for('forget_password'))
            
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            
            flash('Password reset successful! Please login with your new password.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Password reset failed: {str(e)}', 'error')
            return redirect(url_for('forget_password'))
    
    return render_template('forget_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash('Please login to continue', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            subject = request.form['subject'].strip()
            duration_unit = request.form['duration_unit']
            duration = int(request.form['duration'])
            
            # Validation
            if not subject:
                flash('Subject cannot be empty', 'error')
                return redirect(url_for('dashboard'))
            
            if duration <= 0:
                flash('Duration must be positive', 'error')
                return redirect(url_for('dashboard'))
            
            if duration_unit == 'hours':
                duration *= 60
            
            status = request.form['status']
            
            # Get previous block with proper locking
            prev_session = StudySession.query.filter_by(user_id=user.id)\
                .order_by(StudySession.block_number.desc()).first()
            prev_hash = prev_session.hash if prev_session else '0' * 64
            block_number = (prev_session.block_number + 1) if prev_session else 1
            
            # Create block data
            timestamp = datetime.datetime.utcnow()
            data = f"{date}{subject}{duration}{status}"
            
            # Mine the block (Proof of Work)
            hash_val, nonce = mine_block(
                block_number,
                timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                prev_hash,
                data,
                DIFFICULTY
            )
            
            # Create new session
            new_session = StudySession(
                user_id=user.id,
                date=date,
                subject=subject,
                duration=duration,
                status=status,
                block_number=block_number,
                timestamp=timestamp,
                hash=hash_val,
                prev_hash=prev_hash,
                nonce=nonce,
                difficulty=DIFFICULTY
            )
            
            db.session.add(new_session)
            db.session.commit()
            
            flash(f'Block #{block_number} mined successfully! (Nonce: {nonce})', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash(f'Invalid input: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to add session: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    
    # Fetch sessions
    sessions = StudySession.query.filter_by(user_id=user.id)\
        .order_by(StudySession.block_number.desc()).all()
    
    # Calculate statistics
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.status == 'completed'])
    pending_sessions = len([s for s in sessions if s.status == 'pending'])
    total_study_time = sum(s.duration for s in sessions)
    total_study_hours = total_study_time / 60
    
    avg_study_time = total_study_time / total_sessions if total_sessions > 0 else 0
    
    # Find most studied subject
    subject_counts = {}
    for s in sessions:
        subject_counts[s.subject] = subject_counts.get(s.subject, 0) + s.duration
    favorite_subject = max(subject_counts.items(), key=lambda x: x[1])[0] if subject_counts else "None"
    
    # Calculate study streak
    if sessions:
        unique_dates = sorted(set(s.date for s in sessions), reverse=True)
        streak = 0
        current_date = datetime.date.today()
        for i, date in enumerate(unique_dates):
            if date == current_date - datetime.timedelta(days=i):
                streak += 1
            else:
                break
    else:
        streak = 0
    
    # Verify blockchain
    is_valid, message = verify_chain(user.id)
    
    stats = {
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'pending_sessions': pending_sessions,
        'total_study_hours': round(total_study_hours, 1),
        'avg_study_time': round(avg_study_time, 0),
        'favorite_subject': favorite_subject,
        'streak': streak,
        'blockchain_valid': is_valid,
        'blockchain_message': message,
        'total_blocks': total_sessions
    }
    
    today_date = datetime.date.today().strftime('%Y-%m-%d')
    
    return render_template('dashboard.html',
                         user=user,
                         sessions=sessions,
                         stats=stats,
                         today_date=today_date)

@app.route('/blockchain')
def blockchain():
    if 'user_id' not in session:
        flash('Please login to continue', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please login again.', 'error')
        return redirect(url_for('login'))
    
    sessions = StudySession.query.filter_by(user_id=user.id)\
        .order_by(StudySession.block_number).all()
    
    is_valid, message = verify_chain(user.id)
    
    return render_template('blockchain.html',
                         user=user,
                         sessions=sessions,
                         is_valid=is_valid,
                         message=message)

@app.route('/api/verify_chain')
def api_verify_chain():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    is_valid, message = verify_chain(session['user_id'])
    return jsonify({'valid': is_valid, 'message': message})

@app.route('/update_status/<int:session_id>', methods=['POST'])
def update_status(session_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        session_obj = StudySession.query.get(session_id)
        if session_obj and session_obj.user_id == session['user_id']:
            session_obj.status = 'completed'
            db.session.commit()
            flash('Session marked as completed!', 'success')
        else:
            flash('Session not found', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update session: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/delete_session/<int:session_id>', methods=['POST'])
def delete_session(session_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    flash('⚠️ Warning: Deleting blocks from a blockchain breaks the chain integrity!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    username = session.get('username', 'User')
    session.clear()
    flash(f'Goodbye, {username}!', 'success')
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('login.html'), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('login'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully!")
        print(f"📁 Database location: {os.path.join(basedir, 'instance', 'study_chain.db')}")
        print(f"🔗 Blockchain difficulty: {DIFFICULTY} leading zeros")
        print(f"⛏️  Max mining attempts: {MAX_NONCE}")
    app.run(debug=True)