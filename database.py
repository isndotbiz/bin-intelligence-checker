import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Create database engine and session
engine = create_engine('sqlite:///bins_database.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class BinRecord(Base):
    """Table for storing BIN check records"""
    __tablename__ = 'bin_records'
    
    id = Column(Integer, primary_key=True)
    bin_number = Column(String(6), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    scheme = Column(String(50))
    card_type = Column(String(50))
    country = Column(String(50))
    issuer = Column(String(100))
    ip_country = Column(String(50))
    is_3ds = Column(Boolean)
    risk_level = Column(String(20))
    fraud_context = Column(Boolean, default=False)
    raw_response = Column(Text)
    checked_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(50))  # 'manual' or 'scraper'
    source_url = Column(String(255), nullable=True)  # URL if scraped

class ThresholdRecord(Base):
    """Table for storing threshold testing records"""
    __tablename__ = 'threshold_records'
    
    id = Column(Integer, primary_key=True)
    bin_number = Column(String(6), nullable=False, index=True)
    amount = Column(String(20), nullable=False)
    triggered = Column(Boolean, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(engine)
    
def add_bin_record(bin_data, source='manual', source_url=None):
    """
    Add a BIN record to the database
    
    Args:
        bin_data (dict): BIN check result data
        source (str): 'manual' or 'scraper'
        source_url (str): URL if source is 'scraper'
        
    Returns:
        BinRecord: The created record
    """
    session = Session()
    
    try:
        record = BinRecord(
            bin_number=bin_data.get('BIN'),
            ip_address=bin_data.get('ip_address', '0.0.0.0'),
            scheme=bin_data.get('Scheme', 'Unknown'),
            card_type=bin_data.get('Type', 'Unknown'),
            country=bin_data.get('Country', 'Unknown'),
            issuer=bin_data.get('Issuer', 'Unknown'),
            ip_country=bin_data.get('IP Location', 'Unknown'),
            is_3ds=bin_data.get('is3DS', False),
            risk_level=bin_data.get('Risk Level', 'Unknown'),
            fraud_context=bin_data.get('fraud_context', False),
            raw_response=json.dumps(bin_data.get('raw_response', {})),
            source=source,
            source_url=source_url
        )
        
        session.add(record)
        session.commit()
        return record
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()

def add_threshold_record(bin_number, amount, triggered):
    """
    Add a threshold testing record to the database
    
    Args:
        bin_number (str): 6-digit BIN number
        amount (float): Dollar amount
        triggered (bool): Whether 3DS was triggered
        
    Returns:
        ThresholdRecord: The created record
    """
    session = Session()
    
    try:
        record = ThresholdRecord(
            bin_number=bin_number,
            amount=str(amount),
            triggered=triggered
        )
        
        session.add(record)
        session.commit()
        return record
    
    except Exception as e:
        session.rollback()
        raise e
    
    finally:
        session.close()

def get_bin_records(limit=100):
    """
    Get the most recent BIN records
    
    Args:
        limit (int): Maximum number of records to return
        
    Returns:
        list: List of BinRecord objects
    """
    session = Session()
    
    try:
        records = session.query(BinRecord).order_by(BinRecord.checked_at.desc()).limit(limit).all()
        return records
    
    finally:
        session.close()

def get_bin_history(bin_number):
    """
    Get all records for a specific BIN number
    
    Args:
        bin_number (str): 6-digit BIN number
        
    Returns:
        list: List of BinRecord objects
    """
    session = Session()
    
    try:
        records = session.query(BinRecord).filter(
            BinRecord.bin_number == bin_number
        ).order_by(BinRecord.checked_at.desc()).all()
        
        return records
    
    finally:
        session.close()

def get_threshold_records(bin_number):
    """
    Get all threshold testing records for a specific BIN
    
    Args:
        bin_number (str): 6-digit BIN number
        
    Returns:
        list: List of ThresholdRecord objects
    """
    session = Session()
    
    try:
        records = session.query(ThresholdRecord).filter(
            ThresholdRecord.bin_number == bin_number
        ).order_by(ThresholdRecord.amount).all()
        
        return records
    
    finally:
        session.close()

# Initialize the database when the module is imported
init_db()