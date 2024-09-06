import requests
import xml.etree.ElementTree as ET
import os

# URL API для получения данных о дисках
api_url_disks_1 = "https://ka2.sibzapaska.ru/export.xml"
api_url_disks_2 = "https://yngmzleen.github.io/drom/products.xml"
api_url_product = "http://ka2.sibzapaska.ru/API/hs/v1/product"

# Учетные данные для API
username = "API_client"
password = "rWp7mFWXRKOq"

# Заголовки для запроса (если необходимо)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получение данных из API
response_1 = requests.get(api_url_disks_1, headers=headers, verify=False)
response_1.raise_for_status()  # Проверка успешности запроса
response_2 = requests.get(api_url_disks_2, headers=headers, verify=False)
response_2.raise_for_status()  # Проверка успешности запроса
response_product = requests.get(api_url_product, auth=(username, password))
response_product.raise_for_status()  # Проверка успешности запроса

# Парсинг XML данных
root_1 = ET.fromstring(response_1.content)
root_2 = ET.fromstring(response_2.content)
product_data = response_product.json()

# Создание нового корневого элемента для нового XML файла
new_root = ET.Element("items")

# Поля, которые нужно сохранить и их новые названия
fields_to_keep = {
    'name': 'name',
    'brand': 'brand',
    'model': 'model',
    'code': 'article',
    'width': 'width',
    'diameter': 'diameter',
    'color': 'color',
    'vendor_code': 'cae',
    'holes': 'holes',
    'ET': 'et',
    'diam_holes': 'diam_holes',
    'type': 'type',
    'diam_center': 'diam_center'
}

# Словарь для хранения цен и остатков из второй API
prices_dict = {}
counts_dict = {}

# Заполнение словаря цен и остатков из второй API
for item in root_2.findall('disk'):
    code_element = item.find('Код')
    if code_element is not None:
        code = code_element.text
        price_element = item.find('Розничая_Цена')
        count_element = item.find('Остаток')
        if price_element is not None:
            price = price_element.text
            prices_dict[code] = price
        if count_element is not None:
            count = count_element.text
            counts_dict[code] = count

# Словарь для хранения оптовых цен из третьей API
wholesale_prices_dict = {}

# Заполнение словаря оптовых цен из третьей API
for product in product_data:
    code = product.get('Код')
    wholesale_price = product.get('Оптовая_Цена')
    if code and wholesale_price:
        wholesale_prices_dict[code] = wholesale_price

# Копирование данных из первой API и добавление цен и остатков из второй API
for item in root_1.findall('disk'):
    new_item = ET.SubElement(new_root, "item")
    
    for field in fields_to_keep:
        element = item.find(field)
        if element is not None:
            new_element = ET.SubElement(new_item, fields_to_keep[field])
            new_element.text = element.text
    
    # Добавление цены и остатка, если товар найден во второй API
    code_element = item.find('code')
    if code_element is not None:
        code = code_element.text
        if code in prices_dict:
            price_element = ET.SubElement(new_item, 'price')
            price_element.text = prices_dict[code]
        if code in counts_dict:
            count_element = ET.SubElement(new_item, 'count')
            count_element.text = counts_dict[code]
    
    # Добавление оптовой цены, если товар найден в третьей API
    if code in wholesale_prices_dict:
        opt_element = ET.SubElement(new_item, 'opt')
        opt_element.text = wholesale_prices_dict[code]

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
tree.write("zapaska_disks.xml", encoding="utf-8", xml_declaration=True)

print("Новый XML файл для дисков успешно создан.")
