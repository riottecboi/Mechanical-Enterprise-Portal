from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, msnv: int):
    try:
        return db.query(models.UserLogin.hashed).filter(models.UserLogin.msnv==msnv).one()
    except Exception as e:
        return None

def create_user(db: Session, userInfo : dict):
    try:
        user = models.UserLogin(msnv=userInfo['msnv'], userId=userInfo['userId'], apikey=userInfo['apikey'], hashed=userInfo['hashed'], authenticated=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {'apikey':user.apikey, 'msnv': user.msnv}
    except Exception as e:
        print(str(e))
        db.rollback()
        return False
