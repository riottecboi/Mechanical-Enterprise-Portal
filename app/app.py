from fastapi import FastAPI, HTTPException, Depends, Response, Security, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from typing import Union
from app.schemas import UserAuth, UserOut, UserCreated, UserTable
from app.utils import *
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, mapping, check_table_exist
from app import models, crud
from uuid import uuid4

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

x_secret_key = APIKeyHeader(name='X-SECRET-KEY', auto_error=True)
async def fastapi_apikeyauth(db: Session = Depends(get_db), api_key_header: str = Security(x_secret_key)):
    if crud.apikeyauth(db, api_key_header) == None:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )

@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def redirect():
    return RedirectResponse(url='/docs')

@app.post('/signup', summary="Create user account", response_model=UserOut, tags=["users"])
async def signup(form_data: UserAuth, response: Response, db: Session = Depends(get_db)):
    user, status_code = crud.get_user(db, form_data.username)
    if user is not None:
        logger.info("User already exist")
        response.status_code = 200
        return {'message': 'User already exist'}

    userInfo = {
        'username': form_data.username,
        'apikey': str(uuid4()),
        'userId': 1,
        'hashed': hashed_password(form_data.password)
    }
    user, status_code = crud.create_user(db, userInfo)
    response.status_code = status_code
    if status_code == 200:
        u_resp = {'apikey': userInfo['apikey'], 'username': form_data.username, 'message': 'Sign up successful'}
    else:
        u_resp = {'message': 'Cannot create a user'}
    return u_resp


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
    return {'apikey': user.apikey, 'username': form_data.username, 'is_admin': user.is_admin, 'is_edit': user.is_edit, 'is_view': user.is_view, 'message': 'Login successful'}


@app.post('/signupMultipleUserbyExcel', summary='Create/Insert User Information & Authentication by Excel file', dependencies=[Security(fastapi_apikeyauth)],  response_model=UserCreated, tags=["admin"])
async def signup_by_excel(table_name: str, response: Response, db: Session = Depends(get_db), file: Union[UploadFile, None] = File(..., description="Excel file upload")):
    try:
        list_pwd = []
        path = f"/tmp/{file.filename}"
        with open(path, 'wb') as e:
            e.write(file.file.read())
        table_exist = check_table_exist(table_name)
        if table_exist is True:
            datas = extracted_excel_file(path, mapping)
            logger.info('Creating new users ...')
            for data in datas:
                random_pwd = generate_random_password()
                userInfo = {
                    'tmp_password': random_pwd,
                    'apikey': str(uuid4()),
                    'hashed': hashed_password(random_pwd)
                }
                resp, code = crud.insert_user_table(table_name, data, db, userInfo)
                if code == 200:
                    list_pwd.append(resp)
            response.status_code = 200
            return {'list_pwd': list_pwd}
        else:
            response.status_code = 404
            return {'list_pwd': list_pwd}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Cannot create user by Excel file",
        )

@app.post('/dropTable', summary='Drop a user table', dependencies=[Security(fastapi_apikeyauth)], response_model=UserTable, tags=["admin"])
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

@app.post('/createUserTable', summary='Create a user table', response_model=UserTable, tags=["admin"])
async def create_user_table_for_excel(table_name: str, response: Response):
    table_status, status_code = crud.create_user_table(table_name, models.Base.metadata)
    response.status_code = status_code
    models.Base.metadata.create_all(engine)
    if status_code == 200:
        u_resp = {'table_name': table_name, 'status': table_status}
        return u_resp
    else:
        raise HTTPException(
            status_code=400,
            detail="Cannot create a user table"
        )


@app.get('/me', summary='Get details of currently logged in user', dependencies=[Security(fastapi_apikeyauth)], response_model=UserOut)
async def get_me(username: int, response: Response, db: Session = Depends(get_db)):
    user, status_code = crud.get_user(db, username)
    response.status_code = status_code
    if status_code == 200:
        u_resp = {'apikey': user.apikey, 'username': username}
    else:
        u_resp = {'message': 'Incorrect Username'}
    return u_resp