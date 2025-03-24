from fastapi import FastAPI, Request, Form, HTTPException, Response, Depends
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal

from typing import Optional

import jwt
import json
import re

from repository.user import UserRepository, User
from repository.ad import AdRepository, Ad
from repository.comment import CommentRepository, Comment

SECRET_KEY = "Shanirak"
ALGORITHM = "HS256"

Base.metadata.create_all(bind=engine)

app = FastAPI()
user_repository = UserRepository()
ad_repository = AdRepository()
comment_repository = CommentRepository()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Регистрация
@app.post('/auth/users/')
async def post_signup(
    request: Request, 
    username: str = Form(),
    password: str = Form(),
    phone: str = Form(),
    name: str = Form(),
    city: str = Form(),
    db: Session = Depends(get_db)
):
    if username.strip() == "":
        result = {
            "result": "error",
            "message": "invalid username"
        }
        raise HTTPException(status_code=401, detail=result)
    elif phone.strip() == "":
        result = {
            "result": "error",
            "message": "invalid phone"
        }
        raise HTTPException(status_code=401, detail=result)
    elif password.strip() == "":
        result = {
            "result": "error",
            "message": "invalid password"
        }
        raise HTTPException(status_code=401, detail=result)
    elif name.strip() == "":
        result = {
            "result": "error",
            "message": "invalid name"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif city.strip() == "":
        result = {
            "result": "error",
            "message": "invalid city"
        }
        raise HTTPException(status_code=401, detail=result)
    
    # if(validate_phone_number(phone)!= False):
    #     phone = validate_phone_number(phone)
    # else:
    #     result = {
    #         "result": "error",
    #         "message": "invalid phone"
    #     }
    #     raise HTTPException(status_code=401, detail=result)
    
    if user_repository.get_by_username(db, username):
        result = {
            "result": "error",
            "message": "username was registered earley"
        }
        raise HTTPException(status_code=401, detail=result)

    new_user = User(username=username, phone=phone, password=password, name=name, city=city)
    user_repository.add(db, new_user)
    result = {
        "result": "ok",
        "message": "New user created"
    }
    return result

# Валидация номера телефона
# def validate_phone_number(phone: str) -> str:
#     cleaned_phone = ''.join(filter(str.isdigit, phone))
    
#     # Проверяем, соответствует ли номер формату: начинается с 77 и всего 11 цифр
#     if re.fullmatch(r'77\d{9}', cleaned_phone):
#         return cleaned_phone
#     else:
#         return False
    
# Токен авторизации
def create_token(user: User):
    payload = {
        'user_id': user.id,
        "exp": datetime.utcnow() + timedelta(hours=1) 
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Проверка авторизации
def get_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            result = {
                "result": "error",
                "message": "Invalid credentials"
            }
            raise HTTPException(status_code=401, detail=result)
        # Получаем данные пользователя (в виде словаря) из репозитория
        user_data = user_repository.get_by_id(db, int(user_id))
        if not user_data:
            result = {
                "result": "error",
                "message": "User not found"
            }
            raise HTTPException(status_code=401, detail=result)
        # Преобразуем словарь в объект User, если необходимо
        if isinstance(user_data, dict):
            user_obj = User(**user_data)
        else:
            user_obj = user_data
        return user_obj
    except jwt.PyJWTError:
        result = {
                "result": "error",
                "message": "Invalid credentials"
        }
        raise HTTPException(status_code=401, detail=result)
    
# Авторизация
@app.post("/auth/users/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = form_data.username  
    password = form_data.password
    temp_user = user_repository.get_by_username(db, username)
    if not temp_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    elif temp_user.password != password:
        result = {
            "result": "error",
            "message": "invalid password"
        }
        raise HTTPException(status_code=401, detail=result)
    # генерим токен и сохраняем в куки (авторизация)
    token = create_token(temp_user)
    result = {
            "result": "ok",
            "access_token": token
        }
    return result

# Данные пользователя
@app.get('/auth/users/me')
async def get_user_info(db: Session = Depends(get_db), current_user: User = Depends(get_user)):
    result = {
        "id": current_user.id,
        "username": current_user.username,
        "phone": current_user.phone,
        "name": current_user.name,
        "city": current_user.city,
    }
    return result

# Обновление пользователя
@app.patch("/auth/users/me")
def update_user(
    user_id: int,
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    current_user = user_repository.get_by_id(db, user_id)
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    if username is None:
        result = {
            "result": "error",
            "message": "Empty username"
        }
        raise HTTPException(status_code=401, detail=result)
    
    if password is None:
        result = {
            "result": "error",
            "message": "Empty password"
        }
        raise HTTPException(status_code=401, detail=result)
    if phone is None:
        result = {
            "result": "error",
            "message": f"Invalid phone"
        }
        raise HTTPException(status_code=401, detail=result)
    
    if name is None:
        result = {
            "result": "error",
            "message": f"Invalid name"
        }
        raise HTTPException(status_code=401, detail=result)
    
    if city is None:
        result = {
            "result": "error",
            "message": "Empty city"
        }
        raise HTTPException(status_code=401, detail=result)

    current_user.username = username
    current_user.password = password
    current_user.phone = phone
    current_user.name = name
    current_user.city = city
    user_repository.update(db, current_user)
    return {"result": "ok", "message": "user updated"}

# Новое объявление
@app.post('/shanyraks/')
def add_ad(
    request: Request, 
    type: str = Form(),
    price: float = Form(),
    address: str = Form(),
    area: float = Form(),
    rooms_count: int = Form(),
    description: str = Form(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)

    if type.strip() == "":
        result = {
            "result": "error",
            "message": "invalid type"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif price <= 0:
        result = {
            "result": "error",
            "message": "invalid price"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif address.strip() == "":
        result = {
            "result": "error",
            "message": "invalid address"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif area <= 0:
        result = {
            "result": "error",
            "message": "invalid area"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif rooms_count <= 0:
        result = {
            "result": "error",
            "message": "invalid rooms_count"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif description.strip() == "":
        result = {
            "result": "error",
            "message": "invalid description"
        }
        raise HTTPException(status_code=401, detail=result)
    
    new_ad = Ad(
        type=type,
        price=price,
        address=address,
        area=area,
        rooms_count=rooms_count,
        description=description,
        author_id = current_user.id
    )
    new_id = ad_repository.add(db, new_ad)
    result = {
        "result": "ok",
        "message": "New ad created",
        "ad_id": new_id
    }
    return result

# Обновление объявления
@app.patch("/shanyraks/{ad_id}")
def get_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    type: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    address: Optional[str] = Form(None),
    area: Optional[float] = Form(None),
    rooms_count: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_ad = ad_repository.get_by_id(db, ad_id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    if type.strip() == "":
        result = {
            "result": "error",
            "message": "invalid type"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif price <= 0:
        result = {
            "result": "error",
            "message": "invalid price"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif address.strip() == "":
        result = {
            "result": "error",
            "message": "invalid address"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif area <= 0:
        result = {
            "result": "error",
            "message": "invalid area"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif rooms_count <= 0:
        result = {
            "result": "error",
            "message": "invalid rooms_count"
        }
        raise HTTPException(status_code=401, detail=result)
    
    elif description.strip() == "":
        result = {
            "result": "error",
            "message": "invalid description"
        }
        raise HTTPException(status_code=401, detail=result)

    current_ad.type = type
    current_ad.price = price
    current_ad.address = address
    current_ad.area = area
    current_ad.rooms_count = rooms_count
    current_ad.description = description
    
    ad_repository.update(db, current_ad)
    return {"result": "ok", "message": "ad updated"}
    
# Получение объявления
@app.get("/shanyraks/{ad_id}")
def get_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_ad = ad_repository.get_by_id(db, ad_id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    comments = comment_repository.get_by_ad(db, ad_id)
    # count_comments = len(comments['comments'])
    
    result = {
        "id": current_ad.id,
        "type": current_ad.type,
        "price": current_ad.price,
        "address": current_ad.address,
        "area": current_ad.area,
        "rooms_count": current_ad.rooms_count,
        "description": current_ad.description,
        "total_comments": len(comments)
    }
    return result
    

# Удаление объявления
@app.delete("/shanyraks/{ad_id}")
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)

    current_ad = ad_repository.get_by_id(db, ad_id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    ad_repository.delete(db, current_ad)
    return {"result": "ok", "message": "ad deleted"}

# Добавление комментария
@app.post("/shanyraks/{id}/comments")
def add_comment(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user),
    content: str = Form()
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)

    current_ad = ad_repository.get_by_id(db, id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    
    if content.strip() == "":
        result = {
            "result": "error",
            "message": "invalid content"
        }
        raise HTTPException(status_code=401, detail=result)
    
    new_comment = Comment(content=content, author_id=current_user.id, ad_id=current_ad.id)
    comment_repository.add(db, new_comment)
    result = {
        "result": "ok",
        "message": "New comment created"
    }
    return result

# Изменение комментария
@app.patch("/shanyraks/{id}/comments/{comment_id}")
def get_ad(
    id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    content: Optional[str] = Form(None),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_ad = ad_repository.get_by_id(db, id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_comment = comment_repository.get_by_id(db, comment_id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    if content.strip() == "":
        result = {
            "result": "error",
            "message": "invalid content"
        }
        raise HTTPException(status_code=401, detail=result)
    
    

    current_comment.content = content
    
    comment_repository.update(db, current_comment)
    return {"result": "ok", "message": "comment updated"}

# Удаление комментария
@app.delete("/shanyraks/{id}/comments/{comment_id}")
def delete_comment(
    id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_ad = ad_repository.get_by_id(db, id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_comment = comment_repository.get_by_id(db, comment_id)
    if not current_comment:
        result = {
            "result": "error",
            "message": "comment not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    comment_repository.delete(db, current_comment)
    return {"result": "ok", "message": "comment deleted"}

# Все комментарии объявления
@app.get("/shanyraks/{id}/comments")
def get_all_comments(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user)
):
    if not current_user:
        result = {
            "result": "error",
            "message": "user not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    current_ad = ad_repository.get_by_id(db, id)
    if not current_ad:
        result = {
            "result": "error",
            "message": "ad not found"
        }
        raise HTTPException(status_code=401, detail=result)
    
    result = {"comments": comment_repository.get_by_ad(db, id)}
    return result


# Объявление с комментариями