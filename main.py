from typing import List, Optional
from uuid import UUID
from dotenv import load_dotenv
import os

from fastapi import Depends, FastAPI, HTTPException

from starlette.middleware.cors import CORSMiddleware

import uvicorn
from sqlalchemy.orm import Session

from app.utils import crud, models, schemas
from app.utils.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

load_dotenv()
SECRET_KEY = str(os.getenv("SECRET_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/data/upload/")
async def upload_data(db: Session = Depends(get_db)):
    return await crud.upload_data(db=db)


@app.get("/data/all", response_model=List[schemas.Data])
async def get_all_data(page: int, entries_per_page: int, db: Session = Depends(get_db)):
    return await crud.paginate_data(page, entries_per_page, db)


@app.get("/data/filter_by")
async def filter_data(
        filter_parameter: str,
        save_as_csv: bool = False,
        city_name: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
        db: Session = Depends(get_db)):
    return await crud.filter_by_parameters(filter_parameter, city_name, range_start, range_end, db, save_as_csv)


@app.post("/data/update/{transaction_id}")
async def update_data(transaction_id: UUID,
                      data: schemas.DataUpdate,
                      db: Session = Depends(get_db)):

    db_data = await crud.get_data_by_id(db, transaction_id=transaction_id)
    if not db_data:
        raise HTTPException(status_code=400, detail="Data not found!")
    else:
        return await crud.update_data(db=db, data=data, transaction_id=transaction_id)


@app.post("/data/delete/")
async def delete_data(transaction_id: UUID,
                      db: Session = Depends(get_db)
                      ):

    db_data = await crud.get_data_by_id(db, transaction_id=transaction_id)
    if not db_data:
        raise HTTPException(status_code=400, detail="Data not found")
    else:
        return await crud.delete_data(db=db, transaction_id=transaction_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
