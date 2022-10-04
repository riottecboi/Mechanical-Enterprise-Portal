from fastapi import FastAPI, HTTPException, Depends, Response, Security, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from typing import Union
from app.schemas import *
from app.utils import *
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, mapping, check_table_exist
from app import models, crud
from uuid import uuid4
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
        title='Mechanical Enterprise Portal API',
        description='powered by gunicorn-unicorn-fastapi',
        version='1.0.0'
    )

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

x_secret_key = APIKeyHeader(name='X-SECRET-KEY', scheme_name='api-key', auto_error=True)
async def fastapi_apikeyauth(db: Session = Depends(get_db), api_key_header: str = Security(x_secret_key)):
    if crud.apikeyauth(db, api_key_header) == None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
x_admin_secret_key = APIKeyHeader(name='X-ADMIN-SECRET-KEY', scheme_name='admin-api-key', auto_error=True)
async def admin_apikeyauth(db: Session = Depends(get_db), api_key_header: str = Security(x_admin_secret_key)):
    check, status = crud.apikeyadmin(db, api_key_header)
    if check == None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
    else:
        return check
@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def redirect():
    return RedirectResponse(url='/docs')

@app.post('/signup', summary="Create new user", dependencies=[Security(admin_apikeyauth)], response_model=UserOut, tags=["admin"])
async def signup(form_data: UserAdd, response: Response, db: Session = Depends(get_db)):
    user, status_code = crud.get_user(db, form_data.username)
    if user is not None:
        logger.info("User already exist")
        response.status_code = 304
        return {'message': 'User already exist'}
    if form_data.password == form_data.confirm_password:
        # random_pwd = generate_random_password()
        userAuth = {
            'username': form_data.username,
            'apikey': str(uuid4()),
            'hashed': hashed_password(form_data.password)
            # 'tmp_password': random_pwd,
        }
        userInfo = {
            'msnv': form_data.username,
            'fullname': form_data.fullname,
            'department': form_data.department,
            'gender': form_data.gender,
            'vehicle': form_data.vehicle,
            'position': form_data.position,
            'dob': form_data.dob,
            'sector': form_data.sector,
            'tel': form_data.tel,
            'id_card': form_data.id_card,
            'ethnic': form_data.ethnic,
            'nationality': form_data.nationality,
            'address': form_data.address,
            'ward': form_data.ward,
            'district': form_data.district,
            'city': form_data.city,
            'target_group': form_data.target_group
        }
    else:
        logger.info("Password not match")
        response.status_code = 304
        return {'message': 'Password not match'}
    user, status_code = crud.create_user(db, userInfo, userAuth)
    response.status_code = status_code
    if status_code == 200:
        u_resp = {'apikey': userAuth['apikey'], 'username': userAuth['username'], 'message': 'Sign up successful'}
    else:
        u_resp = {'message': 'Cannot create a user'}
    return u_resp

@app.put('/edit', summary="Edit user information", dependencies=[Security(admin_apikeyauth)], response_model=UserOut, tags=["admin"])
async def edit(form_data: UserAdd, response: Response, db: Session = Depends(get_db)):
    user, status_code = crud.get_user(db, form_data.username)
    if user is not None:
        userInfo = {
            'msnv': form_data.username,
            'fullname': form_data.fullname,
            'department': form_data.department,
            'gender': form_data.gender,
            'vehicle': form_data.vehicle,
            'position': form_data.position,
            'dob': form_data.dob,
            'sector': form_data.sector,
            'tel': form_data.tel,
            'id_card': form_data.id_card,
            'ethnic': form_data.ethnic,
            'nationality': form_data.nationality,
            'address': form_data.address,
            'ward': form_data.ward,
            'district': form_data.district,
            'city': form_data.city,
            'target_group': form_data.target_group
        }
    else:
        logger.info("User not found")
        response.status_code = 404
        return {'message': 'User not found'}


