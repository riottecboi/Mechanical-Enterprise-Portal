from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.responses import RedirectResponse
from schemas import UserOut, UserAuth, SystemUser, TokenSchema
from utils import hashed_password, verify_password, create_access_token
from uuid import uuid4
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import uvicorn

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


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: UserAuth, db: Session = Depends(get_db)):
    user = db.get(form_data.msnv, None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user['email'])
    }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        port=8080,
        log_level="info",
        reload=True
    )