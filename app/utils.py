from passlib.context import CryptContext
import logging
import sys
import pandas as pd

loglevel = logging.INFO
logger = logging.getLogger('Mechanical-Enterprise-Portal')
logger.setLevel(loglevel)
if not logger.handlers:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

pwd_context = CryptContext(schemes=['bcrypt'])

def hashed_password(password: str) -> str:
    logger.info('Hashing for {}'.format(password))
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    logger.info('Verifying password ...')
    return pwd_context.verify(password, hashed_password)

def remove_nans(df):
    x = df.dropna(how='all', axis=1)
    x = x.dropna(how='all', axis=0)
    x = x.reset_index(drop=True)
    return x

def extracted_excel_file(path: str):
    logger.info('Extracting Excel file ...')
    read_file = pd.read_excel(path)

    logger.info('Cleaning NaN areas ...')
    data = remove_nans(read_file)

    logger.info('Getting all headers ...')
    headers = data.columns.tolist()

    dict_data = pd.read_excel(path, usecols=headers)
    logger.info('Extracting data by following headers ...')
    extracted_data = dict_data.to_dict(orient='records')
    logger.info('Returning headers and respective data from Excel file: {}'.format(path))
    return headers, extracted_data