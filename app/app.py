from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.schemas import UserAuth, TokenSchema, UserOut
from app.utils import verify_password, create_access_token, hashed_password
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, crud
from uuid import uuid4

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def redirect():
    return RedirectResponse(url='/docs')

@app.post('/signup', summary="Create user account", response_model=UserOut)
async def signup(form_data: UserAuth, db: Session = Depends(get_db)):
    user = crud.get_user(db, form_data.msnv)
    if user is not None:
        print("User already exist")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exist"
        )
    userInfo = {
        'msnv': form_data.msnv,
        'apikey': str(uuid4()),
        'userId': 1,
        'hashed': hashed_password(form_data.password)
    }
    user = crud.create_user(db, userInfo)
    return user


@app.post('/login', summary="Create access for user", response_model=TokenSchema)
async def login(form_data: UserAuth, db: Session = Depends(get_db)):
    user = crud.get_user(db, form_data.msnv)
    if user is None:
        print("Incorrect email or password")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.hashed
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(form_data.msnv)
    }