# 🔗 StudyChain - Blockchain-Based Study Tracker

A modern, secure study tracking application that leverages blockchain technology with Proof of Work (PoW) consensus mechanism to create an immutable record of your study sessions.

![Blockchain](https://img.shields.io/badge/Blockchain-Enabled-00D4FF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## ✨ Key Features

### 🔐 Blockchain Technology
- **SHA-256 Cryptographic Hashing**: Each study session is secured with SHA-256
- **Proof of Work (PoW)**: Mining mechanism with configurable difficulty
- **Chain Integrity Verification**: Real-time blockchain validation
- **Immutable Records**: Cannot alter past study sessions without breaking the chain
- **Block Explorer**: Visualize your entire study blockchain

### 📊 Study Tracking
- Track study sessions with subject, duration, and status
- View detailed statistics (total hours, streaks, favorite subjects)
- Pending and completed session management
- Date-wise organization of study records

### 🎨 Modern UI/UX
- **Glassmorphism Design**: Beautiful frosted-glass aesthetic
- **Animated Gradients**: Dynamic background animations
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Blockchain Theme**: Cyan/purple color scheme representing blockchain
- **Interactive Elements**: Hover effects, smooth transitions
- **Visual Feedback**: Flash messages, loading states

### 🔒 Security Features
- Password hashing with pbkdf2:sha256
- Session-based authentication
- SQL injection protection via SQLAlchemy ORM
- Input validation and sanitization
- Database foreign key constraints

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd study-chain
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running quick Python checks in PowerShell

PowerShell does not support Unix-style here-doc `<<'PY'` used in bash; instead run one-liners with `-c` or enter the interactive shell:

```pwsh
# One-liner in PS (recommended for quick checks)
venv\Scripts\python.exe -c "import hashlib; print('SHA256:', hashlib.sha256(b'test').hexdigest())"

# Launch interactive Python shell and run multiple lines:
venv\Scripts\python.exe
>>> import hashlib
>>> print('SHA256:', hashlib.sha256(b'test').hexdigest())
```

⚠️ If you see an error like `Error: pg_config executable not found` while installing `psycopg2-binary`, it means pip tried to build psycopg2 from source because a prebuilt binary wheel wasn't available for your Python version and platform. You have a few simple options:

- If you don't need PostgreSQL locally for development, remove or comment out `psycopg2-binary` from `requirements.txt` and re-run `pip install -r requirements.txt` (the app defaults to SQLite).
- If you want PostgreSQL and want a binary wheel: update `requirements.txt` to a newer `psycopg2-binary` version with wheels for your Python version (e.g. `psycopg2-binary==2.9.11`) and try again.
- If you must build from source on Windows: install PostgreSQL (https://www.postgresql.org/download/windows/) and add its `bin` folder to your `PATH` so `pg_config` is found. Also install Microsoft Visual C++ Build Tools.
PowerShell example (to get `pg_config` path into PATH):
```pwsh
# If PostgreSQL is installed under C:\Program Files\PostgreSQL\17\
$env:Path += ";C:\Program Files\PostgreSQL\17\bin"
pip install -r requirements.txt
```

Tip: If you can, prefer `psycopg[binary]` (psycopg v3) for modern projects — it has binary wheels and is the successor to psycopg2.
_If you encounter an error like `ERROR: No matching distribution found for hashlib-md5==0.1.1`, it means `hashlib-md5` (a third-party wrapper) isn't available on PyPI. Python provides `hashlib` in the standard library, so remove any `hashlib-md5` entry from `requirements.txt` and re-run the install._

_Security tip: MD5 is weak and not recommended for password hashing. Use `hashlib.sha256()` or stronger hashing/password libraries (e.g., `bcrypt`, `argon2`) for secure data handling._

4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
study-chain/
├── app.py                  # Main Flask application with blockchain logic
├── requirements.txt        # Python dependencies
├── instance/
│   └── study_chain.db     # SQLite database (auto-created)
├── static/
│   ├── style.css          # Modern blockchain-themed CSS
│   └── script.js          # Frontend JavaScript
└── templates/
    ├── base.html          # Base template with layout
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── forget_password.html
    ├── dashboard.html     # Main dashboard with stats
    └── blockchain.html    # Blockchain explorer
```

## 🔧 Configuration

### Blockchain Settings (in `app.py`)

```python
DIFFICULTY = 3          # Number of leading zeros required
MAX_NONCE = 1000000    # Maximum nonce attempts
```

### Database Settings
```python
# Default: SQLite in instance/ folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/study_chain.db'

# For production, use PostgreSQL:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/dbname'
```

## 📊 Database Schema

### User Table
- `id` (Primary Key)
- `username` (Unique, Indexed)
- `age`
- `password` (Hashed)
- `created_at`

### StudySession Table (Blockchain Blocks)
- `id` (Primary Key)
- `user_id` (Foreign Key, Indexed)
- `block_number` (Sequential)
- `date` (Indexed)
- `subject`
- `duration` (minutes)
- `status` (pending/completed)
- `timestamp` (UTC)
- `hash` (SHA-256, 64 chars)
- `prev_hash` (Link to previous block)
- `nonce` (Proof of Work)
- `difficulty` (PoW difficulty level)

## 🎯 How It Works

### Blockchain Mechanism

1. **Block Creation**: When you add a study session
   - System fetches the previous block's hash
   - Creates new block with incremented number
   - Includes study data (date, subject, duration, status)

2. **Proof of Work Mining**:
   - System attempts to find a hash with required leading zeros
   - Tries different nonce values until valid hash is found
   - This makes tampering computationally expensive

3. **Chain Linkage**:
   - Each block stores previous block's hash
   - Forms an immutable chain
   - Any modification breaks subsequent blocks

4. **Verification**:
   - System can verify entire chain integrity
   - Checks: hash validity, chain linkage, PoW compliance

### Security Benefits

- **Immutability**: Cannot change past records without detection
- **Transparency**: Full blockchain history visible
- **Cryptographic Security**: SHA-256 hashing
- **Tamper-Evident**: Breaking chain is immediately visible

## 💡 Suggested Improvements & Features

### 🔥 High Priority

1. **Export Functionality**
   - Export blockchain as JSON
   - Generate PDF reports
   - CSV export for data analysis

2. **Advanced Analytics**
   - Weekly/Monthly charts
   - Subject-wise time distribution
   - Productivity heatmaps
   - Goal tracking

3. **Notifications & Reminders**
   - Email reminders for pending sessions
   - Push notifications
   - Daily/Weekly summaries

4. **Enhanced Security**
   - Two-factor authentication (2FA)
   - Password strength requirements
   - Account recovery via email
   - Rate limiting for login attempts

### 🎨 UI/UX Enhancements

5. **Dark/Light Mode Toggle**
   - User preference storage
   - Smooth theme transitions
   - System preference detection

6. **Interactive Charts**
   - Real-time Chart.js graphs
   - Filterable by date range
   - Subject comparison charts
   - Progress visualizations

7. **Drag & Drop**
   - Rearrange dashboard widgets
   - Customizable layout
   - Save user preferences

8. **Mobile App**
   - React Native or Flutter
   - Offline mode with sync
   - Push notifications

### 🚀 Advanced Features

9. **Multi-User Features**
   - Study groups/teams
   - Leaderboards
   - Shared blockchain for groups
   - Peer verification

10. **Smart Contracts**
    - Automated rewards for goals
    - Study challenges
    - Achievement system
    - Token-based incentives

11. **AI Integration**
    - Study time predictions
    - Subject recommendations
    - Optimal study schedule
    - Performance insights

12. **Blockchain Features**
    - Adjustable difficulty
    - Block size optimization
    - Multiple chain support
    - Merkle tree implementation
    - Smart contract integration

### 🔧 Technical Improvements

13. **Database Optimization**
    - Redis for caching
    - Database connection pooling
    - Query optimization
    - Implement indexes

14. **API Development**
    - RESTful API endpoints
    - API authentication (JWT)
    - API documentation (Swagger)
    - Rate limiting

15. **Testing**
    - Unit tests (pytest)
    - Integration tests
    - Blockchain verification tests
    - UI/UX testing

16. **DevOps**
    - Docker containerization
    - CI/CD pipeline
    - Automated deployments
    - Monitoring & logging

### 📱 Integration Ideas

17. **Calendar Integration**
    - Google Calendar sync
    - iCal export
    - Study schedule import

18. **Third-Party Services**
    - Notion integration
    - Todoist sync
    - Google Tasks
    - Trello boards

19. **Social Features**
    - Share achievements
    - Study buddy matching
    - Public profiles
    - Social media integration

20. **Gamification**
    - XP and level system
    - Badges and achievements
    - Daily challenges
    - Streak rewards
    - Ranking system

## 🐛 Known Issues & Fixes

### Database Issues
**Fixed**: Added proper database initialization, foreign key constraints, and indexes

### Hash Inconsistency  
**Fixed**: Standardized timestamp format and data serialization

### Chain Verification
**Fixed**: Implemented comprehensive verification with proper error reporting

## 🔐 Security Best Practices

1. **Change Secret Key**: Update `app.config['SECRET_KEY']` in production
2. **Use HTTPS**: Deploy with SSL/TLS certificates
3. **Environment Variables**: Store sensitive data in .env files
4. **Database Backups**: Regular automated backups
5. **Input Validation**: Already implemented via WTForms
6. **CSRF Protection**: Add Flask-WTF CSRF tokens

## 📈 Performance Optimization

1. **Database Indexing**: Already implemented on key fields
2. **Query Optimization**: Use `select_related` for joins
3. **Caching**: Implement Redis for frequent queries
4. **Compression**: Enable gzip compression
5. **CDN**: Serve static files via CDN

## 🌍 Deployment

### Heroku Deployment
```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python app.py
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 📚 Learning Resources

- **Blockchain Basics**: Understanding hash chains and PoW
- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy ORM**: https://www.sqlalchemy.org/
- **Web3 Concepts**: Decentralization and cryptography

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details

## 👨‍💻 Author

**A2R**
- GitHub: [@YourGitHub]
- Email: your.email@example.com

## 🙏 Acknowledgments

- Blockchain technology inspiration
- Flask community
- Open source contributors
- Study productivity enthusiasts

## Live Preview
https://anshukumarpal.github.io/blockchain-project/

---

**Built with 💙 using Flask, SQLAlchemy, and Blockchain Technology**

*Secure your study journey on an immutable blockchain!*
