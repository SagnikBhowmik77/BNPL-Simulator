#!/usr/bin/env python3
"""
Script to find user IDs with age below 20 (teen users).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bnpl_simulator.database import SessionLocal
from bnpl_simulator.models import User

def find_teen_users():
    """Find user IDs with age below 20."""
    try:
        db = SessionLocal()
        
        print("=== Finding Users with Age Below 20 ===\n")
        
        # Query users with age < 20
        teen_users = db.query(User).filter(User.age < 20).all()
        
        print(f"Found {len(teen_users)} users with age below 20:\n")
        
        if teen_users:
            print("Teen Users (Age < 20):")
            print("-" * 60)
            for i, user in enumerate(teen_users, 1):
                print(f"{i:2d}. User ID: {user.user_id}")
                print(f"    Age: {user.age}")
                print(f"    Gender: {user.gender}")
                print(f"    Credit Score: {user.credit_score}")
                print(f"    Annual Income: {user.annual_income}")
                print(f"    Purchase Category: {user.purchase_category}")
                print()
        else:
            print("No users found with age below 20.")
        
        # Also show some young adult users (age 20-25) for comparison
        young_adults = db.query(User).filter(User.age.between(20, 25)).limit(5).all()
        
        if young_adults:
            print("Sample Young Adult Users (Age 20-25):")
            print("-" * 60)
            for i, user in enumerate(young_adults, 1):
                print(f"{i:2d}. User ID: {user.user_id}")
                print(f"    Age: {user.age}")
                print(f"    Gender: {user.gender}")
                print(f"    Credit Score: {user.credit_score}")
                print()
        
        db.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_teen_users()