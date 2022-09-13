from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, Integer
from app.models import UserLogin
from app.utils import logger
from app.database import excel_extraction, engine
from typing import Union

def get_user(db: Session, username: int):
    try:
        return db.query(UserLogin).filter(UserLogin.msnv==username).one(), 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info("User not found")
        return None, 404

def get_user_info(table_name: str, username: Union[int, None], apikey: Union[str, None]):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        logger.info(f"Getting {username if username is not None else 'anonymous info'} data ...")
        command = f"select {table_name}.msnv, fullname, department, gender, vehicle, position, dob, " \
                  f"sector, tel, id_card, ethnic, nationality, address, ward, district, city, target_group" \
                  f" from {table_name} inner join authentication on {table_name}.msnv = authentication.msnv " \
                  f"where authentication.msnv = %s or authentication.apikey = %s limit 1;"
        cursor.execute(command, (username, apikey))
        resp = cursor.fetchone()
        if resp is not None:
            user = {'msnv': resp[0], 'fullname': resp[1], 'department': resp[2], 'gender': resp[3], 'vehicle': resp[4],
                    'position': resp[5], 'dob': resp[6], 'sector': resp[7], 'tel': resp[8],'id_card': resp[9],
                    'ethnic': resp[10], 'nationality': resp[11], 'address': resp[12], 'ward': resp[13], 'district': resp[14],
                    'city': resp[15], 'target_group': resp[16]
                    }
            status_code = 200
        else:
            user = {'msnv': None, 'fullname': None, 'department': None, 'gender': None, 'vehicle': None,
                    'position': None, 'dob': None, 'sector': None, 'tel': None, 'id_card': None,
                    'ethnic': None, 'nationality': None, 'address': None, 'ward': None, 'district': None,
                    'city': None, 'target_group': None
                    }
            status_code = 404

        cursor.close()
        connection.close()
        return user, status_code

    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        cursor.close()
        connection.close()
        return {}, 400


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

def create_user_table(excel_path: str, table_name: str, metadata):
    try:
        insert = lambda _dict, obj, pos: {k: v for k, v in (list(_dict.items())[:pos] +
                                                            list(obj.items()) +
                                                            list(_dict.items())[pos:])}
        headers_index = ['id', 'msnv', 'tt', 'sector']
        columns = excel_extraction(excel_path)
        columns = insert(columns, {'id': Integer}, 0)
        logger.info(f'Creating {table_name} table')
        fields = (Column(colname, coltype, primary_key=True) if colname == 'id' else Column(colname, coltype, index=True) if colname in headers_index else Column(colname, coltype) for
                  colname, coltype in columns.items())
        Table(table_name, metadata, *fields)
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

def insert_user_table(table_name: str, data: dict, db: Session, userInfo : dict):
    try:
        s = len(data.values()) * '%s,'
        s = s[:-1]
        val = [str(val) for val in data.values()]
        connection = engine.raw_connection()
        cursor = connection.cursor()
        logger.info(f'Adding data to {table_name} table')
        columns = ' ' + str.join(',', data.keys()) + ' '
        command = f"insert into {table_name} ({columns}) values ({s});"
        cursor.execute(command, tuple(val))
        connection.commit()
        cursor.close()

        user = UserLogin(msnv=data['msnv'], userId=data['tt'], apikey=userInfo['apikey'], tmp_password=userInfo['tmp_password'],
                         hashed=userInfo['hashed'], authenticated=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"New user: {data['msnv']} is created")
        logger.info(f"{table_name} table is updated\n")

        resp = {'apikey': user.apikey, 'username': user.msnv, 'is_admin': user.is_admin, 'is_edit': user.is_edit,
                'is_view': user.is_view, 'message': 'Create user {} successful'.format(user.msnv), 'tmpPWD': user.tmp_password}

        return resp, 200

    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot update data')
        return {}, 400


# create_user_table('U')
# datas = extracted_excel_file('/home/tranvinhliem/PycharmProjects/Mechanical-Enterprise-Portal/Example.xlsx', mapping)
# for data in datas:
#     logger.info('UPDATED for msnv: {}'.format(data['msnv']))
#     insert_table('U', data)