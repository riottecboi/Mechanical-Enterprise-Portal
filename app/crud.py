from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, Integer
from app.models import UserLogin
from app.utils import logger
from app.database import excel_extraction, Base, engine

def get_user(db: Session, username: int):
    try:
        return db.query(UserLogin).filter(UserLogin.msnv==username).one(), 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
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

def create_table(table_name: str):
    try:
        insert = lambda _dict, obj, pos: {k: v for k, v in (list(_dict.items())[:pos] +
                                                            list(obj.items()) +
                                                            list(_dict.items())[pos:])}
        headers_index = ['ID', 'Mã nhân viên', 'TT', 'Đơn vị']
        columns = excel_extraction()
        columns = insert(columns, {'ID': Integer}, 0)
        logger.info(f'Creating {table_name} table')
        fields = (Column(colname, coltype, primary_key=True) if colname == 'ID' else Column(colname, coltype, index=True) if colname in headers_index else Column(colname, coltype) for
                  colname, coltype in columns.items())
        Table(table_name, Base.metadata, *fields)
        return True, 200

    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot create {table_name} table')
        return False, 400

# def alter_table(table_name: str):
#     connection = engine.raw_connection()
#     cursor = connection.cursor()
#     command = "ALTER TABLE {} ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY;".format(table_name)
#     cursor.execute(command)
#     connection.commit()
#     cursor.close()
#     logger.info(f'{table_name} table is created')
#     return True, 200


def drop_table(table_name: str):
    try:
        connection = engine.raw_connection()
        cursor = connection.cursor()
        logger.info(f'Deleting {table_name} table')
        command = "DROP TABLE IF EXISTS {};".format(table_name)
        cursor.execute(command)
        connection.commit()
        cursor.close()
        logger.info(f'{table_name} table is deleted')
        return True, 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot drop {table_name} table')
        return False, 400