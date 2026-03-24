# database.py

from sqlalchemy import create_engine, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import DATABASE_URL
import logging

# Configure logging for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine with optimizations for better performance
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30.0  # 30 second timeout for queries
    },
    poolclass=StaticPool,  # Use StaticPool for SQLite to avoid connection issues
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600     # Recycle connections every hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Create database indexes for better query performance
def create_indexes():
    """Create database indexes to optimize query performance."""
    try:
        # Create indexes on frequently queried columns
        with engine.connect() as conn:
            # Index on user_id for faster user lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_credit_score ON users(credit_score)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_completed_loans ON users(completed_loans)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_late_payments ON users(late_payments)")
            
            # Index on loans for faster loan lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_loan_id ON loans(loan_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_user_id ON loans(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_status ON loans(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_loans_total_amount ON loans(total_amount)")
            
            # Index on installments for faster installment lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_installments_loan_id ON installments(loan_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_installments_status ON installments(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_installments_due_date ON installments(due_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_installments_installment_number ON installments(installment_number)")
            
            conn.commit()
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")

# Dependency to get a DB session with error handling
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
