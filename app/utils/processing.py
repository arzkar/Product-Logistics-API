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
from app.utils import models
import csv
import os

from typing import Optional
from dotenv import load_dotenv
from app.utils.schemas import AdminUserInDB
from app.utils import crud
from datetime import datetime, timedelta


from sqlalchemy.orm import Session
from jose import jwt

from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()
SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = "HS256"


def sql_query_to_csv(query_output):
    """ Converts output from a SQLAlchemy query to a .csv file.
    """
    with open('app/data/filter_results.csv', 'w') as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=['transaction_id', 'transaction_time', 'product_name',
                                 'quantity', 'unit_price', 'total_price', 'delivered_to_city'])
        writer.writeheader()
        for row in query_output:
            writer.writerow({
                'transaction_id': str(row.transaction_id),
                'transaction_time':  str(row.transaction_time),
                'product_name':  str(row.product_name),
                'quantity': int(row.quantity),
                'unit_price': float(row.unit_price),
                'total_price': int(row.quantity)*float(row.unit_price),
                'delivered_to_city': str(row.delivered_to_city)
            })


def get_users(db_data):
    data = {}
    for item in db_data:
        data.update({item.__dict__["username"]: {
            "username": item.__dict__["username"],
            "password":  item.__dict__["password"],
        }})

    return data


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return AdminUserInDB(**user_dict)


def authenticate_user(user_dict, username: str, password: str):
    user = get_user(user_dict, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def init_admin_user(db: Session):
    admin_exits = db.query(models.AdminUser).filter(
        models.AdminUser.username == "admin").first()

    if admin_exits is None:
        password_hashed = get_password_hash("admin")

        db_user = models.AdminUser(
            username="admin", password=password_hashed)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
