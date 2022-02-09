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

from datetime import datetime
import pandas as pd
import chardet
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.utils import models, schemas, database, processing


async def get_data_by_id(db: Session, transaction_id: UUID):
    return db.query(models.Data).filter(models.Data.transaction_id == transaction_id).first()


async def upload_data(db: Session):

    with open('app/data/data.csv', 'rb') as file:
        result = chardet.detect(file.read())
    df = pd.read_csv('app/data/data.csv', encoding=result['encoding'])
    try:
        df.to_sql('data_table', con=database.engine,
                  index=False, if_exists='append')
        db.commit()
    except IntegrityError:
        return "IntegrityError: Data already stored in the database!"

    return "CSV Data successfully uploaded to the database!"


async def update_data(db: Session, data: schemas.DataUpdate, transaction_id: UUID):
    db.query(models.Data).filter(
        models.Data.transaction_id == transaction_id). \
        update(
            {
                models.Data.transaction_time: data.transaction_time,
                models.Data.product_name: data.product_name,
                models.Data.quantity: data.quantity,
                models.Data.unit_price: data.unit_price,
                models.Data.total_price: data.total_price,
                models.Data.delivered_to_city: data.delivered_to_city
            }
    )
    db.commit()
    return "Data updated successfully"


async def delete_data(db: Session, transaction_id: UUID):
    db_data = db.query(models.Data).filter(
        models.Data.transaction_id == transaction_id).first()
    db.delete(db_data)
    db.commit()
    return "Data deleted successfully"


async def filter_by_parameters(filter_parameter: str, city_name: str,
                               range_start: str, range_end: str, db: Session,
                               save_as_csv: bool):
    dt_format = "%Y%m%d %H%M%S"
    try:
        range_start_dt = datetime.strptime(range_start, dt_format)
        range_end_dt = datetime.strptime(range_end, dt_format)
    except (ValueError, TypeError):
        range_start_dt = None
        range_end_dt = None

    if filter_parameter == 'city':
        result = db.query(models.Data).filter(
            func.lower(models.Data.delivered_to_city) == city_name.lower()).all()
    elif filter_parameter == 'date':
        result = db.query(models.Data).filter(
            models.Data.transaction_time.between(range_start_dt, range_end_dt)).all()
    elif filter_parameter == 'total_price':
        result = db.query(models.Data).filter(
            models.Data.total_price.between(range_start_dt, range_end_dt)).all()
    elif filter_parameter == 'quantity':
        result = db.query(models.Data).filter(
            models.Data.quantity.between(range_start_dt, range_end_dt)).all()
    else:
        return "Data not found!"

    if save_as_csv:
        processing.sql_query_to_csv(result)
    return result


async def paginate_data(page: int, entries_per_page: int, db: Session):
    all_rows = db.query(models.Data).all()
    output = [all_rows[i:i + entries_per_page]
              for i in range(0, len(all_rows), entries_per_page)]

    return output[page-1]  # index starts from 0
