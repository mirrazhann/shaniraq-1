from sqlalchemy.orm import Session

from sqlalchemy import Column, Integer, String, DateTime

from database import Base
from .ad import Ad
from .user import User

from datetime import datetime

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    author_id = Column(Integer, index=True)
    ad_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CommentRepository:
    def add(self, db:Session, comment: Comment):
        db_comment = Comment(content=comment.content, author_id=comment.author_id, ad_id=comment.ad_id)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment.id

    def delete(self, db:Session, comment: Comment):
        db.delete(comment)
        db.commit()
        return True
    
    def get_by_user(self, db:Session, user_id: int):
        return db.query(Comment).filter(Comment.author_id == user_id).all()

    def get_by_ad(self, db:Session, ad_id: int):
        return db.query(Comment).filter(Comment.ad_id == ad_id).all()
    
    def get_by_id(self, db:Session, id: int):
        return db.query(Comment).filter(Comment.id == id).first()
    
    def update(self, db:Session, comment: Comment):
        db.commit()
        db.refresh(comment)
        return comment.id