import requests
import xml.etree.ElementTree as ET

# URL API для получения данных
api_url = "https://abcdisk54.ru/ftp/Brinex_shina.xml"

# Заголовки для запроса (если необходимо)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Получение данных из API
response = requests.get(api_url, headers=headers)
response.raise_for_status()  # Проверка успешности запроса

# Парсинг XML данных
root = ET.fromstring(response.content)

# Проверка содержимого root
print("Корневой элемент:", root.tag)

# Создание нового корневого элемента для нового XML файла
new_root = ET.Element("items")

# Поля, которые нужно сохранить
fields_to_keep = {
    'product_id': 'article',
    'name': 'name',
    'price': 'price',
    'countAll': 'count',
    'stockName': 'stock',
    'brand': 'brand',
    'shirina_secheniya': 'width',
    'visota_secheniya': 'height',
    'radius': 'diameter',
    'seasonality': 'season'
}

# Копирование данных из исходного XML
for item in root.findall('.//item'):
    new_item = ET.SubElement(new_root, "item")
    
    for field in fields_to_keep:
        element = item.find(field)
        if element is not None:
            new_element = ET.SubElement(new_item, fields_to_keep[field])
            new_element.text = element.text

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
tree.write("brinex_tyres.xml", encoding="utf-8", xml_declaration=True)

print("Новый XML файл успешно создан.")
