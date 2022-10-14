from sqlalchemy.orm import Session
from sqlalchemy import Table, Column, Integer
from app.models import *
from app.utils import logger, hashed_password
from app.database import excel_extraction, engine, check_table_exist, column_creator
from typing import Union
from datetime import datetime

def get_user(db: Session, username: Union[str,int]):
    try:
        u = db.query(UserLogin).filter(UserLogin.msnv==username).one()
        db.close()
        return u, 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info("User not found")
        return None, 404

def get_admin(db: Session, username: Union[str,int]):
    try:
        u = db.query(Admin).filter(Admin.msnv == username).one()
        db.close()
        return u, 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info("User not found")
        return None, 404

def admin_password_update(db: Session, userAuth: dict):
    try:
        db.query(Admin).filter(Admin.msnv == userAuth['username']).update({'hashed': userAuth['hashed']})
        db.commit()
        db.close()
        return {'username': userAuth['username']}, 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info("Could not update password")
        return None, 304

def password_update(db: Session, userAuth: dict):
    try:
        db.query(UserLogin).filter(UserLogin.msnv == userAuth['username']).update({'hashed': userAuth['hashed'], 'tmp_password': None})
        db.commit()
        db.close()
        return {'username': userAuth['username']}, 200
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info("Could not update password")
        return None, 304

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


def update_user(userInfo : dict):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        joinItems = []
        userInfo['dob'] = datetime.strptime(userInfo['dob'], format('%d/%m/%Y'))
        for col in userInfo:
            joinItems.append(col + '=' + '%s')
        concatenateJoinstring = ', '.join(joinItems)
        val = [str(val) for val in userInfo.values()]
        command = f"update user set {concatenateJoinstring} where msnv=%s"
        val.append(userInfo['msnv'])
        cursor.execute(command, tuple(val))
        connection.commit()
        cursor.close()
        connection.close()
        return {'username': userInfo['msnv']}, 200

    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        return None, 400

