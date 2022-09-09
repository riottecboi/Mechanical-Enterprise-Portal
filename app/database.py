from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from app.utils import extracted_excel_file
from sqlalchemy import Table, Column, Integer, String, Float, DateTime
import pandas
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

columns = {}
convention = {int: Integer, float: Float, str: String(255), pandas.Timestamp: DateTime}

excel_columns = extracted_excel_file(os.getenv('EXCEL_PATH'))[1][0]

engine = create_engine(os.getenv('DATABASE_URL'), encoding='utf8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

for k, v in excel_columns.items():
    columns[k] = convention[type(v)]
fields = (Column(colname, coltype) for colname, coltype in columns.items())
t = Table('U', Base.metadata, *fields)