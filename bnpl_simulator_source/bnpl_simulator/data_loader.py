# data_loader.py

import pandas as pd
from typing import Dict, List
from .models import User as UserModel
from .config import DATASET_FILEPATH
import logging

logger = logging.getLogger(__name__)

def validate_dataset_integrity(df: pd.DataFrame) -> bool:
    """Validate that the dataset has required columns and data quality."""
    required_columns = [
        'Transaction_ID', 'Customer_Age', 'Gender', 'Annual_Income', 
        'Credit_Score', 'Purchase_Category', 'Device_Type', 
        'Connection_Type', 'Checkout_Time_Seconds', 'Browser'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns in dataset: {missing_columns}")
        return False
    
    # Check for null values in critical columns
    critical_columns = ['Transaction_ID', 'Credit_Score', 'Annual_Income']
    null_counts = df[critical_columns].isnull().sum()
    if null_counts.sum() > 0:
        logger.warning(f"Found {null_counts.sum()} null values in critical columns: {null_counts.to_dict()}")
        # Fill null values with defaults where appropriate
        df['Credit_Score'].fillna(600, inplace=True)  # Default medium credit score
        df['Annual_Income'].fillna(40000, inplace=True)  # Default income
    
    # Validate data ranges
    if (df['Credit_Score'] < 300).any() or (df['Credit_Score'] > 850).any():
        logger.warning("Found credit scores outside normal range (300-850)")
        df['Credit_Score'] = df['Credit_Score'].clip(300, 850)
    
    if (df['Annual_Income'] <= 0).any():
        logger.warning("Found non-positive annual income values")
        df['Annual_Income'] = df['Annual_Income'].clip(lower=10000)  # Minimum reasonable income
    
    return True

def load_users_from_csv() -> List[UserModel]:
    """
    Loads user profiles from a CSV file with validation and error handling.
    Each row in the CSV is treated as a unique user's profile at the time of a transaction.
    """
    try:
        logger.info(f"Loading dataset from {DATASET_FILEPATH}")
        df = pd.read_csv(DATASET_FILEPATH)
        logger.info(f"Loaded {len(df)} rows from dataset")
    except FileNotFoundError:
        logger.error(f"Dataset file not found at {DATASET_FILEPATH}")
        return []
    except Exception as e:
        logger.error(f"Error reading dataset file: {e}")
        return []

    # Validate dataset integrity
    if not validate_dataset_integrity(df):
        logger.error("Dataset validation failed, skipping data loading")
        return []

    # Drop duplicate transactions to ensure unique user_ids
    initial_count = len(df)
    df.drop_duplicates(subset=['Transaction_ID'], keep='first', inplace=True)
    duplicates_removed = initial_count - len(df)
    if duplicates_removed > 0:
        logger.info(f"Removed {duplicates_removed} duplicate transactions")

    users_to_create = []
    valid_records = 0
    invalid_records = 0
    
    for index, row in df.iterrows():
        try:
            # Validate individual record
            if pd.isna(row['Transaction_ID']) or pd.isna(row['Credit_Score']):
                invalid_records += 1
                continue
            
            # Using Transaction_ID as a unique user_id for each transaction record
            user_id = str(row['Transaction_ID'])
            new_user = UserModel(
                user_id=user_id,
                age=int(row['Customer_Age']),
                gender=str(row['Gender']),  # Ensure string type
                annual_income=float(row['Annual_Income']),
                credit_score=int(row['Credit_Score']),
                purchase_category=str(row['Purchase_Category']),
                device_type=str(row['Device_Type']),
                connection_type=str(row['Connection_Type']),
                checkout_time_seconds=int(row['Checkout_Time_Seconds']),
                browser=str(row['Browser'])
            )
            users_to_create.append(new_user)
            valid_records += 1
            
        except (ValueError, TypeError) as e:
            invalid_records += 1
            if invalid_records <= 5:  # Log first 5 errors to avoid spam
                logger.warning(f"Invalid record at row {index}: {e}")
        except Exception as e:
            invalid_records += 1
            if invalid_records <= 5:
                logger.error(f"Unexpected error processing row {index}: {e}")

    logger.info(f"Successfully created {valid_records} user records, {invalid_records} invalid records skipped")
    return users_to_create