def create_admin_user(db: Session, userAuth : dict):
    try:
        user = Admin(msnv=userAuth['username'], apikey=userAuth['apikey'],
                     hashed=userAuth['hashed'], is_admin=True, authenticated=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {'apikey': user.apikey, 'username': user.msnv}, 200
    except Exception as e:
        logger.info("Cannot add new user account for {}".format(str(userAuth['username'])))
        return None, 400


def create_user(db: Session, userInfo : dict, userAuth : dict):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        getLatestID = f"select max(tt) from user;"
        cursor.execute(getLatestID)
        resp = cursor.fetchone()
        if resp[0] is None:
            tt = 0
        else:
            tt = resp[0]

        userInfo['tt'] = tt + 1

        if userInfo['dob'] is not None:
            userInfo['dob'] = datetime.strptime(userInfo['dob'], format('%d/%m/%Y'))
        else:
            userInfo.pop('dob')

        if userInfo['tel'] is None:
            userInfo['tel'] = 0
        if userInfo['id_card'] is None:
            userInfo['id_card'] = 0

        s = len(userInfo.values()) * '%s,'
        s = s[:-1]
        val = [str(val) for val in userInfo.values()]
        columns = ' ' + str.join(',', userInfo.keys()) + ' '
        command = f"insert into user ({columns}) values ({s});"
        cursor.execute(command, tuple(val))
        connection.commit()
        getLatestID = f"select max(tt) from user;"
        cursor.execute(getLatestID)
        userID = cursor.fetchone()
        if userID is not None:

            if 'is_admin' in userAuth:
                user = Admin(msnv=userAuth['username'], apikey=userAuth['apikey'],
                                 hashed=userAuth['hashed'], is_admin=True, authenticated=True)
            else:
                user = UserLogin(msnv=userAuth['username'], userId=int(userID[0]), apikey=userAuth['apikey'],
                                 hashed=userAuth['hashed'], authenticated=True)
            db.add(user)
            db.commit()
            db.refresh(user)
            cursor.close()
            connection.close()
            return {'apikey': user.apikey, 'username': user.msnv}, 200
        else:
            cursor.close()
            connection.close()
            logger.info("Cannot add new user account for {}".format(str(userInfo['username'])))
            return None, 400

    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        db.rollback()
        return None, 400

def apikeyauth(db: Session, apikey: str):
    """
    Look up apikey, return username in dict form
    """
    try:
        query = db.query(UserLogin).filter(UserLogin.apikey == apikey).one()
        if query is not None:
            resp = {'username': query.msnv, 'admin': query.is_admin}
            code = 200
        else:
            resp = None
            code = 404
        return resp, code
    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        db.rollback()
        return None, 404

def apikeyadmin(db: Session, apikey: str):
    """
    Look up admin apikey, return username in dict form
    """
    try:
        query = db.query(UserLogin).filter(UserLogin.apikey == apikey).one()
        if query.is_admin is True:
            resp = {'username': query.msnv, 'admin': query.is_admin}
            code = 200
        else:
            resp = None
            code = 401
        return resp, code
    except Exception as e:
        try:
            query = db.query(Admin).filter(Admin.apikey == apikey).one()
            if query.is_admin is True:
                resp = {'username': query.msnv, 'admin': query.is_admin}
                code = 200
            else:
                resp = None
                code = 401
            return resp, code
        except:
            logger.info("Exception occurred: {}".format(str(e)))
            db.rollback()
            return None, 401

def create_user_table_not_by_excel(table_name: str, metadata):
    try:
        insert = lambda _dict, obj, pos: {k: v for k, v in (list(_dict.items())[:pos] +
                                                            list(obj.items()) +
                                                            list(_dict.items())[pos:])}
        headers_index = ['id', 'msnv', 'tt', 'sector']
        columns = column_creator()
        columns = insert(columns, {'id': Integer}, 0)
        logger.info(f'Creating {table_name} table')
        fields = (Column(colname, coltype, primary_key=True) if colname == 'id' else Column(colname, coltype,
                index=True) if colname in headers_index else Column(colname, coltype) for colname, coltype in columns.items())
        Table(table_name, metadata, *fields)
        return True, 200

    except Exception as e:
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot create {table_name} table')
        return False, 400

def create_user_table(excel_path: str, table_name: str, metadata):
    try:
        insert = lambda _dict, obj, pos: {k: v for k, v in (list(_dict.items())[:pos] +
                                                            list(obj.items()) +
                                                            list(_dict.items())[pos:])}
        headers_index = ['id', 'msnv', 'tt', 'sector']
        columns = excel_extraction(excel_path)
        columns = insert(columns, {'id': Integer}, 0)
        logger.info(f'Creating {table_name} table')
        metadata.clear()
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
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        logger.info(f'Deleting {table_name} table')
        command = "DROP TABLE IF EXISTS {};".format(table_name)
        cursor.execute(command)
        connection.commit()
        authentication_command = "DELETE FROM authentication;"
        cursor.execute(authentication_command)
        connection.commit()
        cursor.close()
        logger.info(f'{table_name} table is deleted')
        connection.close()
        return True, 200
    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot drop {table_name} table')
        return False, 400

def del_admin(username):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        authentication_command = f"delete from admin where msnv=%s"
        cursor.execute(authentication_command, (username,))
        connection.commit()

        cursor.close()
        connection.close()
        return {'msg': 'Successful delete account'}, 200

    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot delete account')
        return {}, 400

def del_user(username):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        user_command = f"delete from user where msnv = %s;"
        cursor.execute(user_command, (username,))
        connection.commit()

        authentication_command = f"delete from authentication where msnv=%s"
        cursor.execute(authentication_command, (username,))
        connection.commit()

        cursor.close()
        connection.close()
        return {'msg': 'Successful delete account'}, 200

    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot delete account')
        return {}, 400

def insert_user_table(table_name: str, data: dict, db: Session, userInfo : dict):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        s = len(data.values()) * '%s,'
        s = s[:-1]
        val = [str(val) for val in data.values()]
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
        cursor.close()
        connection.close()
        return resp, 200

    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot update data')
        return {}, 400

def get_all_users(table_name: str):
    connection = engine.raw_connection()
    cursor = connection.cursor()
    try:
        users = []
        logger.info('Getting all users')
        command = f"SELECT * from {table_name};"
        cursor.execute(command)
        resp = cursor.fetchall()
        if resp is not None:
            for result in resp:
                if str(result[2]).lower() == 'admin':
                    continue
                if result[8] is not None:
                    dob = result[8].strftime('%d-%m-%Y')
                else:
                    dob = None
                users.append({'tt': result[1], 'msnv': result[2], 'fullname': result[3], 'department': result[4], 'gender': result[5], 'vehicle': result[6], 'position': result[7], 'dob': dob,
                              'sector': result[9], 'tel': result[10], 'id_card': result[11], 'ethnic': result[12], 'nationality': result[13], 'address': result[14], 'ward': result[15], 'district': result[16],
                              'city': result[17], 'target_group': result[18]})

        cursor.close()
        connection.close()
        return users, 200
    except Exception as e:
        cursor.close()
        connection.close()
        logger.info("Exception occurred: {}".format(str(e)))
        logger.info(f'Cannot get data')
        return [], 400


# create_user_table('U')
# datas = extracted_excel_file('/home/tranvinhliem/PycharmProjects/Mechanical-Enterprise-Portal/Example.xlsx', mapping)
# for data in datas:
#     logger.info('UPDATED for msnv: {}'.format(data['msnv']))
#     insert_table('U', data)