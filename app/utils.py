from passlib.context import CryptContext
import logging
import sys

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