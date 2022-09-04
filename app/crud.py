from sqlalchemy.orm import Session
from app.models import UserLogin
from app.utils import logger

def get_user(db: Session, username: int):
    try:
        return db.query(UserLogin).filter(UserLogin.msnv==username).one(), 200
    except Exception as e:
        logger.info("User not found")
        return None, 404

def create_user(db: Session, userInfo : dict):
    try:
        user = UserLogin(msnv=userInfo['username'], userId=userInfo['userId'], apikey=userInfo['apikey'],
                         hashed=userInfo['hashed'], authenticated=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {'apikey': user.apikey, 'username': user.msnv}, 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        db.rollback()
        return None, 400

def apikeyauth(db: Session, apikey: str):
    """
    Look up apikey, return username in dict form
    """
    try:
        query = db.query(UserLogin.msnv).filter(UserLogin.apikey == apikey).one()
        if query is not None:
            resp = {'username': query[0]}
            code = 200
        else:
            resp = None
            code = 404
        return resp, code
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        db.rollback()
        return None, 404