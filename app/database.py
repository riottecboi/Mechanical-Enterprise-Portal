from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from app.utils import extracted_excel_file
from sqlalchemy import Integer, Float, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
import pandas
import sqlalchemy
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

def check_table_exist(table: str) -> bool:
    is_exists = sqlalchemy.inspect(engine).has_table(table)
    return is_exists

def excel_extraction():
    columns = {}
    convention = {int: Integer, float: Float, str: VARCHAR(charset='utf8', collation='utf8_general_ci', length=255), pandas.Timestamp: DateTime}

    excel_columns = extracted_excel_file(os.getenv('EXCEL_PATH'))[1][0]

    for k, v in excel_columns.items():
        columns[k] = convention[type(v)]
    return columns

engine = create_engine(os.getenv('DATABASE_URL'), encoding='utf8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()