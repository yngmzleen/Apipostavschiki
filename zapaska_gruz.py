import xml.etree.ElementTree as ET
import requests
import re
import os

# URL API для получения данных о шинах
api_url_tyres_1 = "https://ka2.sibzapaska.ru/export.xml"
api_url_tyres_2 = "https://yngmzleen.github.io/drom/products.xml"
api_url_product = "http://ka2.sibzapaska.ru/API/hs/v1/product"

# Учетные данные для API
username = "API_client"
password = "rWp7mFWXRKOq"

# Заголовки для запроса (если необходимо)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получение данных из API
response_1 = requests.get(api_url_tyres_1, headers=headers, verify=False)
response_1.raise_for_status()  # Проверка успешности запроса
response_2 = requests.get(api_url_tyres_2, headers=headers, verify=False)
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
    'diameter': 'diameter',
    'height': 'height',
    'width': 'width',
    'season': 'season',
    'vendor_code': 'cae'
}

# Словарь для хранения цен и остатков из второй API
prices_dict = {}
counts_dict = {}

# Заполнение словаря цен и остатков из второй API
for item in root_2.findall('tyres'):
    nomenclature = item.find('Номенклатура').text
    price = item.find('Розничая_Цена').text
    count = item.find('Остаток').text
    prices_dict[nomenclature] = price
    counts_dict[nomenclature] = count

# Словарь для хранения оптовых цен из третьей API
wholesale_prices_dict = {}

# Заполнение словаря оптовых цен из третьей API
for product in product_data:
    code = product.get('Код')
    wholesale_price = product.get('Оптовая_Цена')
    if code and wholesale_price:
        wholesale_prices_dict[code] = wholesale_price

# Копирование данных из первой API и добавление цен и остатков из второй API
for item in root_1.findall('tyres'):
    load_index = item.find('load_index')
    if load_index is not None and re.match(r'^\d{2,3}/\d{2,3}$', load_index.text):
        new_item = ET.SubElement(new_root, "item")
        
        for field in fields_to_keep:
            element = item.find(field)
            if element is not None:
                new_element = ET.SubElement(new_item, fields_to_keep[field])
                new_element.text = element.text
        
        # Добавление цены и остатка, если товар найден во второй API
        name = item.find('name').text
        if name in prices_dict:
            price_element = ET.SubElement(new_item, 'price')
            price_element.text = prices_dict[name]
        if name in counts_dict:
            count_element = ET.SubElement(new_item, 'count')
            count_element.text = counts_dict[name]
        
        # Проверка наличия слова "шип" в поле <name> и добавление поля <spikes>шипы</spikes>
        if re.search(r'\bшип\b', name, re.IGNORECASE):
            spikes_element = ET.SubElement(new_item, 'spikes')
            spikes_element.text = 'шипы'
        
        # Добавление оптовой цены, если товар найден в третьей API
        code = item.find('code').text
        if code in wholesale_prices_dict:
            opt_element = ET.SubElement(new_item, 'opt')
            opt_element.text = wholesale_prices_dict[code]

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
tree.write("zapaska_gruz.xml", encoding="utf-8", xml_declaration=True)

print("Новый XML файл для шин успешно создан.")
