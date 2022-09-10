from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text
from app.database import Base

class UserLogin(Base):
    __tablename__ = 'authentication'
    id = Column(Integer, autoincrement=True, primary_key=True)
    userId = Column(Integer)
    msnv = Column(Integer)
    apikey = Column(String(64))
    tmp_password = Column(String(128), unique=True)
    hashed = Column(String(128), unique=True)
    authenticated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_view = Column(Boolean, default=True)
    is_edit = Column(Boolean, default=False)
    createdAt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


