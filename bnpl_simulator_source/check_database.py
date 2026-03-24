#!/usr/bin/env python3
"""
Script to check the database contents and verify user data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bnpl_simulator.database import SessionLocal
from bnpl_simulator.models import User

def check_database():
    """Check database contents and user data."""
    try:
        db = SessionLocal()
        
        # Count total users
        total_users = db.query(User).count()
        print(f"Total users in database: {total_users}")
        
        # Check for the specific user IDs
        user1_id = "81bce556-c47a-4786-8456-2404e1113a6e"
        user2_id = "7ea84932-2b9f-4269-b4db-e2eaea1114ba3a6e"
        
        user1 = db.query(User).filter(User.user_id == user1_id).first()
        user2 = db.query(User).filter(User.user_id == user2_id).first()
        
        print(f"\nUser {user1_id}: {'Found' if user1 else 'Not Found'}")
        if user1:
            print(f"  Credit Score: {user1.credit_score}")
            print(f"  Age: {user1.age}")
            print(f"  Gender: {user1.gender}")
        
        print(f"\nUser {user2_id}: {'Found' if user2 else 'Not Found'}")
        if user2:
            print(f"  Credit Score: {user2.credit_score}")
            print(f"  Age: {user2.age}")
            print(f"  Gender: {user2.gender}")
        
        # Show first 5 users
        print("\nFirst 5 users in database:")
        users = db.query(User).limit(5).all()
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user.user_id} - Credit Score: {user.credit_score}")
        
        db.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database()