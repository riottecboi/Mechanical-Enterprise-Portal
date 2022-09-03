from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

db_url = {
    'database': os.getenv('DATABASE'),
    'drivername': os.getenv('DRIVERNAME'),
    'username': os.getenv('USERNAME'),
    'password': os.getenv('PASSWORD'),
    'host': os.getenv('HOST'),
    'query': {'charset': 'utf8'},  # the key-point setting
}

engine = create_engine(os.getenv('DATABASE_URL'), encoding='utf8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

