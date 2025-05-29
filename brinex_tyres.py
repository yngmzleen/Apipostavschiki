import requests
import xml.etree.ElementTree as ET

api_url_rims = os.getenv('BRINEX_T')
if not api_url_rims:
    raise ValueError("Не установлена переменная окружения BRINEX_T с URL API")

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
    'id': 'article',
    'name': 'name',
    'price': 'price',
    'countAll': 'rest',
    'stockName': 'stock',
    'brand': 'brand',
    'shirina_secheniya': 'width',
    'visota_secheniya': 'height',
    'radius': 'diameter',
    'seasonality': 'season',
    'vendor_code': 'cae',
    'categoryname': 'model',
    'priceOpt': 'opt'
}

# Копирование данных из исходного XML
for item in root.findall('.//item'):
    new_item = ET.SubElement(new_root, "item")
    
    for field in fields_to_keep:
        element = item.find(field)
        if element is not None:
            new_element = ET.SubElement(new_item, fields_to_keep[field])
            new_element.text = element.text
    
    # Проверка наличия поля <spikes>Да</spikes> и добавление поля <spikes>шипы</spikes>
    spikes_element = item.find('spikes')
    if spikes_element is not None and spikes_element.text == 'Да':
        new_spikes_element = ET.SubElement(new_item, 'spikes')
        new_spikes_element.text = 'шипы'

# Запись данных в новый XML файл
tree = ET.ElementTree(new_root)
tree.write("brinex_tyres.xml", encoding="utf-8", xml_declaration=True)

print("Новый XML файл успешно создан.")
