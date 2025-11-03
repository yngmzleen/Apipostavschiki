import ftplib
import os
import sys
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# Данные для подключения к FTP серверу (из переменных окружения)
FTP_HOST = os.getenv('BRINEX_FTP_HOST')
FTP_PORT = int(os.getenv('BRINEX_FTP_PORT', '21'))
FTP_USER = os.getenv('BRINEX_FTP_USER')
FTP_PASS = os.getenv('BRINEX_FTP_PASS')

# Проверка наличия необходимых переменных окружения
if not all([FTP_HOST, FTP_USER, FTP_PASS]):
    print("❌ Ошибка: не установлены необходимые переменные окружения!")
    print("   Требуются: BRINEX_FTP_HOST, BRINEX_FTP_USER, BRINEX_FTP_PASS")
    print("   Опционально: BRINEX_FTP_PORT (по умолчанию: 21)")
    sys.exit(1)

# Имя файла для скачивания
INPUT_FILE = "Brinex_disk.xml"
OUTPUT_FILE = "brinex_disks.xml"

# Маппинг полей для дисков
FIELDS_MAPPING = {
    'id': 'article',
    'name': 'name',
    'price': 'price',
    'countAll': 'rest',
    'stockName': 'stock',
    'proizvoditel': 'brand',
    'shirina_diska': 'width',
    'radius': 'diameter',
    'et': 'et',
    'DescriptionOfColor': 'color',
    'vendor_code': 'cae',
    'material': 'type',
    'boltnum': 'holes',
    'boltdistance': 'diam_holes',
    'categoryname': 'model',
    'priceOpt': 'opt'
}


