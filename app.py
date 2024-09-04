# from flask import Flask, render_template
# import requests
# import xmltodict
# import os
#
# app = Flask(__name__)
#
# # Define the URL for loading XML data
# xml_url = 'https://b2b.4tochki.ru/export_data/M28244.xml'
#
# # Define the route for displaying XML data
# @app.route('/')
# def index():
#     # Load XML data from URL
#     response = requests.get(xml_url)
#     xml_data = response.content
#
#     # Parse XML data
#     data = xmltodict.parse(xml_data)
#
#     # Render the template with the data
#     return render_template('index.html', data=data['data']['rims'])
#
# if __name__ == '__main__':
#     # Check if the templates directory exists
#     templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
#     if not os.path.exists(templates_dir):
#         os.makedirs(templates_dir)
#
#     # Run the app
#     app.run(debug=True)

from flask import Flask, render_template
import requests
import xmltodict

app = Flask(__name__)

# Определите URL для загрузки XML-данных
xml_url = 'https://b2b.4tochki.ru/export_data/M28244.xml'

# Определите маршрут для отображения XML-данных
@app.route('/')
def index():
    # Загрузите XML-данные из URL
    response = requests.get(xml_url)
    xml_data = response.content

    # Парсите XML-данные
    data = xmltodict.parse(xml_data)

    # Передайте данные в шаблон
    return render_template('index.html', data=data['data']['rims'])

if __name__ == '__main__':
    app.run(debug=True)