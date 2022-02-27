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

from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DataBase(BaseModel):
    pass


class DataCreate(DataBase):

    transaction_id: UUID = Field(default_factory=uuid4)
    transaction_time: datetime
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    delivered_to_city: str


class DataUpdate(DataBase):
    transaction_time: datetime
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    delivered_to_city: str


class DataDelete(DataBase):
    transaction_id: UUID = Field(default_factory=uuid4)


class Data(DataBase):
    transaction_id: UUID = Field(default_factory=uuid4)
    transaction_time: datetime
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    delivered_to_city: str

    class Config:
        orm_mode = True


class AdminUserBase(BaseModel):
    pass


class AdminUserCreate(AdminUserBase):
    username: str
    password: str


class AdminUserDelete(AdminUserBase):
    username: str


class AdminUserInDB(AdminUserBase):
    username: str
    password: str
    disabled: Optional[bool] = False


class AdminUser(AdminUserBase):
    user_id: int
    username: str
    data: List[Data] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
