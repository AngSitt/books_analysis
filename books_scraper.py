import requests
from bs4 import BeautifulSoup
import csv
import time

URL = 'https://magazin.belkniga.by/catalog/biznes-literatura/'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 YaBrowser/20.9.0.928 Yowser/2.5 Safari/537.36',
           'accept': '*/*'}
FILE = 'books.csv'
HOST = 'https://magazin.belkniga.by'

def get_html(url, params=None):
    req = requests.get(url, headers=HEADERS, params=params)
    return req

def get_pages(html):
    soup = BeautifulSoup(html, 'html.parser')
    last_page = str(soup.find('a', class_='pagging__arrow right fa fa-angle-right').get('href'))
    pagination = int(last_page[-2:])
    return pagination

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='catalog-products-column')
    books = []
    for item in items:
        book_author = item.find('div', class_='productitem__author')
        if book_author:
            book_author = book_author.get_text(strip=True)
        else:
            book_author = None
        books.append({
            'title': item.find('a', class_='productitem__title').get('title'),
            'author': book_author,
            'price': item.find('div', class_='productitem__price').get_text(strip=True).replace('руб.', ''),
            'link': HOST + item.find('a', class_='productitem__title').get('href')
        })
    return books

def save_file(items, path):
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Автор', 'Цена в бел.руб.', 'Ссылка'])
        for item in items:
            writer.writerow([item['title'], item['author'], item['price'], item['link']])
        print('Data is successfully written.')

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        books = []
        pages_count = get_pages(html.text)
        for page in range(1, pages_count + 1):
            print(f'Scraping of the {page}/{pages_count} web-page...')
            html = get_html(URL, params={'PAGEN_1': page})
            books.extend(get_content(html.text))
            time.sleep(3)
        save_file(books, FILE)
        print(f'There are {len(books)} items of books.')
    else:
        print('Error!')

parse()