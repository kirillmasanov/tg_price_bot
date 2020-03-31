from pymongo import MongoClient

from datetime import date

import settings
from data import main_data

db = MongoClient(settings.MONGO_LINK)[settings.MONGO_DB]


def get_create_data(db):
    for item in main_data():
        position = db.items.find_one({'article': item['article']})
        if not position:
            position = {'article': item['article'],
                    'name': item['name'],
                    'price': item['price'],
                    'date': str(date.today())
                    }
            db.items.insert_one(position)
        else:
            new_price = item['price']
            if position['price'] == new_price:
                print('Такая есть!')
            else:
                print(f'Новая цена: {new_price}')
                db.items.update_one(
                    {'article': item['article']},
                    {'$set': {'price': item['price'],
                              'date': str(date.today())}}
                )
                print(f'Обновил!')


# print(f'{db.items.find_one({"price": 203990})}')

get_create_data(db)
# print(date.today())