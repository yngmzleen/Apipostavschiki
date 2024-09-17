import xml.etree.ElementTree as ET
import requests
import re
import os
import logging
import warnings
import json

# Отключение предупреждений о небезопасных запросах
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Настройка логирования
logging.basicConfig(level=logging.INFO)

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
def fetch_data(url, auth=None):
    try:
        response = requests.get(url, headers=headers, auth=auth, verify=False)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе данных: {e}")
        return None

# Парсинг XML данных
def parse_xml(xml_content):
    if xml_content:
        return ET.fromstring(xml_content)
    return None

# Парсинг JSON данных
def parse_json(json_content):
    if json_content:
        return json.loads(json_content)
    return None

# Получение данных из API
response_1_content = fetch_data(api_url_tyres_1)
response_2_content = fetch_data(api_url_tyres_2)
response_product_content = fetch_data(api_url_product, auth=(username, password))

if not all([response_1_content, response_2_content, response_product_content]):
    logging.error("Не удалось получить данные из одного или нескольких API")
    exit(1)

root_1 = parse_xml(response_1_content)
root_2 = parse_xml(response_2_content)
product_data = parse_json(response_product_content)

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
    nomenclature = item.find('Номенклатура').text if item.find('Номенклатура') is not None else None
    price = item.find('Розничая_Цена').text if item.find('Розничая_Цена') is not None else None
    count = item.find('Остаток').text if item.find('Остаток') is not None else None
    if nomenclature and price:
        prices_dict[nomenclature] = price
    if nomenclature and count:
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
    new_item = ET.SubElement(new_root, "item")
    
    for field in fields_to_keep:
        element = item.find(field)
        if element is not None:
            new_element = ET.SubElement(new_item, fields_to_keep[field])
            new_element.text = element.text
    
    # Добавление цены и остатка, если товар найден во второй API
    name = item.find('name').text if item.find('name') is not None else None
    if name and name in prices_dict:
        price_element = ET.SubElement(new_item, 'price')
        price_element.text = prices_dict[name]
    if name and name in counts_dict:
        count_element = ET.SubElement(new_item, 'count')
        count_element.text = counts_dict[name]
    
    # Проверка наличия слова "шип" в поле <name> и добавление поля <spikes>шипы</spikes>
    if name and re.search(r'\bшип\b', name, re.IGNORECASE):
        spikes_element = ET.SubElement(new_item, 'spikes')
        spikes_element.text = 'шипы'
    
    # Добавление оптовой цены, если товар найден в третьей API
    code = item.find('code').text if item.find('code') is not None else None
    if code and code in wholesale_prices_dict:
        opt_element = ET.SubElement(new_item, 'opt')
        opt_element.text = wholesale_prices_dict[code]

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
output_file = "zapaska_tyres.xml"
tree.write(output_file, encoding="utf-8", xml_declaration=True)

logging.info(f"Новый XML файл для шин успешно создан: {output_file}")