@app.post('/login', summary="Create access for user", response_model=UserOut, tags=["users"])
async def login(form_data: UserAuth, response: Response,  db: Session = Depends(get_db)):
    user, status_code = crud.get_user(db, form_data.username)
    response.status_code = status_code
    if user is None:
        logger.info("User not found")
        return {'message': 'User not found'}
    if user.authenticated is not True:
        logger.info("Unauthorized user")
        response.status_code = 401
        return {'message': 'Unauthorized user'}

    hashed_pass = user.hashed
    if not verify_password(form_data.password, hashed_pass):
        logger.info("Incorrect email or password")
        response.status_code = 400
        return {'message': 'Incorrect Username or Password'}

    logger.info("Getting user successful")
    return {'apikey': user.apikey, 'username': form_data.username, 'is_admin': user.is_admin, 'is_edit': user.is_edit,
            'is_view': user.is_view, 'message': 'Login successful'}


@app.post('/signupMultipleUserbyExcel', summary='Create/Insert User Information & Authentication by Excel file',
          dependencies=[Security(admin_apikeyauth)], response_model=UserCreated, tags=["admin"])
async def signup_by_excel(response: Response, db: Session = Depends(get_db), file: Union[UploadFile, None] = File(..., description="Excel file upload")):
    try:
        list_pwd = []
        path = f"/tmp/{file.filename}"
        with open(path, 'wb') as e:
            e.write(file.file.read())
        table_exist = check_table_exist('user')
        if table_exist is False:
            table_status, status_code = crud.create_user_table(path, 'user', models.Base.metadata)
            response.status_code = status_code
            models.Base.metadata.create_all(engine)
            if status_code != 200:
                response.status_code = 400
                return {'list_pwd': list_pwd}
        datas = extracted_excel_file(path, mapping)
        logger.info('Creating new users ...')
        for data in datas:
            random_pwd = generate_random_password()
            userInfo = {
                'tmp_password': random_pwd,
                'apikey': str(uuid4()),
                'hashed': hashed_password(random_pwd)
            }
            resp, code = crud.insert_user_table('user', data, db, userInfo)
            if code == 200:
                list_pwd.append(resp)
        response.status_code = 200
        os.remove(path)
        return {'list_pwd': list_pwd}

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Cannot create user by Excel file",
        )

@app.post('/dropTable', summary='Drop table', dependencies=[Security(admin_apikeyauth)], response_model=UserTable, tags=["admin"])
async def drop_table(table_name: str, response: Response):
    table_status, status_code = crud.drop_table(table_name)
    response.status_code = status_code
    if status_code == 200:
        u_resp = {'table_name': table_name, 'status': table_status}
        return u_resp
    else:
        raise HTTPException(
            status_code=400,
            detail="Cannot drop a user table"
        )

# @app.post('/createUserTable', summary='Create a user table', response_model=UserTable, tags=["admin"])
# async def create_user_table_for_excel(table_name: str, response: Response):
#     table_status, status_code = crud.create_user_table(table_name, models.Base.metadata)
#     response.status_code = status_code
#     models.Base.metadata.create_all(engine)
#     if status_code == 200:
#         u_resp = {'table_name': table_name, 'status': table_status}
#         return u_resp
#     else:
#         raise HTTPException(
#             status_code=400,
#             detail="Cannot create a user table"
#         )

@app.get('/allUser', summary='Get all user from database', dependencies=[Security(admin_apikeyauth)], response_model=Union[List[UserInfo], None], tags=['admin'])
async def getAllusers(response: Response):
    allUsers, status_code = crud.get_all_users('user')
    response.status_code = status_code
    return allUsers

@app.get('/info', summary='Get details of currently logged in user', dependencies=[Security(fastapi_apikeyauth)], response_model=UserInfo, tags=["users"])
async def get_me(response: Response, username: Union[int, None] = None, apikey: Union[str, None] = None):
    user, status_code = crud.get_user_info('user', username, apikey)
    response.status_code = status_code
    if status_code == 200:
        user['dob'] = user['dob'].strftime("%d/%m/%Y")
        u_resp = user
    else:
        u_resp = user
    return u_resp