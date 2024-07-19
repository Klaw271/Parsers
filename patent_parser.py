import os
import pyautogui
import time

time.sleep(3)  # Wait for the image to load
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import urllib.request
import pandas as pd
import os
import subprocess
import sys
#import pkg_resources
from selenium.common.exceptions import TimeoutException


def download_image(url, filename, max_retries=3):
    attempt = 0
    while attempt < max_retries:
        try:
            urllib.request.urlretrieve(url, filename)
            print(f"Image saved: {filename}")
            return
        except urllib.error.URLError as e:
            print(f"URL error occurred when trying to retrieve {url}: {e}")
            attempt += 1
            time.sleep(2)  # Wait 2 seconds before retrying
        except Exception as e:
            print(f"An error occurred when trying to retrieve {url}: {e}")
            attempt += 1
            time.sleep(2)
    print(f"Failed to download image after {max_retries} attempts.")

chromedriver_path = "chromedriver.exe"
url = "https://patents.google.com/patent/"
browser = webdriver.Chrome()
browser.get(url)
df = pd.read_excel("All_patent_all.xlsx")
patent_numbers = df['patent_numbers'].tolist()

print(f'Patents: {patent_numbers}')

main_directory = "Patent_images"
if not os.path.exists(main_directory):
    os.makedirs(main_directory)

patents_with_no_images = []

# Проверка на уже скаченные патенты
patents_already_downloaded = []
for patent in patent_numbers:
    current_patent_directory = os.path.join(main_directory, patent)
    if os.path.exists(current_patent_directory):
        patents_already_downloaded.append(patent)

print(f'Already downloaded patents: {patents_already_downloaded}')

for patent in patent_numbers:
    # Пропускаем уже скаченные патенты
    if patent in patents_already_downloaded:
        print(f"Patent {patent} already downloaded, skipping.")
        continue

    print(patent)
    browser.get(url + str(patent) + '/')
    browser.maximize_window()
    search_box = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "searchInput")))
    search_box.clear()
    search_box.send_keys(patent)
    search_button = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "searchButton")))
    search_button.click()

    # Создаем папку для патента независимо от наличия изображений
    current_patent_directory = os.path.join(main_directory, patent)
    if not os.path.exists(current_patent_directory):
        os.makedirs(current_patent_directory)

    # Wait for the image carousel to be present
    try:
        image_carousel = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.ID, 'figures')))
        images = image_carousel.find_elements(By.TAG_NAME, 'img')
        flag = 0
    except TimeoutException:
        try:
            images = WebDriverWait(browser, 100).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img[alt^="Figure"]')))
            flag = 1
        except TimeoutException:
            # No images found after all attempts
            print(f"No images found for patent {patent}.")
            patents_with_no_images.append(patent)
            continue

    print(f"Total images found for patent {patent}: {len(images)}")

    for index, img in enumerate(images, start=1):
        print(index)
        if flag == 1:
            image_src = img.get_attribute('src')
            image_filename = os.path.join(current_patent_directory, f"{patent}_image_{index}.png")
            download_image(image_src, image_filename)
            print(f"Image saved: {image_filename}")
        else:
            test_image_carousel = WebDriverWait(browser, 10000).until(
                EC.presence_of_element_located((By.ID, 'figures')))
            test_images = test_image_carousel.find_elements(By.TAG_NAME, 'img')
            # Click on the image to open it in a new tab
            click = WebDriverWait(browser, 10000).until(EC.element_to_be_clickable(test_images[index - 1]))
            click.click()
            # Wait for the open icon button to be clickable
            open_icon_button = WebDriverWait(browser, 10000).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "paper-icon-button[icon='open-in-new']")))
            open_icon_button.click()

            # Switch to the new tab with the opened image
            WebDriverWait(browser, 1000).until(EC.new_window_is_opened)
            windows = browser.window_handles
            browser.switch_to.window(windows[-1])
            WebDriverWait(browser, 1000).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            # Save the image URL directly without waiting for a specific element indicating that the image has loaded
            image_url = browser.current_url
            image_filename = os.path.join(current_patent_directory, f"{patent}_image_{index}.png")
            download_image(image_url, image_filename)
            print(f"Image saved: {image_filename}")

            # Close the new tab and switch back to the main tab with the carousel
            browser.close()
            browser.switch_to.window(windows[0])

# Close the browser after the loop ends
browser.quit()
if patents_with_no_images:
    print("Patents with no images found:", patents_with_no_images)