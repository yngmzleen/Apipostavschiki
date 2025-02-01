import xml.etree.ElementTree as ET
import requests
import re
import os
import logging
import warnings
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# URL API для получения данных о шинах
api_url = "https://yngmzleen.github.io/drom/tyres.xml"

# Заголовки для запроса (если необходимо)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получение данных из API
def fetch_data(url):
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Проверка успешности запроса
        return response.content
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе данных: {e}")
        return None

# Парсинг XML данных
def parse_xml(xml_content):
    if xml_content:
        try:
            return ET.fromstring(xml_content)
        except ET.ParseError as e:
            logging.error(f"Ошибка при парсинге XML: {e}")
            return None
    return None

# Получение данных из API
response_content = fetch_data(api_url)
if not response_content:
    logging.error("Не удалось получить данные из API")
    exit(1)

# Парсинг XML
root = parse_xml(response_content)
if not root:
    logging.error("Не удалось распарсить данные из API")
    exit(1)

# Создание нового корневого элемента для нового XML файла
new_root = ET.Element("items")

# Поля, которые нужно сохранить и их новые названия
fields_to_keep = {
    'cae': 'cae',
    'name': 'name',
    'retail': 'price',
    'rest': 'rest',
    'brand': 'brand',
    'model': 'model',
    'code': 'article',
    'diameter': 'diameter',
    'height': 'height',
    'width': 'width',
    'season': 'season',
    'vendor_code': 'cae',
    'img': 'img',
    'category': 'tyretype'
}

# Копирование данных из API и фильтрация по категории "Легковая"
for item in root.findall('tyres'):
    category = item.find('category')
    if category is not None and category.text.strip() == "Легковая":
        new_item = ET.SubElement(new_root, "item")
        
        for field, new_field in fields_to_keep.items():
            element = item.find(field)
            if element is not None and element.text is not None:
                new_element = ET.SubElement(new_item, new_field)
                new_element.text = element.text.strip()

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
output_file = "zapaska_tyres.xml"
tree.write(output_file, encoding="utf-8", xml_declaration=True)

logging.info(f"Новый XML файл для легковых шин успешно создан: {output_file}")