def connect_to_ftp():
    """Подключение к FTP серверу"""
    try:
        print(f"Подключение к FTP серверу {FTP_HOST}:{FTP_PORT}...")
        
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        
        print("✅ Успешное подключение к FTP серверу!")
        return ftp
        
    except ftplib.error_perm as e:
        print(f"❌ Ошибка авторизации: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return None


def download_file(ftp, remote_filename, local_filename=None):
    """Скачивание файла с FTP сервера"""
    if local_filename is None:
        local_filename = remote_filename
    
    try:
        # Получаем размер файла
        file_size = ftp.size(remote_filename)
        print(f"\n📥 Скачивание файла '{remote_filename}'...")
        print(f"   Размер: {file_size:,} байт ({file_size / 1024 / 1024:.2f} МБ)")
        
        # Скачиваем файл
        downloaded_bytes = 0
        
        def progress_callback(data):
            nonlocal downloaded_bytes
            downloaded_bytes += len(data)
            progress = (downloaded_bytes / file_size) * 100 if file_size > 0 else 0
            print(f"\r   Прогресс: {progress:.1f}% ({downloaded_bytes:,} / {file_size:,} байт)", end="")
            file_handle.write(data)
        
        with open(local_filename, 'wb') as file_handle:
            ftp.retrbinary(f'RETR {remote_filename}', progress_callback)
        
        print(f"\n✅ Файл '{remote_filename}' успешно скачан")
        
        # Проверяем размер скачанного файла
        local_size = os.path.getsize(local_filename)
        if local_size == file_size:
            print(f"   Проверка: размеры совпадают ({local_size:,} байт)")
        else:
            print(f"⚠️  Предупреждение: размеры не совпадают! Локальный: {local_size:,}, удаленный: {file_size:,}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка скачивания файла '{remote_filename}': {e}")
        return False


def process_disks_xml(input_filename, output_filename):
    """Обработка XML файла с дисками"""
    try:
        print(f"\n🔄 Обработка файла с дисками '{input_filename}'...")
        
        # Парсинг исходного XML
        tree = ET.parse(input_filename)
        root = tree.getroot()
        
        print(f"   Корневой элемент: {root.tag}")
        
        # Подсчет элементов item
        items = root.findall('.//item')
        print(f"   Найдено элементов: {len(items)}")
        
        # Создание нового корневого элемента
        new_root = ET.Element("items")
        
        processed_count = 0
        diam_center_count = 0
        
        # Обработка каждого элемента
        for item in items:
            new_item = ET.SubElement(new_root, "item")
            
            # Копирование и переименование полей
            for old_field, new_field in FIELDS_MAPPING.items():
                element = item.find(old_field)
                if element is not None:
                    new_element = ET.SubElement(new_item, new_field)
                    new_element.text = element.text
            
            # Извлечение значения после "CB" и до пробела из поля <name>
            name_element = item.find('name')
            if name_element is not None and name_element.text:
                name_text = name_element.text
                match = re.search(r'CB(\d+\.\d+)', name_text)
                if match:
                    diam_center_value = match.group(1)
                    diam_center_element = ET.SubElement(new_item, 'diam_center')
                    diam_center_element.text = diam_center_value
                    diam_center_count += 1
            
            processed_count += 1
        
        # Запись в новый XML файл
        new_tree = ET.ElementTree(new_root)
        new_tree.write(output_filename, encoding="utf-8", xml_declaration=True)
        
        print(f"✅ Обработано элементов: {processed_count}")
        print(f"✅ Извлечено значений diam_center: {diam_center_count}")
        print(f"✅ Результат сохранен в '{output_filename}'")
        
        # Проверка размера выходного файла
        output_size = os.path.getsize(output_filename)
        print(f"   Размер выходного файла: {output_size:,} байт ({output_size / 1024 / 1024:.2f} МБ)")
        
        return True
        
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML файла '{input_filename}': {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка обработки файла '{input_filename}': {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_xml_file(filename):
    """Проверка корректности XML файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read(1000)  # Читаем первые 1000 символов
            
        if content.strip().startswith('<?xml'):
            print(f"✅ Файл '{filename}' является корректным XML")
            return True
        else:
            print(f"⚠️  Файл '{filename}' не является XML файлом")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки файла '{filename}': {e}")
        return False


def main():
    """Основная функция"""
    print("🚀 ОБРАБОТКА XML ФАЙЛА С ДИСКАМИ")
    print("=" * 60)
    
    # ЭТАП 1: Подключение и скачивание
    print("\nЭТАП 1: СКАЧИВАНИЕ ФАЙЛА С FTP")
    print("-" * 60)
    
    ftp = connect_to_ftp()
    if not ftp:
        print("❌ Не удалось подключиться к серверу")
        sys.exit(1)
    
    try:
        # Скачиваем файл
        success = download_file(ftp, INPUT_FILE)
        
        # Закрываем FTP соединение
        try:
            ftp.quit()
            print("✅ Соединение с FTP сервером закрыто")
        except:
            pass
        
        if not success:
            print(f"❌ Не удалось скачать файл '{INPUT_FILE}'")
            sys.exit(1)
        
        # Проверяем корректность XML
        if not validate_xml_file(INPUT_FILE):
            print(f"❌ Файл '{INPUT_FILE}' не является корректным XML")
            sys.exit(1)
        
        # ЭТАП 2: Обработка файла
        print("\n" + "=" * 60)
        print("ЭТАП 2: ОБРАБОТКА ФАЙЛА")
        print("-" * 60)
        
        success = process_disks_xml(INPUT_FILE, OUTPUT_FILE)
        
        if not success:
            print(f"❌ Ошибка при обработке файла")
            sys.exit(1)
        
        # ИТОГИ
        print("\n" + "=" * 60)
        print("📊 ИТОГИ")
        print("=" * 60)
        
        input_size = os.path.getsize(INPUT_FILE)
        output_size = os.path.getsize(OUTPUT_FILE)
        
        print(f"\n✅ Исходный файл: {INPUT_FILE}")
        print(f"   Размер: {input_size:,} байт ({input_size / 1024 / 1024:.2f} МБ)")
        
        print(f"\n✅ Обработанный файл: {OUTPUT_FILE}")
        print(f"   Размер: {output_size:,} байт ({output_size / 1024 / 1024:.2f} МБ)")
        
        print(f"\n💾 Файлы сохранены в директории:")
        print(f"   {os.getcwd()}")
        
        # Удаляем исходный файл
        print(f"\n🗑️  Удаление исходного файла '{INPUT_FILE}'...")
        try:
            os.remove(INPUT_FILE)
            print(f"✅ Исходный файл '{INPUT_FILE}' успешно удален")
        except Exception as e:
            print(f"⚠️  Не удалось удалить файл '{INPUT_FILE}': {e}")
        
        print(f"\n✨ Обработка завершена успешно!")
        
    except Exception as e:
        print(f"\n❌ Общая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

