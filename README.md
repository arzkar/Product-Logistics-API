<h1 align="center">Product Logistics API</h1>

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A basic Product Logistics API which can be used to track the transactions of different products and its delivery to different cities.<br><br>
The `app/data/data.csv` file can be replaced according to your needs since the database is constructed using this csv file.<br>
For testing purposes, `dumpCSV.py` uses `faker` library to generate a fake dataset which is used to run the demo. This csv file is saved at `app/data/data.csv`.

# Database Schema

```
product_logistics_db=> \d data_table;
                            Table "public.data_table"
      Column       |            Type             | Collation | Nullable | Default
-------------------+-----------------------------+-----------+----------+---------
 transaction_id    | uuid                        |           | not null |
 transaction_time  | timestamp without time zone |           |          |
 product_name      | character varying           |           |          |
 quantity          | integer                     |           |          |
 unit_price        | double precision            |           |          |
 total_price       | double precision            |           |          |
 delivered_to_city | character varying           |           |          |
```

# Configure PostgreSQL

- Install PostgreSQL in your respective OS.
- Run the following commands to create an User as well as a database.

```
sudo su postgres;
psql -c "CREATE USER product_logistics_api WITH ENCRYPTED PASSWORD 'product_logistics_api';"
psql -c "CREATE DATABASE product_logistics_db;"
psql -c "GRANT ALL privileges on database product_logistics_db to product_logistics_api;"
```

## Environent Variables

- Create an `.env` file at the root directory which will contain `SQLALCHEMY_DATABASE_URL` & `SECRET_KEY` for the API.

- Check `.env.ex` for an example.

# API Usage

This API has been developed with Python version 3.8.5 and it is expected that the Python version installed in your system is 3.8.5 or above.

## Install the dependencies & run

Install dependencies using-

```
pip install -r requirements.txt
```

Run the API using-

```
python main.py
```

## API endpoints

- Go to the below url to view the Swagger UI. It will list all the endpoints and you can also execute the GET and POST requests from the UI itself.<br>

  ```
  http://0.0.0.0:5000/docs#/
  ```

- `/data/upload`: API endpoint to upload the created CSV file to the server. The contents in the file would be moved to a Database (either PostgreSQL or MySQL as configured).

- `/data/all`: API to query all rows from the database with pagination (entries per page should be passed as query parameter).

- `/data/filter_by`:

  - API to query rows from database with filter. The following filters should be supported:
    (a) Date range
    (b) Total Price range
    (c) Quantity range
    (d) City name

  - The filter parameters are: `city`, `date`, `total_price` and `quantity`.

  - The query result is downloaded as CSV file if `save_as_csv=true` parameter is passed in the query. It is saved as `app/data/filter_result.csv`.

- `/data/update/{transaction_id}`: API to update any row in the database.

- `/data/delete`: API to delete an entry in the database based on given input.

---

### Notes:

- `dumpCSV.py` which can be found in the root directory. Uses `faker` python library to build 1000 records of fake data which is saved as a CSV file at `app/data/data.csv`

---
