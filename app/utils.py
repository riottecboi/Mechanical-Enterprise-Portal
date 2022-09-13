from passlib.context import CryptContext
import logging
import sys
import secrets
import pandas as pd
import numpy as np

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

def generate_random_password():
    passwordString = secrets.token_hex()
    return passwordString

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

def extracted_excel_file(path: str, mapping: dict):
    data_response = []

    read_file = pd.read_excel(path)

    data = remove_nans(read_file)

    headers = data.columns.tolist()

    dict_data = pd.read_excel(path, usecols=headers)
    extracted_data = dict_data.replace({np.nan: None}).to_dict(orient='records')
    for dt in extracted_data:
        newdict = {}
        for k in dt:
            if k =='Số CCCD' or k=='Số điện thoại':
                if dt[k] is None:
                    dt[k] = 0
            newdict[mapping[k]] = dt[k]
        data_response.append(newdict)
    return data_response