from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import openpyxl

# options = Options()

# количество страниц поиска
pages = 1

print(f"Pages: введите два требуемых класса для поиска потента")
pat1 = input("1-Класс: ")
pat2 = input("2-Класс: ")

count = int(input("Введите желаемое количество патентов: "))

url = f'https://patents.google.com/?q=({pat1});({pat2})&oq=({pat1});({pat2})&page='
driver = webdriver.Chrome()

# DataFrame
try:
    df = pd.read_excel('All_patent_all.xlsx', sheet_name='sheet1')
except FileNotFoundError:
    df = pd.DataFrame(columns=['patent_numbers'])

while len(df) < count:
    # Скачиваем по 1 странице за раз
    for page in range(pages, pages + 1):
        driver.get(url + str(page) + '/')
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        items_first_line = [x.text.replace('\n', ' ').split('   ') for x in soup.find_all('h4', attrs = {'class': "metadata style-scope search-result-item"})]

        patent_numbers = [x[1] for x in items_first_line]

        new_df = pd.DataFrame({'patent_numbers': patent_numbers})
        df = pd.concat([df, new_df], ignore_index=True)

        # Проверка на пустой список patent_numbers
        if patent_numbers:
            print(f"patent: {patent_numbers[0]}")

        df.to_excel('All_patent_all.xlsx', sheet_name='sheet1', index=False)

        # Проверка, найдены ли новые патенты
        if len(new_df) == 0:
            print("Больше патентов на этой странице не найдено.")
            break  # Прекращаем цикл по страницам, если новых патентов нет

    pages += 1  # Увеличиваем `pages` на 1, т.к. скачивали по 1 странице

driver.close()