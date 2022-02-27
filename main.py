# Copyright 2022 Arbaaz Laskar

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Optional
from uuid import UUID
from dotenv import load_dotenv
import os
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.middleware.cors import CORSMiddleware

import uvicorn
from sqlalchemy.orm import Session

from app.utils import crud, models, schemas
from app.utils import processing
from app.utils.schemas import AdminUser, TokenData
from app.utils.processing import get_users, get_user, \
    get_password_hash, authenticate_user, create_access_token
from app.utils.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


load_dotenv()
SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(access_token: str = Depends(oauth2_scheme),
                           db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user_obj = await crud.get_users(db)
    user_dict = get_users(user_obj)
    user = get_user(user_dict, username=token_data.username)

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: AdminUser = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/access_token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user_obj = await crud.get_users(db)
    user_dict = get_users(user_obj)
    user = authenticate_user(
        user_dict, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: AdminUser = Depends(get_current_active_user)):
    return current_user


@app.post("/user/create/")
async def create_user(
        user: schemas.AdminUserCreate,
        db: Session = Depends(get_db),
        current_user: AdminUser = Depends(get_current_active_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    password_hashed = get_password_hash(user.password)
    return await crud.create_admin_user(db=db, user=user, password=password_hashed)


@app.post("/user/update/")
async def update_user(
        user: schemas.AdminUserCreate,
        db: Session = Depends(get_db),
        current_user: AdminUser = Depends(get_current_active_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_user = await crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="User is not registered")
    password_hashed = get_password_hash(user.password)
    return await crud.update_admin_user(db=db, user=user, password=password_hashed)


@app.post("/user/delete/")
async def delete_user(
        user: schemas.AdminUserDelete, db: Session = Depends(get_db),
        current_user: AdminUser = Depends(get_current_active_user)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not registered")
    else:
        return await crud.delete_admin_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.AdminUser])
async def read_users(users: AdminUser = Depends(get_current_active_user),
                     skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.AdminUser)
async def read_user(user_id: int, db: Session = Depends(get_db),
                    current_user: AdminUser = Depends(get_current_active_user)):
    db_user = await crud.get_user_by_id(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/data/upload/")
async def upload_data(db: Session = Depends(get_db),
                      current_user: AdminUser = Depends(
                          get_current_active_user)):
    return await crud.upload_data(db=db)


@app.get("/data/all", response_model=List[schemas.Data])
async def get_all_data(page: int, entries_per_page: int,
                       current_user: AdminUser = Depends(
        get_current_active_user), db: Session = Depends(get_db)):
    return await crud.paginate_data(page, entries_per_page, db)


@app.get("/data/filter_by")
async def filter_data(
        filter_parameter: str,
        save_as_csv: bool = False,
        city_name: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
        db: Session = Depends(get_db),
    current_user: AdminUser = Depends(
            get_current_active_user)):
    return await crud.filter_by_parameters(filter_parameter, city_name, range_start, range_end, db, save_as_csv)


@app.post("/data/update/{transaction_id}")
async def update_data(transaction_id: UUID,
                      data: schemas.DataUpdate,
                      db: Session = Depends(get_db),
                      current_user: AdminUser = Depends(
                          get_current_active_user)):

    db_data = await crud.get_data_by_id(db, transaction_id=transaction_id)
    if not db_data:
        raise HTTPException(status_code=400, detail="Data not found!")
    else:
        return await crud.update_data(db=db, data=data, transaction_id=transaction_id)


@app.post("/data/delete/")
async def delete_data(transaction_id: UUID,
                      db: Session = Depends(get_db),
                      current_user: AdminUser = Depends(
                          get_current_active_user)
                      ):

    db_data = await crud.get_data_by_id(db, transaction_id=transaction_id)
    if not db_data:
        raise HTTPException(status_code=400, detail="Data not found")
    else:
        return await crud.delete_data(db=db, transaction_id=transaction_id)


if __name__ == "__main__":
    processing.init_admin_user(db=SessionLocal())  # create default admin user
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
