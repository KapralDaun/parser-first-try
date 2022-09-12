import requests
import json
import sys
import codecs
from config import *
import os
import math

''' Функция получения данных о ноутах с сайта МВИДЕО'''


def get_data():
    params = {
        'categoryId': '181',
        'offset': '0',
        'limit': '24',
        'doTranslit': 'true',
    }

    if not os.path.exists('data'):  # Если не существует директории дата, создаем её
        os.mkdir('data')

    s = requests.Session()  # Создаем объект сессии и отправим через нее первый запрос
    response = s.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                     headers=headers).json()

    total_items = response.get('body').get('total')  # Получим количество товаров

    if total_items is None:
        return '[!] There are no items here [!]'

    pages_count = math.ceil(total_items / 24)

    print(f'[INFO] Total items: {total_items} | Total pages: {pages_count}')

    products_ids = {}  # Словарь ид оборудований
    products_description = {}  # Словарь описания товаров
    products_price = {}  # Словарь с ценами на товары

    for i in range(pages_count):
        offset = f'{i * 24}'

        params = {
            'categoryId': '181',
            'offset': offset,  # Передаем в параметры оффсет
            'limit': '24',
            'doTranslit': 'true',
        }

        response = s.get('https://www.mvideo.ru/bff/products/listing', params=params, cookies=cookies,
                         headers=headers).json()

        products_ids_list = response.get('body').get('products')  # Получаем список ид текущей итерации
        products_ids[i] = products_ids_list  # Запишем список в словарь с ключом = номеру итерации
        json_data = {  # Формируем второй запрос для получения описаний товаров
            'productIds': products_ids_list,
            'mediaTypes': [
                'images',
            ],
            'category': True,
            'status': True,
            'brand': True,
            'propertyTypes': [
                'KEY',
            ],
            'propertiesConfig': {
                'propertiesPortionSize': 5,
            },
            'multioffer': False,
        }

        response = s.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                                 json=json_data).json()
        products_description[i] = response  # Получаем описание товаров в виде ответа

        products_ids_str = ','.join(products_ids_list)  # Переводим список ид в строку для передачи в запрос

        params = {
            'productIds': products_ids_str,
            'addBonusRubles': 'true',
            'isPromoApplied': 'true',
        }

        #  Получим данные о ценах по строке ид
        response = s.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                                headers=headers).json()

        material_prices = response.get('body').get('materialPrices')  # Получаем список словарей с ценами

        for item in material_prices:  # Пробежимся по списку и составим словарь, который запишем в JSON
            item_id = item.get('price').get('productId')
            item_base_price = item.get('price').get('basePrice')
            item_sale_price = item.get('price').get('salePrice')
            item_bonus = item.get('bonusRubles').get('total')

            products_price[item_id] = {
                'item_basePrice': item_base_price,
                'item_salePrice': item_sale_price,
                'item_bonus': item_bonus,
            }

        print(f'[INFO] Finished {i + 1} of the {pages_count} pages!')
        with open('data/1_products_ids.json', 'w', encoding="utf-8") as file:  # Запишем ид в файл JSON
            json.dump(products_ids, file, indent=4, ensure_ascii=False)

        with open('data/2_products_description.json', 'w', encoding="utf-8") as file:  # Запишем ид в файл JSON
            json.dump(products_description, file, indent=4, ensure_ascii=False)

        with open('data/3_products_prices.json', 'w', encoding="utf-8") as file:  # Запишем ид в файл JSON
            json.dump(products_price, file, indent=4, ensure_ascii=False)
"""
    products_ids = response.get('body').get('products')  # Достанем ид товаров

    with open('1_products_ids.json', 'w') as file:  # Запишем ид в файл JSON
        json.dump(products_ids, file, indent=4, ensure_ascii=False)

    # print(products_ids)

    json_data = {
        'productIds': products_ids,  # Вместо списка подставляем products_ids, на выходе получаем json
        'mediaTypes': [
            'images',
        ],
        'category': True,
        'status': True,
        'brand': True,
        'propertyTypes': [
            'KEY',
        ],
        'propertiesConfig': {
            'propertiesPortionSize': 5,
        },
        'multioffer': False,
    }

    response = requests.post('https://www.mvideo.ru/bff/product-details/list', cookies=cookies, headers=headers,
                             json=json_data).json()

    #  print(len(response.get('body').get('products')))

    with open('2_items.json', 'w', encoding="utf-8") as file:  # Запишем в файл JSON
        json.dump(response, file, indent=4, ensure_ascii=False)

    products_ids_str = ','.join(products_ids)

    params = {
        'productIds': products_ids_str,
        'addBonusRubles': 'true',
        'isPromoApplied': 'true',
    }
    #  Получим данные о ценах по строке ид
    response = requests.get('https://www.mvideo.ru/bff/products/prices', params=params, cookies=cookies,
                            headers=headers).json()

    with open('3_prices.json', 'w', encoding="utf-8") as file:  # Запишем в третий файл полученные данные о ценах
        json.dump(response, file, indent=4, ensure_ascii=False)

    items_prices = {}

    material_prices = response.get('body').get('materialPrices')

    for i in material_prices:  # Пробежимся по списку и составим словарь, который запишем в JSON
        item_id = i.get('price').get('productId')
        item_base_price = i.get('price').get('basePrice')
        item_sale_price = i.get('price').get('salePrice')
        item_bonus = i.get('bonusRubles').get('total')

        items_prices[item_id] = {
            'item_basePrice': item_base_price,
            'item_salePrice': item_sale_price,
            'item_bonus': item_bonus,
        }

        with open('4_items_price.json', 'w', encoding="utf-8") as file:
            json.dump(items_prices, file, indent=4, ensure_ascii=False)

"""


def get_result():  # Функция обобщения результатов
    with open('data/2_products_description.json', encoding="utf-8") as file:  # Открываем файл с описание товаров
        products_data = json.load(file)

    with open('data/3_products_prices.json', encoding="utf-8") as file:  # Открываем файл с ценами на товары
        products_prices = json.load(file)

    for items in products_data.values():  # Пробегаемся циклом по значениям словаря
        products = items.get('body').get('products')

    # products_data = products_data.get('body').get('products')

        for i in products:
            product_id = i.get('productId')

            if product_id in products_prices:
                prices = products_prices[product_id]

            i['item_basePrice'] = prices.get('item_basePrice')
            i['item_salePrice'] = prices.get('item_salePrice')
            i['item_bonus'] = prices.get('item_bonus')
            i['item_link'] = f'https://www.mvideo.ru/products/{i.get("nameTranslit")}-{product_id}'  # Формируем ссылку на товар

    with open('data/4_result.json', 'w', encoding="utf-8") as file:  # Запишем результаты в файл №4
        json.dump(products_data, file, indent=4, ensure_ascii=False)


def main():
    get_data()
    get_result()


if __name__ == '__main__':
    main()
