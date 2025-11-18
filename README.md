# 🔗 StudyChain - Blockchain-Based Study Tracker

A modern, secure study tracking application that leverages blockchain technology with Proof of Work (PoW) consensus mechanism to create an immutable record of your study sessions.

![Blockchain](https://img.shields.io/badge/Blockchain-Enabled-00D4FF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)



## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/AnshukumarPal/blockchain-project.git
cd study-chain
```

2. **Create virtual environment**
```bash
py -m venv venv

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

>[!Tip]
>If you can, prefer `psycopg[binary]` (psycopg v3) for modern projects — it has binary wheels and is the successor to psycopg2.
_If you encounter an error like `ERROR: No matching distribution found for hashlib-md5==0.1.1`, it means `hashlib-md5` (a third-party wrapper) isn't available on PyPI. Python provides `hashlib` in the standard library, so remove any `hashlib-md5` entry from `requirements.txt` and re-run the install._



4. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details

## 👨‍💻 Author

**A2R**
- GitHub: [AnshukumarPal](https://www.github.com/AnshukumarPal), [Ruchi](https://www.github.com/Richi-Rich01), [Astha](https://www.github.com/astharavat)
- Email: [AnshukumarPal](anshuspal.btce2023@iar.ac.in), [Ruchi](ruchirudani01@gmail.com), [Astha](astharavat1525@gmail.com)

---

**Built with 💙 using Flask, SQLAlchemy, and Blockchain Technology**
