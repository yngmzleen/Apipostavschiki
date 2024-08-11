import requests
import xml.etree.ElementTree as ET
import re

# URL API для получения данных о дисках
api_url_rims = "https://b2b.4tochki.ru/export_data/M28244.xml"

# Заголовки для запроса (если необходимо)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получение данных из API
response = requests.get(api_url_rims, headers=headers)
response.raise_for_status()  # Проверка успешности запроса

# Парсинг XML данных
root = ET.fromstring(response.content)

# Создание нового корневого элемента для нового XML файла
new_root = ET.Element("items")

# Поля, которые нужно сохранить
fields_to_keep = {
    'cae': 'article',
    'brand': 'brand',
    'model': 'model',
    'color': 'color',
    'width': 'width',
    'diameter': 'diameter',
    'img_small': 'img_small',
    'name': 'name',
    'cae': 'cae',
    'bolts_count': 'holes',
    'bolts_spacing': 'diam_holes',
    'et': 'et',
    'rim_type': 'type',
    'dia': 'diam_center'
}

# Копирование данных из исходного XML
for item in root.findall('rims'):
    new_item = ET.SubElement(new_root, "item")
    
    for field in fields_to_keep:
        element = item.find(field)
        if element is not None:
            new_element = ET.SubElement(new_item, fields_to_keep[field])
            if field == 'cae':
                # Удаляем буквы "WHS" из значения поля <cae>
                new_element.text = re.sub(r'WHS', '', element.text)
            else:
                new_element.text = element.text

    # Добавляем все поля, содержащие 'rest_'
    for element in item:
        if element.tag.startswith('rest_'):
            new_element = ET.SubElement(new_item, element.tag)
            new_element.text = element.text

    # Заменяем все поля, содержащие 'price_..._rozn', на 'price'
    for element in item:
        if element.tag.startswith('price_') and element.tag.endswith('_rozn'):
            new_element = ET.SubElement(new_item, 'price')
            new_element.text = element.text

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
tree.write("4tochki_disk.xml", encoding="utf-8", xml_declaration=True)

print("Новый XML файл для дисков успешно создан.")
