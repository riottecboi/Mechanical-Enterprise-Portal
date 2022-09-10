from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, TIMESTAMP, text
from app.database import Base

# class User(Base):
#     __tablename__ = 'user'
#     id = Column(Integer, autoincrement=True, primary_key=True)
#     msnv = Column(Integer, index=True)
#     fullname = Column(VARCHAR(charset='utf8', collation='utf8_general_ci', length=255), index=True)
#     department = Column(String(128))
#     gender = Column(String(8))
#     vehicle = Column(String(128))
#     position = Column(String(64))
#     dob = Column(String(32))
#     unit = Column(String(32))
#     tel = Column(Integer, index=True)
#     id_card = Column(Integer, index=True)
#     ethnic = Column(String(8))
#     address = Column(String(255))
#     ward = Column(String(64))
#     district = Column(String(64))
#     city = Column(String(64))
#     target_group = Column(String(16))

class UserLogin(Base):
    __tablename__ = 'authentication'
    id = Column(Integer, autoincrement=True, primary_key=True)
    userId = Column(Integer)
    msnv = Column(Integer)
    apikey = Column(String(64))
    hashed = Column(String(128), unique=True)
    authenticated = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_view = Column(Boolean, default=True)
    is_edit = Column(Boolean, default=False)
    createdAt = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


