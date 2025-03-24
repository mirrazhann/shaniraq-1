from sqlalchemy.orm import Session

from sqlalchemy import Column, Integer, String, Float

from database import Base

class Ad(Base):
    __tablename__ = 'ads'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    price = Column(Float)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    author_id = Column(Integer, index=True)

class AdRepository:
    def add(self, db:Session, ad: Ad):
        db_ad = Ad(type=ad.type, price = ad.price, address = ad.address, area = ad.area, rooms_count = ad.rooms_count, description = ad.description, author_id = ad.author_id)
        db.add(db_ad)
        db.commit() 
        db.refresh(db_ad)
        return db_ad.id

    def update(self, db:Session, ad: Ad):
        db.commit()
        db.refresh(ad)
        return ad.id

    def delete(self, db:Session, ad: Ad):
        db.delete(ad)
        db.commit()
        return True

    def get_by_user(self, db:Session, user_id: int):
        return db.query(Ad).filter(Ad.author_id==user_id).all()
    
    def get_by_id(self, db:Session, id: int):
        return db.query(Ad).filter(Ad.id==id).first() 
