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

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.utils.database import Base
import uuid


class Data(Base):
    __tablename__ = "data_table"

    transaction_id = Column(
        UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    transaction_time = Column(DateTime)
    product_name = Column(String)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_price = Column(Float)
    delivered_to_city = Column(String)


class AdminUser(Base):
    __tablename__ = "admin_user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    disabled = Column(Boolean, default=False)
