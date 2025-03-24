from sqlalchemy.orm import Session

from sqlalchemy import Column, Integer, String, Float

from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index = True)
    username = Column(String, index=True)
    phone = Column(String)
    password = Column(String)
    name = Column(String)
    city = Column(String)

class UserRepository:
    def add(self, db: Session, user: User):
        db_user = User(username=user.username, phone=user.phone, password=user.password, name=user.name, city=user.city)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return user.id

    def update(self, db: Session, user: User):
        db.commit()
        db.refresh(user)
        return user.id

    def delete(self, db: Session, user: User):
        db.delete(user)
        db.commit()
        return True

    def get_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()
    
    def get_by_id(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()