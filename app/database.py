from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from app.utils import extracted_excel_file
from sqlalchemy import Integer, Float, DateTime, BigInteger
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

mapping = {
        'TT': 'tt',
        'Mã nhân viên': 'msnv',
        'Họ và tên': 'fullname',
        'Bộ phận': 'department',
        'Giới tính': 'gender',
        'Phương tiện': 'vehicle',
        'Vị trí công việc': 'position',
        'Ngày tháng năm sinh': 'dob',
        'Đơn vị': 'sector',
        'Số điện thoại': 'tel',
        'Số CCCD': 'id_card',
        'Dân tộc': 'ethnic',
        'Quốc tịch': 'nationality',
        'Số nhà/ Tổ': 'address',
        'Xã/ Phường': 'ward',
        'Quận/ Huyện': 'district',
        'Tỉnh/TP': 'city',
        'Nhóm đối tượng': 'target_group'
    }

def check_table_exist(table: str) -> bool:
    is_exists = sqlalchemy.inspect(engine).has_table(table)
    return is_exists

def excel_extraction():
    columns = {}
    convention = {int: Integer, float: BigInteger, str: VARCHAR(charset='utf8', collation='utf8_general_ci', length=255), pandas.Timestamp: DateTime}

    excel_columns = extracted_excel_file(os.getenv('EXCEL_PATH'), mapping)[0]

    for k, v in excel_columns.items():
        columns[k] = convention[type(v)]
    return columns

engine = create_engine(os.getenv('DATABASE_URL'), encoding='utf8')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()