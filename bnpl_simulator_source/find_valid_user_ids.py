#!/usr/bin/env python3
"""
Script to help find valid user IDs and demonstrate the 404 issue resolution.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bnpl_simulator.database import SessionLocal
from bnpl_simulator.models import User

def find_valid_user_ids():
    """Find and display valid user IDs from the database."""
    try:
        db = SessionLocal()
        
        print("=== BNPL Simulator User ID Verification ===\n")
        
        # Check the specific user IDs mentioned in the issue
        test_user_ids = [
            "81bce556-c47a-4786-8456-2404e1113a6e",  # Working user ID
            "7ea84932-2b9f-4269-b4db-e2eaea1114ba3a6e"  # Problematic user ID
        ]
        
        print("Testing specific user IDs:")
        print("-" * 50)
        
        for user_id in test_user_ids:
            user = db.query(User).filter(User.user_id == user_id).first()
            status = "FOUND" if user else "NOT FOUND"
            length = len(user_id)
            uuid_status = "Valid UUID" if length == 36 else f"Invalid UUID ({length} chars)"
            
            print(f"User ID: {user_id}")
            print(f"  Status: {status}")
            print(f"  Length: {length} characters ({uuid_status})")
            if user:
                print(f"  Credit Score: {user.credit_score}")
                print(f"  Age: {user.age}")
                print(f"  Gender: {user.gender}")
            print()
        
        # Show some valid user IDs for testing
        print("Sample of valid user IDs from database:")
        print("-" * 50)
        users = db.query(User).limit(10).all()
        for i, user in enumerate(users, 1):
            print(f"{i:2d}. {user.user_id} (Credit Score: {user.credit_score})")
        
        print(f"\nTotal users in database: {db.query(User).count()}")
        
        db.close()
        
        print("\n=== Resolution Summary ===")
        print("The 404 error occurs because the user ID '7ea84932-2b9f-4269-b4db-e2eaea1114ba3a6e'")
        print("is not a valid UUID format (40 characters instead of 36) and does not exist in the database.")
        print("\nTo fix this issue, use any of the valid user IDs listed above.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_valid_user_ids()