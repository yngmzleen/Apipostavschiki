import requests
import xml.etree.ElementTree as ET

# URL API для получения данных
api_url = "https://b2b.4tochki.ru/export_data/M28274.xml"

# Заголовки для запроса (если необходимо)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получение данных из API
response = requests.get(api_url, headers=headers)
response.raise_for_status()  # Проверка успешности запроса

# Парсинг XML данных
root = ET.fromstring(response.content)

# Создание нового корневого элемента для нового XML файла
new_root = ET.Element("items")

# Поля, которые нужно сохранить
fields_to_keep = {
    'cae': 'article',
    'price': 'price',
    'brand': 'brand',
    'model': 'model',
    'width': 'width',
    'height': 'height',
    'diameter': 'diameter',
    'season': 'season',
    'img_small': 'img_small',
    'name': 'name'
}

# Копирование данных из исходного XML
for item in root.findall('tires'):
    new_item = ET.SubElement(new_root, "item")
    
    for field in fields_to_keep:
        element = item.find(field)
        if element is not None:
            new_element = ET.SubElement(new_item, fields_to_keep[field])
            new_element.text = element.text

    # Добавляем все поля, содержащие 'rest_'
    for element in item:
        if element.tag.startswith('rest_'):
            new_element = ET.SubElement(new_item, element.tag)
            new_element.text = element.text

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
tree.write("4tochki_tyres.xml", encoding="utf-8", xml_declaration=True)

print("Новый XML файл успешно создан.")
