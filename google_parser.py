# ипорт библиотек

from selenium import webdriver
from selenium.webdriver.common.by import By

import time
import requests
import os


# Функция создания корневого каталога и подкаталогов для каждого запроса, а также скачивания картинок по ссылкам
def create_folder(path, keyword, url_data):
    folder = keyword.lower().replace(" ", "_")
    folder_path = os.path.join(path, folder)
    os.makedirs(folder_path, exist_ok=True)  # предотвращает ошибку, если каталог уже был создан
    print(f"Folder '{folder}' created at {folder_path}")

    image_count = list(range(0, quantity))

    for (i, f) in zip(url_data, image_count):
        download_images(i, f, folder, path)

    print(f"Successfully saved images of {keyword}")

def search_google(search_query,quantity,path):
    # Стандартизируем запрос

    converted_name = search_query.lower().replace(" ", "_")

    search_url = f"https://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q={search_query}"

    url_data = []

    browser = webdriver.Chrome()

    # Открыть браузер для начала поиска
    browser.get(search_url)

    # Расширить окно
    browser.maximize_window()

    time.sleep(1)

    count = 0

    for i in range(0, quantity):

        count += 1

        link = ""

        # нажать на картинку

        img_box = browser.find_elements(By.CSS_SELECTOR, 'div.eA0Zlc')[i]

        try:
            img_box.click()

            time.sleep(1)

            # получить ссылку

            img_box_2 = browser.find_elements(By.CSS_SELECTOR, 'div.v6bUne')[1]

            link = img_box_2.find_elements(By.TAG_NAME, 'img')[0].get_attribute('src')

        except:

            # если клик был прерван

            try:

                browser.execute_script("window.scrollBy(0, 100);")

                time.sleep(2)

                img_box.click()

                time.sleep(1)

                # получить ссылку

                img_box_2 = browser.find_elements(By.CSS_SELECTOR, 'div.v6bUne')[1]

                link = img_box_2.find_elements(By.TAG_NAME, 'img')[0].get_attribute('src')

            except:

                pass

        # добавить ссылку в список

        print(f"Link: {link}")

        url_data.append(link)

        if count % 5 == 0:
            print(f"Downloaded {count} images of {search_query}")

    # скачать картинки и создать для них каталоги

    create_folder(path,search_query,url_data)

    browser.close()

def download_images(url,count,query,path):
    try:

        img_data = requests.get(url).content
        with open(f'{path}{query}/{query}_{count}.jpg', 'wb') as handler:
            handler.write(img_data)

    except Exception as e:

        pass


quantity = 100  #Количество картинок по каждому запросу
keywords = ["plot linear ecuation graph", "plot logarithmic graph"]  #Запросы
path = 'google_images/'  #Путь к паке сохранения

for keyword in keywords:
     print(f"Downloading Images of {keyword}")
     search_google(keyword,quantity,path)

