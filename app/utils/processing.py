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
