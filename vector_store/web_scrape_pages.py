from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time


def extract_all_links(number_of_pages: int = 5) -> list[str]:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get('https://www.nasa.gov/news/all-news/')

    all_articles = []

    for page in range(1, number_of_pages + 1):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'hds-content-item'))
            )
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            articles = soup.find_all('div', class_='hds-content-item')

            for article in articles:
                title = article.get_text(strip=True)
                link = article.find('a')['href']
                full_link = link
                all_articles.append({'title': title, 'link': full_link})
                print(f"Title: {title}\nLink: {full_link}\n")

            next_button = driver.find_element(By.XPATH, f'//a[@aria-label="Goto Page {page + 1}"]')
            next_button.click()

            time.sleep(2)

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    driver.quit()

    print(f"Total articles collected: {len(all_articles)}")
    return all_articles