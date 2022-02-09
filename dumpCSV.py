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

import csv
from faker import Faker  # generates fake data
import datetime
import uuid
import random


def data_generate(records, headers):
    fake = Faker('en_IN')
    with open("app/data/data.csv", 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader()
        for _ in range(records):
            quantity = random.randint(1, 100)
            unit_price = random.uniform(2.25, 55.75)
            writer.writerow({
                'transaction_id': uuid.uuid4(),
                'transaction_time': fake.date(pattern="%Y%m%d %H%M%S", end_datetime=datetime.date(2021, 1, 1)),
                'product_name': fake.word(),
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': quantity*unit_price,
                'delivered_to_city': fake.city()
            })


if __name__ == '__main__':
    records = 1000
    headers = ['transaction_id', 'transaction_time', 'product_name',
               'quantity', 'unit_price', 'total_price', 'delivered_to_city']
    data_generate(records, headers)
    print("CSV generated at `app/data/data.csv`")
