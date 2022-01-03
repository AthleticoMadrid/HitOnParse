import requests
from bs4 import BeautifulSoup
import time
from random import randrange
import json


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

# функция для сбора всех ссылок на все статьи на сайте:
def get_articles_urls(url):
    s = requests.Session()          #создание сессии
    response = s.get(url=url, headers=headers)          #отправляем запрос на главную страницу

    # находим <span class="navigations"> в котором лежат все страницы и забираем последнюю:
    soup = BeautifulSoup(response.text, 'lxml')
    pagination_count = int(soup.find('span', class_='navigations').find_all('a')[-1].text)
    
    articles_urls_list = []
    #в цикле пройдёмся по всем страницам:
    for page in range(1, pagination_count + 1):
        response = s.get(url=f'https://hi-tech.news/page/{page}/', headers=headers)         #отправляем запрос на каждую страницу
        soup = BeautifulSoup(response.text, 'lxml')

        articles_urls = soup.find_all('a', class_='post-title-a')                   #достаём по классу все ссылки
        for au in articles_urls:
            art_url = au.get('href')                                    #достаём ссылки по отдельности
            articles_urls_list.append(art_url)                          #закинем ссылки в список

        time.sleep(randrange(2, 5))                                     #рандомная пауза между запросами
        print(f'Обработал {page}/{pagination_count}')

    #сохранение ссылок в файл:
    with open('articles_urls.txt', 'w', encoding='utf-8') as file:
        for url in articles_urls_list:
            file.write(f'{url}\n')                                  #для удобства каждую ссылку запишем с новой строки

    return 'Работа по сбору ссылок выполнена!'


# функция по сбору данных с ссылок:
def get_data(file_path):
    with open(file_path) as file:
        urls_list = [line.strip() for line in file.readlines()]             #кладём все ссылки в список

    urls_count = len(urls_list)                     #получим общее количество ссылок

    #создадим объект сессии и список под данные и пройдёмся по списку с ссылками:
    s = requests.Session()
    result_data = []
    for url in enumerate(urls_list[:100]):                  #100 статей
        response = s.get(url=url[1], headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        #получим заголовок статьи (и обрежем пробелы strip-ом):
        article_title = soup.find('div', class_='post-content').find('h1', class_='title').text.strip()
        #дата публикации статьи:
        article_date = soup.find('div', class_='post').find('div', class_='tile-views').text.strip()
        #ссылка на главное изображение статьи:
        article_img = f"https://hi-tech.news{soup.find('div', class_='post-media-full').find('img').get('src')}"
        #текст статьи:
        article_text = soup.find('div', class_='the-excerpt').text.strip().replace('\n', '')
        #добавляем в список словарь:
        result_data.append(
            {
                'original_url': url[1],
                'article_title': article_title,
                'article_date': article_date,
                'article_img': article_img,
                'article_text': article_text
            }
        )
        print(f'Обработал {url[0] + 1}/{urls_count}')

    #сохранение в JSON-файл:
    with open('result.json', 'w', encoding='utf-8') as file:
        json.dump(result_data, file, indent=4, ensure_ascii=False)

def main():
    get_data('articles_urls.txt')
    #print(get_articles_urls(url='https://hi-tech.news/'))


if __name__ == '__main__':
    main()