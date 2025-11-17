"""
Blockchain Utilities and Verification Tools
============================================
Standalone script for managing and verifying the StudyChain blockchain

Usage:
    python blockchain_utils.py --verify                    # Verify all chains
    python blockchain_utils.py --stats                     # Show blockchain statistics
    python blockchain_utils.py --export user_id output.json  # Export user's blockchain
    python blockchain_utils.py --visualize user_id         # Visualize blockchain
"""

import sys
import os
import json
import hashlib
import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def setup_app():
    """Initialize Flask app context"""
    from app import app, db
    return app, db

def calculate_hash(block_number, timestamp, prev_hash, data, nonce, difficulty):
    """Calculate SHA-256 hash for a block"""
    block_data = f"{block_number}{timestamp}{prev_hash}{data}{nonce}{difficulty}"
    return hashlib.sha256(block_data.encode()).hexdigest()

def verify_user_chain(user_id):
    """Verify blockchain integrity for a specific user"""
    from app import StudySession
    
    sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.block_number).all()
    
    if not sessions:
        return True, "No blocks to verify", []
    
    errors = []
    
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
            errors.append(f"Block {session.block_number}: Invalid hash")
        
        # Verify chain linkage
        if i > 0:
            if session.prev_hash != sessions[i-1].hash:
                errors.append(f"Block {session.block_number}: Broken chain link")
        
        # Verify proof of work
        if not session.hash.startswith('0' * session.difficulty):
            errors.append(f"Block {session.block_number}: Doesn't meet difficulty requirement")
    
    if errors:
        return False, f"Found {len(errors)} error(s)", errors
    return True, "Blockchain is valid", []

def verify_all_chains():
    """Verify all user blockchains"""
    from app import User
    
    app, db = setup_app()
    with app.app_context():
        users = User.query.all()
        
        print("\n" + "="*70)
        print("BLOCKCHAIN VERIFICATION REPORT")
        print("="*70 + "\n")
        
        total_users = len(users)
        valid_chains = 0
        
        for user in users:
            is_valid, message, errors = verify_user_chain(user.id)
            status = "✅ VALID" if is_valid else "❌ INVALID"
            
            print(f"User: {user.username} (ID: {user.id})")
            print(f"Status: {status}")
            print(f"Message: {message}")
            
            if errors:
                print("Errors:")
                for error in errors:
                    print(f"  - {error}")
            
            print("-" * 70)
            
            if is_valid:
                valid_chains += 1
        
        print(f"\nSummary: {valid_chains}/{total_users} chains are valid")
        print("="*70 + "\n")

def show_statistics():
    """Display blockchain statistics"""
    from app import User, StudySession
    
    app, db = setup_app()
    with app.app_context():
        users = User.query.all()
        
        print("\n" + "="*70)
        print("BLOCKCHAIN STATISTICS")
        print("="*70 + "\n")
        
        for user in users:
            sessions = StudySession.query.filter_by(user_id=user.id).all()
            
            if not sessions:
                print(f"User: {user.username} - No blockchain data")
                continue
            
            total_blocks = len(sessions)
            completed = len([s for s in sessions if s.status == 'completed'])
            pending = len([s for s in sessions if s.status == 'pending'])
            total_time = sum(s.duration for s in sessions)
            
            # Calculate average nonce (mining difficulty indicator)
            avg_nonce = sum(s.nonce for s in sessions) / total_blocks
            
            # Get subject distribution
            subjects = {}
            for s in sessions:
                subjects[s.subject] = subjects.get(s.subject, 0) + 1
            
            print(f"User: {user.username} (ID: {user.id})")
            print(f"  Total Blocks: {total_blocks}")
            print(f"  Completed: {completed} | Pending: {pending}")
            print(f"  Total Study Time: {total_time} minutes ({total_time/60:.1f} hours)")
            print(f"  Average Nonce: {avg_nonce:.0f}")
            print(f"  Subjects: {', '.join(subjects.keys())}")
            print(f"  Latest Block: #{sessions[-1].block_number}")
            print(f"  Latest Hash: {sessions[-1].hash[:16]}...")
            
            is_valid, _, _ = verify_user_chain(user.id)
            status = "✅ Valid" if is_valid else "❌ Invalid"
            print(f"  Chain Status: {status}")
            print("-" * 70)
        
        print()

def export_blockchain(user_id, output_file):
    """Export user's blockchain to JSON"""
    from app import User, StudySession
    
    app, db = setup_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return
        
        sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.block_number).all()
        
        blockchain_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            "blockchain": {
                "total_blocks": len(sessions),
                "algorithm": "SHA-256",
                "consensus": "Proof of Work",
                "difficulty": sessions[0].difficulty if sessions else 0
            },
            "blocks": [session.to_dict() for session in sessions]
        }
        
        # Add verification status
        is_valid, message, _ = verify_user_chain(user_id)
        blockchain_data["verification"] = {
            "valid": is_valid,
            "message": message,
            "timestamp": datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(output_file, 'w') as f:
            json.dump(blockchain_data, f, indent=2)
        
        print(f"✅ Blockchain exported to {output_file}")
        print(f"   User: {user.username}")
        print(f"   Blocks: {len(sessions)}")
        print(f"   Status: {'Valid' if is_valid else 'Invalid'}")

def visualize_blockchain(user_id):
    """Create ASCII visualization of blockchain"""
    from app import User, StudySession
    
    app, db = setup_app()
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return
        
        sessions = StudySession.query.filter_by(user_id=user_id).order_by(StudySession.block_number).all()
        
        print("\n" + "="*70)
        print(f"BLOCKCHAIN VISUALIZATION - {user.username}")
        print("="*70 + "\n")
        
        for session in sessions:
            print(f"┌{'─'*66}┐")
            print(f"│ Block #{session.block_number:<58} │")
            print(f"├{'─'*66}┤")
            print(f"│ Timestamp: {session.timestamp.strftime('%Y-%m-%d %H:%M:%S'):<50} │")
            print(f"│ Subject: {session.subject:<56} │")
            print(f"│ Duration: {session.duration} min{'':<51} │")
            print(f"│ Status: {session.status:<57} │")
            print(f"│ Nonce: {session.nonce:<58} │")
            print(f"├{'─'*66}┤")
            print(f"│ Hash: {session.hash:<58} │")
            print(f"│ Prev: {session.prev_hash:<58} │")
            print(f"└{'─'*66}┘")
            print(f"      │")
            print(f"      ↓")
        
        print(f"\n   [END OF CHAIN - {len(sessions)} blocks]\n")

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == '--verify':
        verify_all_chains()
    
    elif command == '--stats':
        show_statistics()
    
    elif command == '--export':
        if len(sys.argv) < 4:
            print("Usage: python blockchain_utils.py --export user_id output.json")
            return
        user_id = int(sys.argv[2])
        output_file = sys.argv[3]
        export_blockchain(user_id, output_file)
    
    elif command == '--visualize':
        if len(sys.argv) < 3:
            print("Usage: python blockchain_utils.py --visualize user_id")
            return
        user_id = int(sys.argv[2])
        visualize_blockchain(user_id)
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()